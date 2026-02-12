# MiniClaw 🦞

<div align="center">
  <img src="https://raw.githubusercontent.com/uknownothingsnow/miniclaw/main/assets/logo.png" alt="MiniClaw Logo" width="200"/>

  > 一个极简版的 AI 助手，用 **400 行代码**实现核心功能：Telegram 集成 + LLM 工具调用 + 文件操作
</div>

## 📖 教程目标

通过这个教程，你将学会：
- ✅ 如何构建一个基于 Telegram 的 AI 助手
- ✅ 理解 LLM Function Calling（工具调用）的原理
- ✅ 实现迭代式工具调用（类似 ReAct）
- ✅ 管理多用户会话历史
- ✅ 安全地执行文件操作和 Shell 命令

**总代码量：~400 行 Python**

---

## 🏗️ 架构设计

```
┌──────────────────────────────────────────┐
│          Telegram Bot API                │
│     (python-telegram-bot 库)             │
└──────────────┬───────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────┐
│  bot.py - 消息路由器                     │
│  - 接收用户消息                          │
│  - 加载/保存会话历史（JSON 文件）         │
│  - 调用 agent.process()                 │
│  - 返回响应                              │
└──────────────┬───────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────┐
│  agent.py - AI 大脑                      │
│  - 构建 messages (system + history)     │
│  - 调用 LLM (通过 litellm)              │
│  - 执行工具（read/write/exec）           │
│  - 迭代处理（最多 10 轮）                │
└──────────────────────────────────────────┘
```

**核心理念：去掉所有不必要的抽象，直达本质！**

---

## 🚀 快速开始

### 1. 准备工作

#### 1.1 获取 Telegram Bot Token

1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建机器人
3. 按提示设置名称（如：`My Mini Bot`）
4. 获得 Token（格式：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`）

#### 1.2 获取 LLM API Key

选择以下任一提供商：

**选项1：OpenAI**
- 访问 https://platform.openai.com/api-keys
- 创建 API Key
- 模型推荐：`gpt-4o-mini`（性价比高）、`gpt-4o`（最强）

**选项2：Qwen (阿里云通义千问)**
- 访问 https://dashscope.aliyun.com/
- 开通服务并获取 API Key
- 模型推荐：`qwen-plus`（性价比高）、`qwen3-max-2026-01-23`（最强）

**选项3：DeepSeek**
- 访问 https://platform.deepseek.com/
- 创建 API Key
- 模型推荐：`deepseek-chat`（通用）、`deepseek-reasoner`（推理）

**选项4：其他兼容 OpenAI 格式的服务**
- 支持任何提供 OpenAI 兼容 API 的服务

### 2. 安装

```bash
# 克隆或下载项目
cd miniclaw

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的 Token
nano .env
```

`.env` 配置示例：

**使用 OpenAI：**
```env
TELEGRAM_TOKEN=你的_Telegram_Token
API_KEY=sk-your-openai-api-key
BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

**使用 Qwen (阿里云)：**
```env
TELEGRAM_TOKEN=你的_Telegram_Token
API_KEY=sk-your-qwen-api-key
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

**使用 DeepSeek：**
```env
TELEGRAM_TOKEN=你的_Telegram_Token
API_KEY=sk-your-deepseek-api-key
BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

**使用自定义端点：**
```env
TELEGRAM_TOKEN=你的_Telegram_Token
API_KEY=your-api-key
BASE_URL=https://your-custom-endpoint.com/v1
LLM_MODEL=your-model-name
CUSTOM_USER_AGENT=miniclaw  # 某些企业端点需要
```

**配置参数说明：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `TELEGRAM_TOKEN` | ✅ | Telegram Bot Token |
| `API_KEY` | ✅ | LLM API Key |
| `BASE_URL` | ❌ | API 端点地址（默认 OpenAI） |
| `LLM_MODEL` | ❌ | 模型名称（默认 gpt-4o-mini） |
| `CUSTOM_USER_AGENT` | ❌ | 自定义 User-Agent 头 |

### 4. 运行

```bash
python bot.py
```

