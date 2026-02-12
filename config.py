"""配置文件"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# Telegram Bot Token (从 @BotFather 获取)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# LLM 配置
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
API_KEY = os.getenv("API_KEY")

# 如果使用自定义 API 端点
BASE_URL = os.getenv("BASE_URL", None)

# 自定义 HTTP Headers（如 User-Agent）
CUSTOM_USER_AGENT = os.getenv("CUSTOM_USER_AGENT", None)

# 目录配置
BASE_DIR = Path(__file__).parent
WORKSPACE = BASE_DIR / "workspace"
SESSION_DIR = BASE_DIR / "sessions"

# 创建必要的目录
WORKSPACE.mkdir(exist_ok=True)
SESSION_DIR.mkdir(exist_ok=True)

# Agent 配置
MAX_ITERATIONS = 10  # 最大工具调用轮次
SHELL_TIMEOUT = 30   # Shell 命令超时（秒）

# 验证必要的配置
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN 未设置！请在 .env 文件中配置")

if not API_KEY:
    raise ValueError("API_KEY 未设置！请在 .env 文件中配置")
