#!/usr/bin/env python3
"""
MCP Client 实现
支持 stdio 和 http 两种协议方式
"""

import argparse
import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPClient:
    """MCP Client 基类"""

    def __init__(self):
        self.initialized = False
        self.server_info: Optional[Dict[str, Any]] = None
        self.tools: List[Dict[str, Any]] = []
        self.request_id = 0

    def _get_next_id(self) -> int:
        """获取下一个请求 ID"""
        self.request_id += 1
        return self.request_id

    async def initialize(self) -> Dict[str, Any]:
        """初始化连接"""
        response = await self.send_request("initialize", {})
        if "result" in response:
            self.initialized = True
            self.server_info = response["result"].get("server", {})
            self.tools = response["result"].get("tools", [])
            logger.info(f"MCP Client initialized: {self.server_info}")
        return response

    async def list_tools(self) -> List[Dict[str, Any]]:
        """获取工具列表"""
        response = await self.send_request("tools/list", {})
        if "result" in response:
            self.tools = response["result"].get("tools", [])
            logger.info(f"Available tools: {len(self.tools)}")
        return self.tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        response = await self.send_request("tools/call", params)
        return response

    async def ping(self) -> Dict[str, Any]:
        """心跳检测"""
        return await self.send_request("ping", {})

    async def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求（子类实现）"""
        raise NotImplementedError


class StdioMCPClient(MCPClient):
    """基于 stdio 的 MCP Client"""

    def __init__(self, command: List[str], cwd: Optional[str] = None):
        super().__init__()
        self.command = command
        self.cwd = cwd
        self.process: Optional[asyncio.subprocess.Process] = None

    async def connect(self) -> None:
        """连接到 MCP 服务器"""
        logger.info(f"Starting MCP server: {' '.join(self.command)}")
        
        # 使用 asyncio 创建子进程
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd
        )
        
        logger.info(f"MCP server started with PID: {self.process.pid}")

    async def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送 JSON-RPC 请求"""
        if self.process is None:
            raise RuntimeError("Not connected. Call connect() first.")

        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params
        }

        request_json = json.dumps(request) + "\n"
        logger.debug(f"Sending request: {request_json.strip()}")

        # 写入请求
        self.process.stdin.write(request_json.encode('utf-8'))
        await self.process.stdin.drain()

        # 读取响应
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("Server closed the connection")

        response_json = response_line.decode('utf-8').strip()
        logger.debug(f"Received response: {response_json}")

        try:
            response = json.loads(response_json)
            return response
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response: {response_json}")
            raise

    async def close(self) -> None:
        """关闭连接"""
        if self.process:
            logger.info("Closing MCP server connection")
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Server did not terminate gracefully, killing...")
                self.process.kill()
                await self.process.wait()
            except ProcessLookupError:
                # 进程已经不存在了
                logger.info("Process already terminated")
            finally:
                self.process = None


