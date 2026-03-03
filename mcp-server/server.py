#!/usr/bin/env python3
"""
最简单的 MCP Server 实现
支持 stdio 和 sse 两种传输方式
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def add(a: float, b: float) -> float:
    """两个数字相加"""
    return a + b


def subtract(a: float, b: float) -> float:
    """两个数字相减"""
    return a - b


def multiply(a: float, b: float) -> float:
    """两个数字相乘"""
    return a * b


def divide(a: float, b: float) -> float:
    """两个数字相除"""
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b


def get_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def reverse_text(text: str) -> str:
    """反转文本"""
    return text[::-1]


def count_chars(text: str) -> Dict[str, Any]:
    """统计文本中的字符数"""
    chars = len(text)
    words = len(text.split()) if text.strip() else 0
    lines = len(text.split('\n')) if text else 0
    return {
        "characters": chars,
        "words": words,
        "lines": lines,
        "text": text
    }


class MCPServer:
    """MCP Server 实现"""

    def __init__(self):
        self.tools = {
            "add": {
                "description": "两个数字相加",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "第一个数字"},
                        "b": {"type": "number", "description": "第二个数字"}
                    },
                    "required": ["a", "b"]
                },
                "function": add
            },
            "subtract": {
                "description": "两个数字相减",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "被减数"},
                        "b": {"type": "number", "description": "减数"}
                    },
                    "required": ["a", "b"]
                },
                "function": subtract
            },
            "multiply": {
                "description": "两个数字相乘",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "第一个数字"},
                        "b": {"type": "number", "description": "第二个数字"}
                    },
                    "required": ["a", "b"]
                },
                "function": multiply
            },
            "divide": {
                "description": "两个数字相除",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "被除数"},
                        "b": {"type": "number", "description": "除数"}
                    },
                    "required": ["a", "b"]
                },
                "function": divide
            },
            "get_time": {
                "description": "获取当前时间",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "function": get_time
            },
            "reverse_text": {
                "description": "反转文本",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "要反转的文本"}
                    },
                    "required": ["text"]
                },
                "function": reverse_text
            },
            "count_chars": {
                "description": "统计文本中的字符数",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "要统计的文本"}
                    },
                    "required": ["text"]
                },
                "function": count_chars
            }
        }
        self.server_info = {
            "name": "simple-mcp-server",
            "version": "1.0.0",
            "description": "最简单的 MCP Server 实现"
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """获取服务器能力"""
        tools_list = []
        for name, tool in self.tools.items():
            tools_list.append({
                "name": name,
                "description": tool["description"],
                "parameters": tool["parameters"]
            })

        return {
            "server": self.server_info,
            "tools": tools_list
        }

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }

        tool = self.tools[tool_name]
        func = tool["function"]

        try:
            # 验证必需参数
            required = tool["parameters"].get("required", [])
            for param in required:
                if param not in params:
                    return {
                        "success": False,
                        "error": f"Missing required parameter: {param}"
                    }

            # 执行函数
            result = func(**params)

            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id", 0)

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": self.get_capabilities()
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": name,
                            "description": tool["description"],
                            "parameters": tool["parameters"]
                        }
                        for name, tool in self.tools.items()
                    ]
                }
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_params = params.get("arguments", {})
            result = self.execute_tool(tool_name, tool_params)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False)
                        }
                    ]
                }
            }
        elif method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {}
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }


class StdioServer:
    """基于 stdio 的 MCP Server"""

    def __init__(self, server: MCPServer):
        self.server = server

    async def run(self):
        """运行 stdio 服务器"""
        logger.info("Starting MCP server in stdio mode")

        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    request = json.loads(line)
                    response = self.server.handle_request(request)
                    print(json.dumps(response, ensure_ascii=False), flush=True)
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response, ensure_ascii=False), flush=True)

            except Exception as e:
                logger.error(f"Error handling request: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response, ensure_ascii=False), flush=True)


class SSEServer:
    """基于 SSE 的 MCP Server"""

    def __init__(self, server: MCPServer, host: str = "127.0.0.1", port: int = 3000):
        self.server = server
        self.host = host
        self.port = port
        self.sessions: Dict[str, asyncio.Queue] = {}

    async def handle_sse(self, request):
        """处理 SSE 连接"""
        import aiohttp
        from aiohttp import web

        session_id = str(id(asyncio.current_task()))
        queue = asyncio.Queue()
        self.sessions[session_id] = queue

        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )
        await response.prepare(request)

        # 发送初始事件
        await response.write(f"event: connected\ndata: {{\"session_id\": \"{session_id}\"}}\n\n".encode())

        try:
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=30)
                    event_data = json.dumps(data)
                    await response.write(f"event: message\ndata: {event_data}\n\n".encode())
                except asyncio.TimeoutError:
                    # 发送 ping 保持连接
                    await response.write(f"event: ping\ndata: {{}}\n\n".encode())
        except Exception as e:
            logger.error(f"SSE connection error: {e}")
        finally:
            del self.sessions[session_id]

        return response

    async def handle_post(self, request):
        """处理 POST 请求"""
        from aiohttp import web

        try:
            data = await request.json()

            # 支持两种格式：标准 MCP 请求或直接请求
            if "jsonrpc" in data:
                response = self.server.handle_request(data)
            else:
                # 简单格式：直接调用工具
                tool_name = data.get("tool")
                params = data.get("params", {})
                result = self.server.execute_tool(tool_name, params)
                response = result

            # 如果有 SSE 连接，广播结果
            for queue in self.sessions.values():
                await queue.put(response)

            return web.json_response(response)
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_get_tools(self, request):
        """获取工具列表"""
        from aiohttp import web
        return web.json_response(self.server.get_capabilities())

    async def run(self):
        """运行 SSE 服务器"""
        from aiohttp import web

        logger.info(f"Starting MCP server in SSE mode on http://{self.host}:{self.port}")

        app = web.Application()
        app.router.add_get('/sse', self.handle_sse)
        app.router.add_post('/message', self.handle_post)
        app.router.add_get('/tools', self.handle_get_tools)
        app.router.add_get('/', lambda r: web.json_response({
            "name": "Simple MCP Server",
            "version": "1.0.0",
            "endpoints": {
                "sse": "/sse",
                "message": "POST /message",
                "tools": "GET /tools"
            }
        }))

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        logger.info(f"MCP Server running at http://{self.host}:{self.port}")
        logger.info(f"  - SSE endpoint: http://{self.host}:{self.port}/sse")
        logger.info(f"  - Message endpoint: http://{self.host}:{self.port}/message")
        logger.info(f"  - Tools endpoint: http://{self.host}:{self.port}/tools")

        # 保持运行
        while True:
            await asyncio.sleep(3600)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Simple MCP Server')
    parser.add_argument('--transport', choices=['stdio', 'sse'], default='stdio',
                        help='Transport mode: stdio or sse (default: stdio)')
    parser.add_argument('--host', default='127.0.0.1', help='Host for SSE mode (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=3000, help='Port for SSE mode (default: 3000)')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')

    args = parser.parse_args()

    server = MCPServer()

    if args.transport == 'stdio':
        stdio_server = StdioServer(server)
        await stdio_server.run()
    elif args.transport == 'sse':
        sse_server = SSEServer(server, host=args.host, port=args.port)
        await sse_server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")
