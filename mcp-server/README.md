# Simple MCP Server

一个最简单的 Python MCP Server 实现，支持 stdio 和 http 两种传输方式。

## 功能特点

- ✅ 支持 stdio 传输方式（标准输入输出）
- ✅ 支持 HTTP 传输方式（REST API 风格）
- ✅ 完整的 MCP 协议实现
- ✅ 提供 7 个实用工具函数
- ✅ 无需复杂依赖
- ✅ 包含完整的功能测试

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

### 2. HTTP 模式

```bash
python server.py --transport http --host 127.0.0.1 --port 3000
```

**HTTP 模式 API 端点：**

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 服务器信息和可用端点 |
| `/health` | GET | 健康检查 |
| `/tools` | GET | 获取工具列表 |
| `/call` | POST | 调用工具（简单格式） |
| `/rpc` | POST | JSON-RPC 格式请求 |

**HTTP 模式示例请求：**

```bash
# 获取服务器信息
curl http://127.0.0.1:3000/

# 健康检查
curl http://127.0.0.1:3000/health

# 获取工具列表
curl http://127.0.0.1:3000/tools

# 调用工具（简单格式）
curl -X POST http://127.0.0.1:3000/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "add", "params": {"a": 10, "b": 20}}'

# 调用工具（JSON-RPC 格式）
curl -X POST http://127.0.0.1:3000/rpc \
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
  --transport {stdio,http}
                        Transport mode: stdio or http (default: stdio)
  --host HOST           Host for HTTP mode (default: 127.0.0.1)
  --port PORT           Port for HTTP mode (default: 3000)
  --version             show program's version number and exit
```

## 运行测试

```bash
# 运行功能测试
python test_server.py
```

测试包括：
- stdio 传输方式测试（12 个测试用例）
- HTTP 传输方式测试（11 个测试用例）

测试内容涵盖：
- 初始化和工具列表获取
- 所有工具的调用测试
- 错误处理测试（除以零、未知工具、缺少参数等）
- HTTP 端点测试

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动 HTTP 服务器
python server.py --transport http --port 3000

# 3. 在另一个终端测试
curl http://127.0.0.1:3000/tools
curl -X POST http://127.0.0.1:3000/call -H "Content-Type: application/json" -d '{"tool": "add", "params": {"a": 5, "b": 3}}'
```

## 示例输出

**HTTP 工具调用响应：**
```json
{
  "success": true,
  "result": 8
}
```

**JSON-RPC 响应：**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"result\": 8}"
      }
    ]
  }
}
```
