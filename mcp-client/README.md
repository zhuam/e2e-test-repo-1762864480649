# MCP Client

一个 Python MCP (Model Context Protocol) Client 实现，支持 stdio 和 http 两种协议方式。

## 功能特点

- ✅ 支持 stdio 传输方式（通过子进程与本地 MCP 服务器通信）
- ✅ 支持 HTTP 传输方式（通过 HTTP POST 与远程 MCP 服务器通信）
- ✅ 完整的 MCP 协议实现
- ✅ 提供演示模式和交互模式
- ✅ 包含完整的单元测试

## 安装

```bash
pip install -r requirements.txt
```

## 使用方式

### 1. stdio 模式（默认）

**演示模式：**

```bash
python client.py --demo --transport stdio
```

**交互模式：**

```bash
python client.py -i --transport stdio
```

**编程方式：**

```python
import asyncio
from client import StdioMCPClient

async def main():
    # 创建客户端
    client = StdioMCPClient(
        command=["python", "mcp-server/server.py", "--transport", "stdio"]
    )
    
    # 连接
    await client.connect()
    
    # 初始化
    await client.initialize()
    
    # 获取工具列表
    tools = await client.list_tools()
    print(f"可用工具：{[t['name'] for t in tools]}")
    
    # 调用工具
    result = await client.call_tool("add", {"a": 10, "b": 20})
    print(f"10 + 20 = {result}")
    
    # 关闭连接
    await client.close()

asyncio.run(main())
```

### 2. HTTP 模式

首先启动 HTTP 模式的 MCP 服务器：

```bash
python mcp-server/server.py --transport sse --host 127.0.0.1 --port 3000
```

**演示模式：**

```bash
python client.py --demo --transport http --url http://127.0.0.1:3000
```

**交互模式：**

```bash
python client.py -i --transport http --url http://127.0.0.1:3000
```

**编程方式：**

```python
import asyncio
from client import HTTPMCPClient

async def main():
    # 创建客户端
    client = HTTPMCPClient("http://127.0.0.1:3000")
    
    # 连接
    await client.connect()
    
    # 初始化
    await client.initialize()
    
    # 获取工具列表
    tools = await client.list_tools()
    
    # 调用工具
    result = await client.call_tool("add", {"a": 10, "b": 20})
    print(f"10 + 20 = {result}")
    
    # 关闭连接
    await client.close()

asyncio.run(main())
```

## 交互模式命令

| 命令 | 描述 |
|------|------|
| `list` | 列出所有可用工具 |
| `call <tool> <json_args>` | 调用工具，如：`call add {"a": 1, "b": 2}` |
| `ping` | 心跳检测 |
| `help` | 显示帮助信息 |
| `quit` | 退出 |

## 命令行参数

```
python client.py --help

optional arguments:
  -h, --help            show this help message and exit
  --transport {stdio,http}
                        Transport mode: stdio or http (default: stdio)
  --url URL             URL for HTTP mode (default: http://127.0.0.1:3000)
  --demo                Run demo mode
  --interactive, -i     Run interactive mode
```

## 运行测试

```bash
# 运行单元测试
python test_client.py

# 带详细输出
python test_client.py -v
```

## 协议说明

本客户端实现了 MCP (Model Context Protocol) 协议，支持以下方法：

- `initialize` - 初始化连接，获取服务器信息
- `tools/list` - 获取可用工具列表
- `tools/call` - 调用指定工具
- `ping` - 心跳检测

请求和响应均使用 JSON-RPC 2.0 格式。

## 架构

```
MCPClient (基类)
├── StdioMCPClient (stdio 传输)
└── HTTPMCPClient (HTTP 传输)
```

两种客户端实现相同的接口，可以根据需要灵活切换。