class HTTPMCPClient(MCPClient):
    """基于 HTTP 的 MCP Client"""

    def __init__(self, base_url: str, session: Optional[aiohttp.ClientSession] = None):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self._session: Optional[aiohttp.ClientSession] = session
        self._owns_session = session is None  # 是否拥有 session 的生命周期

    async def connect(self) -> None:
        """连接到 MCP 服务器"""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        logger.info(f"Connecting to MCP server at {self.base_url}")

    async def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送 HTTP POST 请求"""
        if self._session is None:
            raise RuntimeError("Not connected. Call connect() first.")

        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params
        }

        url = urljoin(self.base_url, '/message')
        logger.debug(f"Sending request to {url}: {json.dumps(request)}")

        try:
            async with self._session.post(
                url,
                json=request,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                logger.debug(f"Received response: {response_data}")
                return response_data
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise

    async def get_tools_direct(self) -> List[Dict[str, Any]]:
        """直接获取工具列表（如果服务器支持 /tools 端点）"""
        if self._session is None:
            raise RuntimeError("Not connected. Call connect() first.")

        url = urljoin(self.base_url, '/tools')
        try:
            async with self._session.get(url) as response:
                self.tools = await response.json()
                return self.tools
        except aiohttp.ClientError:
            # 如果 /tools 端点不存在，使用标准 MCP 协议
            return await self.list_tools()

    async def close(self) -> None:
        """关闭连接"""
        if self._session and self._owns_session:
            logger.info("Closing HTTP session")
            await self._session.close()
            self._session = None


async def demo_stdio():
    """stdio 模式演示"""
    print("=" * 60)
    print("MCP Client - stdio 模式演示")
    print("=" * 60)

    # 启动本地 MCP server
    client = StdioMCPClient(
        command=["python", "mcp-server/server.py", "--transport", "stdio"]
    )

    try:
        await client.connect()
        print("\n1. 初始化连接...")
        result = await client.initialize()
        print(f"   服务器信息：{result.get('result', {}).get('server', {})}")

        print("\n2. 获取工具列表...")
        tools = await client.list_tools()
        print(f"   可用工具：{[t['name'] for t in tools]}")

        print("\n3. 调用加法工具 (10 + 20)...")
        result = await client.call_tool("add", {"a": 10, "b": 20})
        print(f"   结果：{result}")

        print("\n4. 调用时间工具...")
        result = await client.call_tool("get_time", {})
        print(f"   当前时间：{result}")

        print("\n5. 调用文本反转工具...")
        result = await client.call_tool("reverse_text", {"text": "Hello MCP!"})
        print(f"   反转结果：{result}")

        print("\n6. 心跳检测...")
        result = await client.ping()
        print(f"   Ping 结果：{result}")

    except Exception as e:
        print(f"错误：{e}")
    finally:
        await client.close()


async def demo_http(base_url: str = "http://127.0.0.1:3000"):
    """HTTP 模式演示"""
    print("=" * 60)
    print(f"MCP Client - HTTP 模式演示 (服务器：{base_url})")
    print("=" * 60)

    client = HTTPMCPClient(base_url)

    try:
        await client.connect()

        print("\n1. 初始化连接...")
        result = await client.initialize()
        print(f"   服务器信息：{result.get('result', {}).get('server', {})}")

        print("\n2. 获取工具列表...")
        tools = await client.list_tools()
        print(f"   可用工具：{[t['name'] for t in tools]}")

        print("\n3. 调用加法工具 (10 + 20)...")
        result = await client.call_tool("add", {"a": 10, "b": 20})
        print(f"   结果：{result}")

        print("\n4. 调用时间工具...")
        result = await client.call_tool("get_time", {})
        print(f"   当前时间：{result}")

        print("\n5. 调用文本反转工具...")
        result = await client.call_tool("reverse_text", {"text": "Hello MCP!"})
        print(f"   反转结果：{result}")

        print("\n6. 心跳检测...")
        result = await client.ping()
        print(f"   Ping 结果：{result}")

    except aiohttp.ClientError as e:
        print(f"连接错误：{e}")
        print("提示：请确保 HTTP 服务器正在运行")
    except Exception as e:
        print(f"错误：{e}")
    finally:
        await client.close()


async def interactive_mode_stdio():
    """stdio 交互模式"""
    client = StdioMCPClient(
        command=["python", "mcp-server/server.py", "--transport", "stdio"]
    )

    await client.connect()
    await client.initialize()

    print("MCP Client 交互模式 (输入 'quit' 退出)")
    print("可用命令：list, call <tool> <json_args>, ping, help")

    while True:
        try:
            cmd = input("\nmcp> ").strip()
            if not cmd:
                continue

            if cmd == "quit":
                break
            elif cmd == "help":
                print("命令列表:")
                print("  list                     - 列出所有工具")
                print("  call <tool> <json_args>  - 调用工具，如：call add {\"a\": 1, \"b\": 2}")
                print("  ping                     - 心跳检测")
                print("  quit                     - 退出")
            elif cmd == "list":
                tools = await client.list_tools()
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
            elif cmd == "ping":
                result = await client.ping()
                print(f"Ping: {result}")
            elif cmd.startswith("call "):
                parts = cmd[5:].split(maxsplit=1)
                if len(parts) != 2:
                    print("用法：call <tool> <json_args>")
                    continue
                tool_name, args_str = parts
                try:
                    args = json.loads(args_str)
                    result = await client.call_tool(tool_name, args)
                    print(f"结果：{result}")
                except json.JSONDecodeError:
                    print("JSON 参数格式错误")
            else:
                print(f"未知命令：{cmd}")
        except EOFError:
            break
        except Exception as e:
            print(f"错误：{e}")

    await client.close()


async def interactive_mode_http(base_url: str):
    """HTTP 交互模式"""
    client = HTTPMCPClient(base_url)

    try:
        await client.connect()
        await client.initialize()

        print(f"MCP Client 交互模式 (服务器：{base_url})")
        print("输入 'quit' 退出")

        while True:
            try:
                cmd = input("\nmcp> ").strip()
                if not cmd:
                    continue

                if cmd == "quit":
                    break
                elif cmd == "list":
                    tools = await client.list_tools()
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description']}")
                elif cmd == "ping":
                    result = await client.ping()
                    print(f"Ping: {result}")
                elif cmd.startswith("call "):
                    parts = cmd[5:].split(maxsplit=1)
                    if len(parts) != 2:
                        print("用法：call <tool> <json_args>")
                        continue
                    tool_name, args_str = parts
                    try:
                        args = json.loads(args_str)
                        result = await client.call_tool(tool_name, args)
                        print(f"结果：{result}")
                    except json.JSONDecodeError:
                        print("JSON 参数格式错误")
                else:
                    print("未知命令，输入 'help' 查看帮助")
            except EOFError:
                break
            except Exception as e:
                print(f"错误：{e}")
    finally:
        await client.close()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MCP Client')
    parser.add_argument('--transport', choices=['stdio', 'http'], default='stdio',
                        help='Transport mode: stdio or http (default: stdio)')
    parser.add_argument('--url', default='http://127.0.0.1:3000',
                        help='URL for HTTP mode (default: http://127.0.0.1:3000)')
    parser.add_argument('--demo', action='store_true',
                        help='Run demo mode')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Run interactive mode')

    args = parser.parse_args()

    if args.demo:
        if args.transport == 'stdio':
            await demo_stdio()
        else:
            await demo_http(args.url)
    elif args.interactive:
        if args.transport == 'stdio':
            await interactive_mode_stdio()
        else:
            await interactive_mode_http(args.url)
    else:
        # 默认运行 demo
        if args.transport == 'stdio':
            await demo_stdio()
        else:
            await demo_http(args.url)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMCP Client stopped")
