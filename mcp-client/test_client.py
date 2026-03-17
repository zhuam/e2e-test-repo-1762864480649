#!/usr/bin/env python3
"""
MCP Client 单元测试
"""

import asyncio
import json
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# 导入被测试的模块
from client import MCPClient, StdioMCPClient, HTTPMCPClient


class TestMCPClientBase(unittest.TestCase):
    """MCPClient 基类测试"""

    def test_init(self):
        """测试初始化"""
        client = MCPClient()
        self.assertFalse(client.initialized)
        self.assertIsNone(client.server_info)
        self.assertEqual(client.tools, [])
        self.assertEqual(client.request_id, 0)

    def test_get_next_id(self):
        """测试请求 ID 生成"""
        client = MCPClient()
        self.assertEqual(client._get_next_id(), 1)
        self.assertEqual(client._get_next_id(), 2)
        self.assertEqual(client._get_next_id(), 3)

    def test_send_request_not_implemented(self):
        """测试 send_request 方法未实现"""
        client = MCPClient()
        with self.assertRaises(NotImplementedError):
            asyncio.run(client.send_request("test", {}))


class TestStdioMCPClient(unittest.IsolatedAsyncioTestCase):
    """StdioMCPClient 测试"""

    async def test_init(self):
        """测试初始化"""
        client = StdioMCPClient(command=["echo", "test"])
        self.assertEqual(client.command, ["echo", "test"])
        self.assertIsNone(client.cwd)
        self.assertIsNone(client.process)

    async def test_init_with_cwd(self):
        """测试带工作目录的初始化"""
        client = StdioMCPClient(command=["echo", "test"], cwd="/tmp")
        self.assertEqual(client.cwd, "/tmp")

    async def test_initialize(self):
        """测试初始化连接"""
        client = StdioMCPClient(command=["echo", "test"])
        
        # Mock send_request
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "server": {"name": "test-server", "version": "1.0.0"},
                "tools": [{"name": "test_tool", "description": "A test tool"}]
            }
        }
        client.send_request = AsyncMock(return_value=mock_response)
        
        result = await client.initialize()
        
        self.assertTrue(client.initialized)
        self.assertEqual(client.server_info["name"], "test-server")
        self.assertEqual(len(client.tools), 1)
        self.assertEqual(result, mock_response)

    async def test_list_tools(self):
        """测试获取工具列表"""
        client = StdioMCPClient(command=["echo", "test"])
        
        mock_response = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "tools": [
                    {"name": "add", "description": "Add two numbers"},
                    {"name": "subtract", "description": "Subtract two numbers"}
                ]
            }
        }
        client.send_request = AsyncMock(return_value=mock_response)
        
        tools = await client.list_tools()
        
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0]["name"], "add")
        self.assertEqual(client.tools, tools)

    async def test_call_tool(self):
        """测试调用工具"""
        client = StdioMCPClient(command=["echo", "test"])
        
        mock_response = {
            "jsonrpc": "2.0",
            "id": 3,
            "result": {
                "content": [
                    {"type": "text", "text": json.dumps({"success": True, "result": 30})}
                ]
            }
        }
        client.send_request = AsyncMock(return_value=mock_response)
        
        result = await client.call_tool("add", {"a": 10, "b": 20})
        
        self.assertEqual(result, mock_response)

    async def test_ping(self):
        """测试心跳检测"""
        client = StdioMCPClient(command=["echo", "test"])
        
        mock_response = {
            "jsonrpc": "2.0",
            "id": 4,
            "result": {}
        }
        client.send_request = AsyncMock(return_value=mock_response)
        
        result = await client.ping()
        
        self.assertEqual(result, mock_response)

    async def test_send_request_not_connected(self):
        """测试未连接时发送请求"""
        client = StdioMCPClient(command=["echo", "test"])
        
        with self.assertRaises(RuntimeError) as context:
            await client.send_request("test", {})
        
        self.assertIn("Not connected", str(context.exception))

    async def test_send_request_with_mock_process(self):
        """测试发送请求（使用 mock 进程）"""
        client = StdioMCPClient(command=["echo", "test"])
        
        # 创建 mock 进程
        mock_process = MagicMock()
        mock_stdout = AsyncMock()
        mock_stdout.readline = AsyncMock(return_value=b'{"jsonrpc": "2.0", "id": 1, "result": {}}\n')
        mock_process.stdout = mock_stdout
        mock_process.stdin = AsyncMock()
        
        client.process = mock_process
        
        result = await client.send_request("initialize", {})
        
        self.assertEqual(result["jsonrpc"], "2.0")
        self.assertEqual(result["result"], {})
        mock_process.stdin.write.assert_called_once()

    async def test_close_with_mock_process(self):
        """测试关闭连接"""
        client = StdioMCPClient(command=["echo", "test"])
        
        # 创建 mock 进程
        mock_process = AsyncMock()
        mock_process.terminate = MagicMock()
        mock_process.wait = AsyncMock()
        
        client.process = mock_process
        
        await client.close()
        
        mock_process.terminate.assert_called_once()
        self.assertIsNone(client.process)


