#!/usr/bin/env python3
"""
MCP Client 集成测试脚本
测试与真实 MCP 服务器的连接
"""

import asyncio
import json
import subprocess
import sys
import time
import aiohttp
from client import StdioMCPClient, HTTPMCPClient


async def test_stdio_integration():
    """测试 stdio 模式与真实服务器"""
    print("=" * 60)
    print("集成测试：stdio 模式")
    print("=" * 60)
    
    client = StdioMCPClient(
        command=["python", "mcp-server/server.py", "--transport", "stdio"]
    )
    
    try:
        # 连接
        await client.connect()
        print("✓ 连接到 stdio 服务器")
        
        # 初始化
        result = await client.initialize()
        assert "result" in result
        assert "server" in result["result"]
        print(f"✓ 初始化成功：{result['result']['server']['name']}")
        
        # 获取工具列表
        tools = await client.list_tools()
        assert len(tools) > 0
        print(f"✓ 获取工具列表成功：{len(tools)} 个工具")
        
        # 测试加法
        result = await client.call_tool("add", {"a": 10, "b": 20})
        response_text = json.loads(result["result"]["content"][0]["text"])
        assert response_text["success"] is True
        assert response_text["result"] == 30
        print(f"✓ 加法测试通过：10 + 20 = {response_text['result']}")
        
        # 测试减法
        result = await client.call_tool("subtract", {"a": 50, "b": 20})
        response_text = json.loads(result["result"]["content"][0]["text"])
        assert response_text["result"] == 30
        print(f"✓ 减法测试通过：50 - 20 = {response_text['result']}")
        
        # 测试乘法
        result = await client.call_tool("multiply", {"a": 5, "b": 6})
        response_text = json.loads(result["result"]["content"][0]["text"])
        assert response_text["result"] == 30
        print(f"✓ 乘法测试通过：5 * 6 = {response_text['result']}")
        
        # 测试除法
        result = await client.call_tool("divide", {"a": 60, "b": 2})
        response_text = json.loads(result["result"]["content"][0]["text"])
        assert response_text["result"] == 30
        print(f"✓ 除法测试通过：60 / 2 = {response_text['result']}")
        
        # 测试获取时间
        result = await client.call_tool("get_time", {})
        response_text = json.loads(result["result"]["content"][0]["text"])
        assert response_text["success"] is True
        print(f"✓ 时间工具测试通过：{response_text['result']}")
        
        # 测试文本反转
        result = await client.call_tool("reverse_text", {"text": "Hello"})
        response_text = json.loads(result["result"]["content"][0]["text"])
        assert response_text["result"] == "olleH"
        print(f"✓ 文本反转测试通过：'Hello' -> '{response_text['result']}'")
        
        # 测试字符统计
        result = await client.call_tool("count_chars", {"text": "Hello World"})
        response_text = json.loads(result["result"]["content"][0]["text"])
        assert response_text["result"]["words"] == 2
        print(f"✓ 字符统计测试通过：{response_text['result']}")
        
        # 心跳检测
        result = await client.ping()
        assert "result" in result
        print("✓ 心跳检测通过")
        
        print("\n✓ stdio 模式所有测试通过!")
        return True
        
    except Exception as e:
        print(f"\n✗ stdio 模式测试失败：{e}")
        return False
    finally:
        await client.close()


async def test_http_integration(base_url="http://127.0.0.1:3000"):
    """测试 HTTP 模式与真实服务器"""
    print("=" * 60)
    print(f"集成测试：HTTP 模式 ({base_url})")
    print("=" * 60)
    
    # 首先检查服务器是否运行
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/tools", timeout=5) as response:
                if response.status != 200:
                    print("⚠ HTTP 服务器未运行，跳过 HTTP 集成测试")
                    print("  提示：运行以下命令启动服务器：")
                    print(f"  python mcp-server/server.py --transport sse --host 127.0.0.1 --port 3000")
                    return None
    except aiohttp.ClientError:
        print("⚠ HTTP 服务器未运行，跳过 HTTP 集成测试")
        print("  提示：运行以下命令启动服务器：")
        print(f"  python mcp-server/server.py --transport sse --host 127.0.0.1 --port 3000")
        return None
    
    client = HTTPMCPClient(base_url)
    
    try:
        # 连接
        await client.connect()
        print("✓ 连接到 HTTP 服务器")
        
        # 初始化
        result = await client.initialize()
        assert "result" in result
        print(f"✓ 初始化成功：{result['result']['server']['name']}")
        
        # 获取工具列表
        tools = await client.list_tools()
        assert len(tools) > 0
        print(f"✓ 获取工具列表成功：{len(tools)} 个工具")
        
        # 测试加法
        result = await client.call_tool("add", {"a": 10, "b": 20})
        response_text = json.loads(result["result"]["content"][0]["text"])
        assert response_text["success"] is True
        assert response_text["result"] == 30
        print(f"✓ 加法测试通过：10 + 20 = {response_text['result']}")
        
        # 测试减法
        result = await client.call_tool("subtract", {"a": 50, "b": 20})
        response_text = json.loads(result["result"]["content"][0]["text"])
        assert response_text["result"] == 30
        print(f"✓ 减法测试通过：50 - 20 = {response_text['result']}")
        
        # 测试乘法
        result = await client.call_tool("multiply", {"a": 5, "b": 6})
        response_text = json.loads(result["result"]["content"][0]["text"])
        assert response_text["result"] == 30
        print(f"✓ 乘法测试通过：5 * 6 = {response_text['result']}")
        
        # 测试除法
        result = await client.call_tool("divide", {"a": 60, "b": 2})
        response_text = json.loads(result["result"]["content"][0]["text"])
        assert response_text["result"] == 30
        print(f"✓ 除法测试通过：60 / 2 = {response_text['result']}")
        
        # 心跳检测
        result = await client.ping()
        assert "result" in result
        print("✓ 心跳检测通过")
        
        print("\n✓ HTTP 模式所有测试通过!")
        return True
        
    except Exception as e:
        print(f"\n✗ HTTP 模式测试失败：{e}")
        return False
    finally:
        await client.close()


async def main():
    """主函数"""
    results = {}
    
    # 测试 stdio 模式
    results["stdio"] = await test_stdio_integration()
    
    print()
    
    # 测试 HTTP 模式
    results["http"] = await test_http_integration()
    
    # 输出总结
    print()
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if results["stdio"]:
        print("✓ stdio 模式：通过")
    else:
        print("✗ stdio 模式：失败")
    
    if results["http"] is True:
        print("✓ HTTP 模式：通过")
    elif results["http"] is False:
        print("✗ HTTP 模式：失败")
    else:
        print("- HTTP 模式：跳过（服务器未运行）")
    
    # 返回退出码
    if results["stdio"] is False or results["http"] is False:
        sys.exit(1)
    else:
        print("\n所有测试通过!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