看到以下输出表示成功：
```
2026-02-07 18:00:00.000 | INFO     | bot:main:185 - ==================================================
2026-02-07 18:00:00.001 | INFO     | bot:main:186 - MiniClaw - 极简版 AI 助手
2026-02-07 18:00:00.002 | INFO     | bot:main:187 - ==================================================
2026-02-07 18:00:00.500 | INFO     | agent:__init__:19 - Agent initialized: model=gpt-4o-mini, workspace=/path/to/workspace
2026-02-07 18:00:00.501 | INFO     | bot:run:168 - Starting Telegram bot...
2026-02-07 18:00:00.502 | INFO     | bot:run:178 - Bot is running (model: gpt-4o-mini)
```

### 5. 测试

#### 5.1 运行自动化测试

在启动 Bot 之前，可以先运行测试验证配置：

```bash
# 运行完整的 Agent 功能测试
python tests/test_agent.py

# 运行 LiteLLM 调试工具（用于排查配置问题）
python tests/test_litellm_debug.py
```

详细的测试说明请查看 [tests/README.md](tests/README.md)。

#### 5.2 在 Telegram 中测试

1. 在 Telegram 中找到你的 bot
2. 发送 `/start` 开始对话
3. 试试这些命令：

```
写一个 hello.py 文件，内容是打印 hello world
```

```
执行 python hello.py
```

```
列出当前目录的所有文件
```

---

## 📁 项目结构

```
miniclaw/
├── bot.py                  # Telegram Bot（150行）
├── agent.py                # AI Agent + 工具（200行）
├── config.py               # 配置管理（50行）
├── requirements.txt        # 依赖
├── .env.example            # 配置模板
├── .env                    # 实际配置（已在 .gitignore 中）
├── .gitignore              # Git 忽略规则
├── check_security.sh       # 安全检查脚本
├── README.md               # 本教程
├── CONFIG_EXAMPLES.md      # 配置示例文档
├── TUTORIAL.md             # 详细教程
├── sessions/               # 会话历史（JSON，已忽略）
├── workspace/              # Bot 的工作目录（已忽略）
└── tests/                  # 测试文件
    ├── README.md           # 测试说明
    ├── test_agent.py       # Agent 功能测试
    └── test_litellm_debug.py  # LiteLLM 调试工具
```

### 🔒 安全说明

项目已配置 `.gitignore` 保护敏感信息：

```bash
# 运行安全检查
./check_security.sh

# 检查项目：
# ✅ .env 文件已被忽略
# ✅ sessions/ 和 workspace/ 已被忽略
# ✅ 没有硬编码的 API Keys
```

**重要提示：**
- ✅ `.env` 文件包含敏感密钥，已在 `.gitignore` 中，不会被提交
- ✅ 使用 `.env.example` 作为配置模板，不含真实密钥
- ✅ 提交前运行 `./check_security.sh` 验证安全性

---

## 🔧 核心代码解析

### 1. Agent 的迭代式工具调用

```python
# agent.py - process() 方法核心逻辑

for iteration in range(1, max_iterations + 1):
    # 调用 LLM
    response = await acompletion(
        model=self.model,
        messages=messages,
        tools=tools
    )
    
    # 如果没有工具调用，返回最终响应
    if not response.tool_calls:
        return response.content
    
    # 有工具调用，执行工具
    for tool_call in response.tool_calls:
        result = execute_tool(tool_call.name, tool_call.args)
        messages.append(tool_result)  # 添加结果到历史
    
    # 继续下一轮（LLM 可以根据结果决定是否再调用工具）
```

**为什么需要循环？**

LLM 可能需要多步工具调用：
1. `list_dir()` 查看有哪些文件
2. `read_file("config.json")` 读取配置
3. `write_file("output.txt", ...)` 写入结果

### 2. 会话管理（简单但有效）

```python
# bot.py

def _load_history(chat_id: int) -> list:
    file = SESSION_DIR / f"{chat_id}.json"
    if file.exists():
        return json.loads(file.read_text())
    return []

def _save_history(chat_id: int, history: list):
    file = SESSION_DIR / f"{chat_id}.json"
    file.write_text(json.dumps(history, indent=2))
```

每个用户独立的 JSON 文件，简单可靠！

### 3. 工具定义（OpenAI Function Calling 格式）

```python
{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "读取文件内容",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"}
            },
            "required": ["path"]
        }
    }
}
```

LLM 会根据这个定义决定何时调用工具。

---

## 🎯 功能特性

### ✅ 已实现

- 📱 Telegram 集成（polling 模式）
- 🤖 LLM 工具调用（read/write/exec/list）
- 🔄 迭代式处理（最多 10 轮）
- 💾 多用户会话管理（JSON 持久化）
- 🛡️ 基本安全检查（危险命令拦截）
- 📊 状态查询（`/status` 命令）
- 🗑️ 清空历史（`/clear` 命令）

