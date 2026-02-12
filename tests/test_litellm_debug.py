"""调试 LiteLLM 配置"""
import os
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
import litellm

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 加载项目根目录的 .env 文件
load_dotenv(Path(__file__).parent.parent / ".env")

# 启用调试模式
litellm.set_verbose = True

async def test():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    api_base = os.getenv("BASE_URL")
    model = os.getenv("LLM_MODEL")

    print(f"API Key (前10个字符): {api_key[:10]}...")
    print(f"API Key (完整长度): {len(api_key) if api_key else 0}")
    print(f"API Base: {api_base}")
    print(f"Model: {model}")

    # 设置环境变量
    os.environ["OPENAI_API_KEY"] = api_key

    print("\n尝试调用 LiteLLM...")

    try:
        response = await litellm.acompletion(
            model=f"openai/{model}",
            messages=[{"role": "user", "content": "Say hi"}],
            api_base=api_base,
            api_key=api_key,  # 显式传递 API key
            extra_headers={"User-Agent": "moltbot-cli"},
            max_tokens=20
        )
        print("\n✅ 成功!")
        print(f"响应: {response.choices[0].message.content}")
    except Exception as e:
        print(f"\n❌ 失败: {e}")

if __name__ == "__main__":
    asyncio.run(test())
