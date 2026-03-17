#!/usr/bin/env python3
"""
MCP Server 功能测试
测试 stdio 和 http 两种传输方式
"""

import asyncio
import json
import subprocess
import sys
import time
import unittest
from typing import Any, Dict, Optional

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


class TestStdioServer(unittest.TestCase):
    """测试 stdio 传输方式"""

    def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到 stdio server 并获取响应"""
        process = subprocess.Popen(
            [sys.executable, 'server.py', '--transport', 'stdio'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        request_json = json.dumps(request) + '\n'
        stdout, stderr = process.communicate(input=request_json, timeout=5)
        
        if stderr:
            # 忽略日志输出，只取 JSON 响应
            pass
        
        # 解析响应
        for line in stdout.strip().split('\n'):
            if line.strip():
                try:
                    return json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
        
        raise ValueError(f"No valid JSON response: {stdout}")

    def test_initialize(self):
        """测试 initialize 方法"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize"
        }
        response = self.send_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 1)
        self.assertIn("result", response)
        self.assertIn("server", response["result"])
        self.assertIn("tools", response["result"])

    def test_tools_list(self):
        """测试 tools/list 方法"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        response = self.send_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 2)
        self.assertIn("result", response)
        self.assertIn("tools", response["result"])
        
        tools = response["result"]["tools"]
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)

    def test_add_tool(self):
        """测试 add 工具"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "add",
                "arguments": {"a": 10, "b": 20}
            }
        }
        response = self.send_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 3)
        self.assertIn("result", response)
        
        result = json.loads(response["result"]["content"][0]["text"])
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], 30)

    def test_subtract_tool(self):
        """测试 subtract 工具"""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "subtract",
                "arguments": {"a": 50, "b": 30}
            }
        }
        response = self.send_request(request)
        
        result = json.loads(response["result"]["content"][0]["text"])
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], 20)

    def test_multiply_tool(self):
        """测试 multiply 工具"""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "multiply",
                "arguments": {"a": 6, "b": 7}
            }
        }
        response = self.send_request(request)
        
        result = json.loads(response["result"]["content"][0]["text"])
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], 42)

    def test_divide_tool(self):
        """测试 divide 工具"""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "divide",
                "arguments": {"a": 100, "b": 4}
            }
        }
        response = self.send_request(request)
        
        result = json.loads(response["result"]["content"][0]["text"])
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], 25)

    def test_divide_by_zero(self):
        """测试除以零的错误处理"""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "divide",
                "arguments": {"a": 10, "b": 0}
            }
        }
        response = self.send_request(request)
        
        result = json.loads(response["result"]["content"][0]["text"])
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_get_time_tool(self):
        """测试 get_time 工具"""
        request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "get_time",
                "arguments": {}
            }
        }
        response = self.send_request(request)
        
        result = json.loads(response["result"]["content"][0]["text"])
        self.assertTrue(result["success"])
        self.assertIsInstance(result["result"], str)

    def test_reverse_text_tool(self):
        """测试 reverse_text 工具"""
        request = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "reverse_text",
                "arguments": {"text": "hello"}
            }
        }
        response = self.send_request(request)
        
        result = json.loads(response["result"]["content"][0]["text"])
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "olleh")

    def test_count_chars_tool(self):
        """测试 count_chars 工具"""
        request = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "count_chars",
                "arguments": {"text": "hello world"}
            }
        }
        response = self.send_request(request)
        
        result = json.loads(response["result"]["content"][0]["text"])
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["characters"], 11)
        self.assertEqual(result["result"]["words"], 2)

    def test_ping(self):
        """测试 ping 方法"""
        request = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "ping"
        }
        response = self.send_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 11)
        self.assertIn("result", response)

    def test_unknown_tool(self):
        """测试未知工具的错误处理"""
        request = {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {}
            }
        }
        response = self.send_request(request)
        
        result = json.loads(response["result"]["content"][0]["text"])
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_missing_parameter(self):
        """测试缺少必需参数的错误处理"""
        request = {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/call",
            "params": {
                "name": "add",
                "arguments": {"a": 10}  # 缺少 b
            }
        }
        response = self.send_request(request)
        
        result = json.loads(response["result"]["content"][0]["text"])
        self.assertFalse(result["success"])
        self.assertIn("error", result)