### 🚧 可扩展功能

想添加更多功能？只需修改 `agent.py`:

#### 1. Web 搜索

```python
# 在 _get_tools() 中添加
{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "搜索网络信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            }
        }
    }
}

# 在 _execute_tool() 中处理
elif name == "web_search":
    # 调用 Brave Search API 或其他搜索服务
    return search_results
```

#### 2. 图片生成

```python
elif name == "generate_image":
    # 调用 DALL-E / Stable Diffusion
    image_url = generate_image(args["prompt"])
    return f"图片已生成：{image_url}"
```

#### 3. 定时任务

可以添加一个简单的 cron 系统，在 bot.py 中用 `asyncio.create_task()` 实现。

---

## 🔒 安全建议

**当前实现适合个人使用，生产环境需要加强：**

### 1. 命令执行安全
```python
# 当前：简单的黑名单
dangerous_patterns = ["rm -rf /", "mkfs"]

# 建议：白名单 + 沙箱
ALLOWED_COMMANDS = ["ls", "cat", "python", "node"]
# 或使用 Docker 容器隔离
```

### 2. 文件路径安全
```python
# 防止路径遍历攻击
def is_safe_path(path: Path) -> bool:
    return path.resolve().is_relative_to(WORKSPACE.resolve())
```

### 3. 用户认证
```python
# 在 config.py 中添加
ALLOWED_USER_IDS = [123456789, 987654321]

# 在 bot.py 中检查
if update.effective_user.id not in ALLOWED_USER_IDS:
    await update.message.reply_text("⛔ 未授权")
    return
```

---

## 🤔 常见问题

### Q1: 为什么使用 litellm？
**A:** litellm 统一了不同 LLM 提供商的 API（OpenAI、Anthropic、Azure 等），一行代码切换模型。

### Q2: 会话历史会无限增长吗？
**A:** 是的！建议添加历史长度限制：
```python
MAX_HISTORY = 20  # 只保留最近 20 条消息
history = history[-MAX_HISTORY:]
```

### Q3: 如何支持多语言？
**A:** 修改 `_get_system_prompt()` 中的提示词即可，LLM 会自动适应。

### Q4: 可以部署到服务器吗？
**A:** 可以！建议使用：
- **Docker**: 容器化部署
- **systemd**: Linux 服务守护
- **supervisor**: 进程管理

---

## 📚 延伸学习

### 理解 Function Calling

OpenAI 的官方文档：
https://platform.openai.com/docs/guides/function-calling

### ReAct 模式

论文：*ReAct: Synergizing Reasoning and Acting in Language Models*
https://arxiv.org/abs/2210.03629

### Telegram Bot API

官方文档：
https://core.telegram.org/bots/api

---

## 🎓 总结

### 核心收获

1. **极简架构**：400 行代码实现完整功能
2. **迭代式工具调用**：LLM 可以像人类一样分步思考
3. **会话管理**：JSON 文件简单可靠
4. **安全意识**：命令执行需要谨慎处理

### 与完整版 OpenClaw 的对比

| 特性 | MiniClaw | 完整版 OpenClaw |
|------|--------------|----------------|
| 代码量 | ~400 行 | 430,000+ 行 |
| 消息渠道 | Telegram | Telegram/WhatsApp/Discord/Signal... |
| 工具系统 | if-else | 插件化注册表 |
| 会话管理 | JSON 文件 | SQLite + 复杂缓存 |
| 浏览器控制 | ❌ | ✅ (Playwright) |
| 子代理 | ❌ | ✅ |
| 定时任务 | ❌ | ✅ (cron) |
| 适用场景 | 学习/个人使用 | 生产环境 |

### 下一步

- 🔧 **实践**：运行起来，体验工具调用
- 📝 **扩展**：添加你需要的功能
- 🚀 **优化**：改进安全性、性能
- 🌟 **分享**：把你的改进贡献回社区！

---

## 📞 反馈与贡献

遇到问题？有改进建议？

- **Issues**: 提交问题报告
- **Pull Requests**: 贡献代码改进

---

## 📄 许可证

MIT License - 自由使用、修改、分发

---

**Happy Coding! 🎉**

从这 400 行代码开始，构建属于你自己的 AI 助手！
