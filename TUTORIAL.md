# 从0到1实现一个最简单的 MiniClaw - 详细教程

> **目标**：用 400 行 Python 代码，从零开始构建一个功能完整的 AI 助手

---

## 📋 目录

1. [设计理念](#1-设计理念)
2. [核心概念](#2-核心概念)
3. [逐步实现](#3-逐步实现)
4. [测试运行](#4-测试运行)
5. [扩展功能](#5-扩展功能)
6. [常见问题](#6-常见问题)

---

## 1. 设计理念

### 🎯 核心原则

**极简主义 (Minimalism)**
- 去掉所有不必要的抽象层
- 每个文件职责单一清晰
- 代码即文档，一看就懂

**实用主义 (Pragmatism)**
- 优先实现核心功能
- 使用成熟的第三方库
- 避免过早优化

### 📊 与完整 MiniClaw 的对比

```
完整版 MiniClaw (430,000+ 行):
├── 复杂的事件总线系统
├── 插件化架构
├── 多种 Channel 抽象
├── 浏览器自动化
├── 子代理系统
├── 复杂的配置管理
└── ... 更多企业级特性

MiniClaw (400 行):
├── 简单的消息路由
├── 直接的工具调用
├── 单一 Telegram 集成
└── 核心 Agent 逻辑
```

**我们保留了什么？**
- ✅ LLM 工具调用（Function Calling）
- ✅ 迭代式处理（ReAct 模式）
- ✅ 会话管理
- ✅ 文件和命令执行

**我们简化了什么？**
- ❌ 复杂的事件总线 → 简单的 async 函数
- ❌ 工具注册表 → if-else 匹配
- ❌ 多渠道抽象 → 只支持 Telegram
- ❌ 插件系统 → 直接修改代码

---

## 2. 核心概念

### 2.1 什么是 Function Calling？

**传统方式：**
```
用户: "今天天气怎么样？"
LLM: "抱歉，我无法获取实时天气信息。"
```

**有 Function Calling：**
```
用户: "今天天气怎么样？"
LLM: [调用工具] get_weather(location="current")
工具: 返回 "晴天，25°C"
LLM: "今天是晴天，气温 25°C"
```

**核心机制：**

1. **定义工具** (Tool Definition)
```python
{
    "name": "get_weather",
    "description": "获取天气信息",
    "parameters": {
        "location": {"type": "string"}
    }
}
```

2. **LLM 决策**
```
LLM 分析用户问题 → 判断需要哪个工具 → 生成工具调用
```

3. **执行工具**
```python
result = execute_tool("get_weather", {"location": "Beijing"})
```

4. **返回结果**
```python
messages.append({
    "role": "tool",
    "content": result
})
# 再次调用 LLM，让它总结结果
```

### 2.2 迭代式工具调用（ReAct 模式）

**为什么需要多轮？**

假设用户问："分析 data.csv 并生成报告"

```
第1轮:
LLM → 需要先读取文件
工具 → list_dir() 查看有哪些文件

第2轮:
LLM → 找到了 data.csv，读取它
工具 → read_file("data.csv")

第3轮:
LLM → 分析数据...
工具 → write_file("report.txt", "...")

第4轮:
LLM → "✅ 已生成报告 report.txt"
```

**这就是 ReAct (Reasoning + Acting)**：
- **Reasoning**: LLM 思考下一步
- **Acting**: 调用工具执行
- **循环**: 直到任务完成

### 2.3 会话管理

**为什么需要？**

```
用户A: "我叫张三"
Bot: "你好张三！"
[过了一会儿...]
用户A: "我叫什么名字？"
Bot: "你叫张三"  ← 需要记住历史
```

**实现方式：**

```python
# sessions/123456.json
[
    {"role": "user", "content": "我叫张三"},
    {"role": "assistant", "content": "你好张三！"},
    {"role": "user", "content": "我叫什么名字？"},
    {"role": "assistant", "content": "你叫张三"}
]
```

每个用户（chat_id）独立的历史记录。

---

## 3. 逐步实现

### Step 1: 配置管理 (config.py)

**职责：**
- 加载环境变量
- 验证必要的配置
- 创建工作目录

```python
import os
from pathlib import Path

# 从环境变量读取
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 目录结构
WORKSPACE = Path("./workspace")
SESSION_DIR = Path("./sessions")

# 验证
if not TELEGRAM_TOKEN:
    raise ValueError("缺少 TELEGRAM_TOKEN")
```

**为什么分离配置？**
- 安全：敏感信息不硬编码
- 灵活：切换环境无需改代码
- 清晰：所有配置集中管理

---

### Step 2: Agent 核心 (agent.py)

#### 2.1 初始化

```python
class Agent:
    def __init__(self, model, workspace):
        self.model = model
        self.workspace = workspace
        self.max_iterations = 10
```

#### 2.2 主处理流程

```python
async def process(self, user_message, history):
    # 1. 构建 messages
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_message}
    ]
    
    # 2. 迭代循环
    for i in range(max_iterations):
        # 调用 LLM
        response = await acompletion(
            model=self.model,
            messages=messages,
            tools=self._get_tools()
        )
        
        # 如果没有工具调用，结束
        if not response.tool_calls:
            return response.content
        
        # 执行工具
        for tool_call in response.tool_calls:
            result = self._execute_tool(
                tool_call.function.name,
                tool_call.function.arguments
            )
            messages.append(tool_result)
    
    return "达到最大迭代次数"
```

#### 2.3 工具定义

```python
def _get_tools(self):
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "读取文件内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    }
                }
            }
        },
        # ... 其他工具
    ]
```

#### 2.4 工具执行

```python
def _execute_tool(self, name, args):
    if name == "read_file":
        path = self.workspace / args["path"]
        return path.read_text()
    
    elif name == "write_file":
        path = self.workspace / args["path"]
        path.write_text(args["content"])
        return f"已写入 {path}"
    
    elif name == "exec_shell":
        result = subprocess.run(
            args["command"],
            shell=True,
            capture_output=True
        )
        return result.stdout
```

**关键点：**
- 所有文件操作在 workspace 内
- Shell 命令需要安全检查
- 返回字符串结果

---

### Step 3: Telegram Bot (bot.py)

#### 3.1 会话管理

```python
def _load_history(chat_id):
    file = SESSION_DIR / f"{chat_id}.json"
    if file.exists():
        return json.loads(file.read_text())
    return []

def _save_history(chat_id, history):
    file = SESSION_DIR / f"{chat_id}.json"
    file.write_text(json.dumps(history, indent=2))
```

#### 3.2 消息处理

```python
async def handle_message(update, context):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    
    # 1. 加载历史
    history = load_history(chat_id)
    
    # 2. 调用 agent
    agent = Agent(model=LLM_MODEL, workspace=WORKSPACE)
    response = await agent.process(user_text, history)
    
    # 3. 保存历史
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": response})
    save_history(chat_id, history)
    
    # 4. 发送响应
    await update.message.reply_text(response)
```

#### 3.3 启动 Bot

```python
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()
```

---

## 4. 测试运行

### 4.1 环境准备

```bash
# 1. 创建项目目录
mkdir miniclaw && cd miniclaw

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install python-telegram-bot litellm loguru python-dotenv
```

### 4.2 配置

创建 `.env` 文件：
```env
TELEGRAM_TOKEN=你的_Bot_Token
OPENAI_API_KEY=你的_API_Key
LLM_MODEL=gpt-4o-mini
```

### 4.3 启动

```bash
python bot.py
```

### 4.4 测试场景

**场景1：基本对话**
```
你: 你好
Bot: 你好！有什么可以帮助你的吗？
```

**场景2：文件操作**
```
你: 创建一个 hello.txt 文件，内容是 "Hello World"
Bot: [调用 write_file]
     ✅ 已写入文件：hello.txt
```

**场景3：读取文件**
```
你: 读取 hello.txt 的内容
Bot: [调用 read_file]
     文件内容：Hello World
```

**场景4：执行命令**
```
你: 列出当前目录的所有文件
Bot: [调用 list_dir]
     目录内容：
     📄 hello.txt
```

**场景5：多步骤任务**
```
你: 创建一个 Python 脚本，打印 1 到 10 的平方，然后执行它
Bot: 
[第1轮] 调用 write_file 创建 squares.py
[第2轮] 调用 exec_shell 执行 python squares.py
结果：
1
4
9
16
25
36
49
64
81
100
```

---

## 5. 扩展功能

### 5.1 添加网络搜索

```python
# 在 agent.py 的 _get_tools() 中添加
{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "搜索网络信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"}
            }
        }
    }
}

# 在 _execute_tool() 中处理
elif name == "web_search":
    import requests
    api_key = os.getenv("BRAVE_API_KEY")
    response = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": api_key},
        params={"q": args["query"]}
    )
    results = response.json()
    # 提取前 3 条结果
    top_results = results["web"]["results"][:3]
    return "\n\n".join([
        f"{r['title']}\n{r['description']}\n{r['url']}"
        for r in top_results
    ])
```

### 5.2 添加图片理解

```python
# 在 bot.py 的 handle_message 中
if update.message.photo:
    # 下载图片
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()
    
    # 转换为 base64
    import base64
    image_b64 = base64.b64encode(image_bytes).decode()
    
    # 构建包含图片的 message
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": caption or "分析这张图片"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ]
    })
```

### 5.3 添加流式输出

```python
# 在 agent.py 中修改 acompletion 调用
response = await acompletion(
    model=self.model,
    messages=messages,
    tools=tools,
    stream=True  # 启用流式
)

# 处理流式响应
collected_text = ""
async for chunk in response:
    if chunk.choices[0].delta.content:
        collected_text += chunk.choices[0].delta.content
        # 实时更新 Telegram 消息
        await update.message.edit_text(collected_text)
```

### 5.4 添加记忆系统

```python
# 在 workspace/ 中创建 MEMORY.md
def _get_system_prompt(self):
    memory_file = self.workspace / "MEMORY.md"
    memory_content = ""
    if memory_file.exists():
        memory_content = f"\n\n长期记忆：\n{memory_file.read_text()}"
    
    return f"""你是一个AI助手...{memory_content}"""

# 添加记忆工具
{
    "name": "update_memory",
    "description": "更新长期记忆",
    "parameters": {
        "content": {"type": "string"}
    }
}
```

---

## 6. 常见问题

### Q1: LiteLLM 是什么？

**A:** LiteLLM 是一个统一的 LLM API 封装库，支持：
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Azure OpenAI
- 开源模型 (Ollama, vLLM)

**切换模型只需改配置：**
```python
# OpenAI
model = "gpt-4o-mini"

# Claude
model = "claude-3-5-sonnet-20241022"

# 本地 Ollama
model = "ollama/llama3.2"
```

### Q2: 历史记录会爆炸吗？

**A:** 会！建议限制长度：

```python
MAX_HISTORY_MESSAGES = 20

def _load_history(chat_id):
    history = json.loads(...)
    # 只保留最近 20 条
    return history[-MAX_HISTORY_MESSAGES:]
```

或使用滑动窗口：
```python
# 保留最近的用户消息 + 助手回复
user_messages = [m for m in history if m["role"] == "user"][-10:]
assistant_messages = [m for m in history if m["role"] == "assistant"][-10:]
```

### Q3: Token 消耗如何优化？

**A:** 几个技巧：

1. **压缩历史**
```python
# 使用摘要替代完整历史
if len(history) > 10:
    summary = await summarize(history[:5])
    history = [
        {"role": "system", "content": f"之前的对话摘要：{summary}"},
        *history[5:]
    ]
```

2. **工具结果截断**
```python
if len(result) > 2000:
    result = result[:2000] + "\n... (已截断)"
```

3. **使用更小的模型**
```python
# 简单对话用 gpt-4o-mini
# 复杂任务用 gpt-4o
```

### Q4: 如何调试？

**A:** 使用 loguru 打印详细日志：

```python
from loguru import logger

logger.debug(f"Messages: {messages}")
logger.info(f"Tool call: {tool_name}({args})")
logger.error(f"Error: {e}")
```

查看 `sessions/` 目录的 JSON 文件，了解对话历史。

### Q5: 部署到服务器？

**A:** 使用 systemd service：

```ini
# /etc/systemd/system/miniclaw.service
[Unit]
Description=MiniClaw Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/miniclaw
Environment="PATH=/home/ubuntu/miniclaw/venv/bin"
ExecStart=/home/ubuntu/miniclaw/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动：
```bash
sudo systemctl enable miniclaw
sudo systemctl start miniclaw
sudo systemctl status miniclaw
```

---

## 🎓 总结

### 你学到了什么

1. **LLM Function Calling** 的原理和实现
2. **迭代式工具调用**（ReAct 模式）
3. **会话管理**的简单有效方案
4. **Telegram Bot** 的基本使用
5. **极简架构**的设计思想

### 下一步

- 🔧 **实践**：运行代码，体验工具调用
- 📝 **扩展**：添加你需要的功能（搜索、图片、定时任务）
- 🛡️ **加固**：改进安全性（白名单、沙箱）
- 🚀 **部署**：上线到服务器
- 🌟 **分享**：告诉其他人你的实现

### 推荐阅读

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [完整版 MiniClaw](https://github.com/openclaw/openclaw)

---

**恭喜你！🎉**

你已经掌握了构建 AI Agent 的核心技能。

从这 400 行代码开始，构建属于你自己的 AI 助手！