class TestHTTPMCPClient(unittest.IsolatedAsyncioTestCase):
    """HTTPMCPClient 测试"""

    async def test_init(self):
        """测试初始化"""
        client = HTTPMCPClient("http://localhost:3000")
        self.assertEqual(client.base_url, "http://localhost:3000")
        self.assertIsNone(client._session)
        self.assertTrue(client._owns_session)

    async def test_init_with_session(self):
        """测试带现有 session 的初始化"""
        mock_session = MagicMock()
        client = HTTPMCPClient("http://localhost:3000", session=mock_session)
        self.assertFalse(client._owns_session)

    async def test_base_url_normalization(self):
        """测试 base_url 标准化"""
        client1 = HTTPMCPClient("http://localhost:3000/")
        client2 = HTTPMCPClient("http://localhost:3000")
        self.assertEqual(client1.base_url, client2.base_url)

    async def test_initialize(self):
        """测试初始化连接"""
        client = HTTPMCPClient("http://localhost:3000")
        
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "server": {"name": "test-server", "version": "1.0.0"},
                "tools": [{"name": "test_tool", "description": "A test tool"}]
            }
        }
        client.send_request = AsyncMock(return_value=mock_response)
        
        result = await client.initialize()
        
        self.assertTrue(client.initialized)
        self.assertEqual(client.server_info["name"], "test-server")

    async def test_list_tools(self):
        """测试获取工具列表"""
        client = HTTPMCPClient("http://localhost:3000")
        
        mock_response = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "tools": [
                    {"name": "add", "description": "Add two numbers"}
                ]
            }
        }
        client.send_request = AsyncMock(return_value=mock_response)
        
        tools = await client.list_tools()
        
        self.assertEqual(len(tools), 1)

    async def test_call_tool(self):
        """测试调用工具"""
        client = HTTPMCPClient("http://localhost:3000")
        
        mock_response = {
            "jsonrpc": "2.0",
            "id": 3,
            "result": {
                "content": [{"type": "text", "text": '{"success": true}'}]
            }
        }
        client.send_request = AsyncMock(return_value=mock_response)
        
        result = await client.call_tool("add", {"a": 10, "b": 20})
        
        self.assertEqual(result, mock_response)

    async def test_ping(self):
        """测试心跳检测"""
        client = HTTPMCPClient("http://localhost:3000")
        
        mock_response = {"jsonrpc": "2.0", "id": 4, "result": {}}
        client.send_request = AsyncMock(return_value=mock_response)
        
        result = await client.ping()
        
        self.assertEqual(result, mock_response)

    async def test_send_request_not_connected(self):
        """测试未连接时发送请求"""
        client = HTTPMCPClient("http://localhost:3000")
        
        with self.assertRaises(RuntimeError) as context:
            await client.send_request("test", {})
        
        self.assertIn("Not connected", str(context.exception))

    async def test_send_request_with_mock_session(self):
        """测试发送请求（使用 mock session）"""
        client = HTTPMCPClient("http://localhost:3000")
        
        # 创建 mock session 和 response
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"jsonrpc": "2.0", "id": 1, "result": {}})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_response)
        
        client._session = mock_session
        
        result = await client.send_request("initialize", {})
        
        self.assertEqual(result["jsonrpc"], "2.0")
        mock_session.post.assert_called_once()

    async def test_close(self):
        """测试关闭连接"""
        client = HTTPMCPClient("http://localhost:3000")
        
        # 创建 mock session
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()
        
        client._session = mock_session
        
        await client.close()
        
        mock_session.close.assert_called_once()
        self.assertIsNone(client._session)

    async def test_close_without_owns_session(self):
        """测试关闭连接（不拥有 session）"""
        mock_session = AsyncMock()
        client = HTTPMCPClient("http://localhost:3000", session=mock_session)
        
        await client.close()
        
        # 不应该关闭不拥有的 session
        mock_session.close.assert_not_called()


