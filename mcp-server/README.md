# Simple MCP Server

一个最简单的 Python MCP Server 实现，支持 stdio 和 sse 两种传输方式。

## 功能特点

- ✅ 支持 stdio 传输方式（标准输入输出）
- ✅ 支持 SSE 传输方式（Server-Sent Events）
- ✅ 完整的 MCP 协议实现
- ✅ 提供 7 个实用工具函数
- ✅ 无需复杂依赖

## 安装

```bash
pip install -r requirements.txt
```

## 使用方式

### 1. stdio 模式（默认）

```bash
python server.py --transport stdio
```

或简写：

```bash
python server.py
```

**stdio 模式示例交互：**

```bash
# 初始化请求
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize"}' | python server.py

# 获取工具列表
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}' | python server.py

# 调用加法工具
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 10, "b": 20}}}' | python server.py
```

### 2. SSE 模式

```bash
python server.py --transport sse --host 127.0.0.1 --port 3000
```

**SSE 模式示例请求：**

```bash
# 获取服务器信息
curl http://127.0.0.1:3000/

# 获取工具列表
curl http://127.0.0.1:3000/tools

# 调用工具（简单格式）
curl -X POST http://127.0.0.1:3000/message \
  -H "Content-Type: application/json" \
  -d '{"tool": "add", "params": {"a": 10, "b": 20}}'

# 调用工具（MCP 标准格式）
curl -X POST http://127.0.0.1:3000/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "add",
      "arguments": {"a": 10, "b": 20}
    }
  }'
```

## 可用工具

| 工具名 | 描述 | 参数 |
|--------|------|------|
| `add` | 两个数字相加 | `a`: number, `b`: number |
| `subtract` | 两个数字相减 | `a`: number, `b`: number |
| `multiply` | 两个数字相乘 | `a`: number, `b`: number |
| `divide` | 两个数字相除 | `a`: number, `b`: number |
| `get_time` | 获取当前时间 | 无 |
| `reverse_text` | 反转文本 | `text`: string |
| `count_chars` | 统计文本字符数 | `text`: string |

## 协议说明

本服务器实现了 MCP (Model Context Protocol) 协议，支持以下方法：

- `initialize` - 初始化连接，返回服务器信息和工具列表
- `tools/list` - 获取可用工具列表
- `tools/call` - 调用指定工具
- `ping` - 心跳检测

请求和响应均使用 JSON-RPC 2.0 格式。

## 命令行参数

```
python server.py --help

optional arguments:
  -h, --help            show this help message and exit
  --transport {stdio,sse}
                        Transport mode: stdio or sse (default: stdio)
  --host HOST           Host for SSE mode (default: 127.0.0.1)
  --port PORT           Port for SSE mode (default: 3000)
  --version             show program's version number and exit
```