@unittest.skipUnless(AIOHTTP_AVAILABLE, "aiohttp is not installed")
class TestHTTPServer(unittest.TestCase):
    """测试 HTTP 传输方式"""

    @classmethod
    def setUpClass(cls):
        """启动 HTTP 服务器"""
        cls.server_process = subprocess.Popen(
            [sys.executable, 'server.py', '--transport', 'http', '--port', '3001'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # 等待服务器启动
        time.sleep(2)
        cls.base_url = "http://127.0.0.1:3001"

    @classmethod
    def tearDownClass(cls):
        """停止 HTTP 服务器"""
        cls.server_process.terminate()
        cls.server_process.wait()

    async def async_get(self, path: str) -> Dict[str, Any]:
        """发送 GET 请求"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{path}") as response:
                return await response.json()

    async def async_post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送 POST 请求"""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}{path}", json=data) as response:
                return await response.json()

    def test_health(self):
        """测试健康检查"""
        async def run_test():
            response = await self.async_get("/health")
            self.assertEqual(response["status"], "ok")
        
        asyncio.run(run_test())

    def test_root(self):
        """测试根路径"""
        async def run_test():
            response = await self.async_get("/")
            self.assertIn("name", response)
            self.assertIn("endpoints", response)
        
        asyncio.run(run_test())

    def test_tools_list(self):
        """测试获取工具列表"""
        async def run_test():
            response = await self.async_get("/tools")
            self.assertIn("server", response)
            self.assertIn("tools", response)
            self.assertGreater(len(response["tools"]), 0)
        
        asyncio.run(run_test())

    def test_add_tool_simple(self):
        """测试简单格式调用 add 工具"""
        async def run_test():
            response = await self.async_post("/call", {
                "tool": "add",
                "params": {"a": 15, "b": 25}
            })
            self.assertTrue(response["success"])
            self.assertEqual(response["result"], 40)
        
        asyncio.run(run_test())

    def test_add_tool_rpc(self):
        """测试 JSON-RPC 格式调用 add 工具"""
        async def run_test():
            response = await self.async_post("/rpc", {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "add",
                    "arguments": {"a": 100, "b": 200}
                }
            })
            self.assertIn("result", response)
            result = json.loads(response["result"]["content"][0]["text"])
            self.assertTrue(result["success"])
            self.assertEqual(result["result"], 300)
        
        asyncio.run(run_test())

    def test_multiply_tool(self):
        """测试 multiply 工具"""
        async def run_test():
            response = await self.async_post("/call", {
                "tool": "multiply",
                "params": {"a": 8, "b": 9}
            })
            self.assertTrue(response["success"])
            self.assertEqual(response["result"], 72)
        
        asyncio.run(run_test())

    def test_divide_by_zero(self):
        """测试除以零的错误处理"""
        async def run_test():
            response = await self.async_post("/call", {
                "tool": "divide",
                "params": {"a": 10, "b": 0}
            })
            self.assertFalse(response["success"])
            self.assertIn("error", response)
        
        asyncio.run(run_test())

    def test_reverse_text(self):
        """测试 reverse_text 工具"""
        async def run_test():
            response = await self.async_post("/call", {
                "tool": "reverse_text",
                "params": {"text": "MCP Server"}
            })
            self.assertTrue(response["success"])
            self.assertEqual(response["result"], "revreS PCM")
        
        asyncio.run(run_test())

    def test_get_time(self):
        """测试 get_time 工具"""
        async def run_test():
            response = await self.async_post("/call", {
                "tool": "get_time",
                "params": {}
            })
            self.assertTrue(response["success"])
            self.assertIsInstance(response["result"], str)
        
        asyncio.run(run_test())

    def test_unknown_tool(self):
        """测试未知工具"""
        async def run_test():
            response = await self.async_post("/call", {
                "tool": "unknown_tool",
                "params": {}
            })
            self.assertFalse(response["success"])
            self.assertIn("error", response)
        
        asyncio.run(run_test())

    def test_not_found(self):
        """测试 404 错误"""
        async def run_test():
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/nonexistent") as response:
                    self.assertEqual(response.status, 404)
        
        asyncio.run(run_test())


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("MCP Server 功能测试")
    print("=" * 60)
    print()

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加 stdio 测试
    print("添加 stdio 传输方式测试...")
    stdio_tests = loader.loadTestsFromTestCase(TestStdioServer)
    suite.addTests(stdio_tests)

    # 添加 HTTP 测试（如果 aiohttp 可用）
    if AIOHTTP_AVAILABLE:
        print("添加 HTTP 传输方式测试...")
        http_tests = loader.loadTestsFromTestCase(TestHTTPServer)
        suite.addTests(http_tests)
    else:
        print("警告：aiohttp 未安装，跳过 HTTP 测试")

    print()
    print("=" * 60)
    print("开始运行测试...")
    print("=" * 60)
    print()

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 60)
    print(f"测试结果：{result.testsRun} 个测试，{len(result.failures)} 个失败，{len(result.errors)} 个错误")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