class TestIntegration(unittest.IsolatedAsyncioTestCase):
    """集成测试"""

    async def test_stdio_workflow(self):
        """测试 stdio 完整工作流程"""
        client = StdioMCPClient(command=["echo", "test"])
        
        # Mock 所有方法
        client.connect = AsyncMock()
        client.send_request = AsyncMock(side_effect=[
            {"jsonrpc": "2.0", "id": 1, "result": {"server": {"name": "test"}, "tools": []}},
            {"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "add"}]}},
            {"jsonrpc": "2.0", "id": 3, "result": {"content": [{"text": "30"}]}},
            {"jsonrpc": "2.0", "id": 4, "result": {}}
        ])
        client.close = AsyncMock()
        
        # 模拟工作流程
        await client.connect()
        await client.initialize()
        self.assertTrue(client.initialized)
        
        tools = await client.list_tools()
        self.assertEqual(len(tools), 1)
        
        result = await client.call_tool("add", {"a": 10, "b": 20})
        self.assertIn("result", result)
        
        await client.ping()
        await client.close()

    async def test_http_workflow(self):
        """测试 HTTP 完整工作流程"""
        client = HTTPMCPClient("http://localhost:3000")
        
        # Mock 所有方法
        client.connect = AsyncMock()
        client.send_request = AsyncMock(side_effect=[
            {"jsonrpc": "2.0", "id": 1, "result": {"server": {"name": "test"}, "tools": []}},
            {"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "add"}]}},
            {"jsonrpc": "2.0", "id": 3, "result": {"content": [{"text": "30"}]}},
            {"jsonrpc": "2.0", "id": 4, "result": {}}
        ])
        client.close = AsyncMock()
        
        # 模拟工作流程
        await client.connect()
        await client.initialize()
        self.assertTrue(client.initialized)
        
        tools = await client.list_tools()
        self.assertEqual(len(tools), 1)
        
        result = await client.call_tool("add", {"a": 10, "b": 20})
        self.assertIn("result", result)
        
        await client.ping()
        await client.close()


def run_integration_with_real_server():
    """与真实服务器进行集成测试（手动运行）"""
    import subprocess
    import time

    print("=" * 60)
    print("真实服务器集成测试")
    print("=" * 60)

    # 启动 stdio 服务器
    print("\n1. 测试 stdio 模式...")
    process = subprocess.Popen(
        ["python", "mcp-server/server.py", "--transport", "stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 发送测试请求
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 10, "b": 20}}},
        {"jsonrpc": "2.0", "id": 4, "method": "ping"}
    ]

    for req in requests:
        process.stdin.write(json.dumps(req) + "\n")
        process.stdin.flush()
        response = process.stdout.readline()
        print(f"   请求：{req['method']}")
        print(f"   响应：{response.strip()[:100]}...")

    process.terminate()
    process.wait()
    print("   stdio 测试完成!")

    print("\n所有测试完成!")


if __name__ == "__main__":
    # 运行单元测试
    unittest.main(verbosity=2)
