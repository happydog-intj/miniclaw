"""测试 Agent 功能"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import Agent

# 加载项目根目录的 .env 文件
load_dotenv(Path(__file__).parent.parent / ".env")

async def test_agent():
    """测试 Agent 基础功能"""
    print("=" * 60)
    print("MiniClaw - Agent 测试")
    print("=" * 60)

    # 显示配置
    print("\n📋 当前配置：")
    print(f"  模型: {os.getenv('LLM_MODEL', 'gpt-4o-mini')}")
    print(f"  API Base: {os.getenv('BASE_URL', 'None')}")
    print(f"  User-Agent: {os.getenv('CUSTOM_USER_AGENT', 'None')}")
    print(f"  工作目录: {Path.cwd() / 'workspace'}")

    # 创建 workspace
    workspace = Path.cwd() / "workspace"
    workspace.mkdir(exist_ok=True)

    # 初始化 Agent
    print("\n🤖 初始化 Agent...")
    agent = Agent(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        workspace=workspace,
        max_iterations=5,  # 减少迭代次数以加快测试
        shell_timeout=30,
        api_base=os.getenv("BASE_URL"),
        user_agent=os.getenv("CUSTOM_USER_AGENT")
    )

    # 测试 1: 简单问答
    print("\n" + "=" * 60)
    print("测试 1: 简单问答（不使用工具）")
    print("=" * 60)

    user_msg = "你好！请简单介绍一下你自己。"
    print(f"\n👤 用户: {user_msg}")
    print("🤖 AI 思考中...")

    try:
        response = await agent.process(user_msg, [])
        print(f"\n🤖 AI: {response}\n")
        print("✅ 测试 1 通过")
    except Exception as e:
        print(f"\n❌ 测试 1 失败: {e}\n")
        return False

    # 测试 2: 文件操作
    print("\n" + "=" * 60)
    print("测试 2: 文件操作（使用工具）")
    print("=" * 60)

    user_msg = "请在 workspace 中创建一个 test.txt 文件，内容是 'Hello from MiniClaw!'"
    print(f"\n👤 用户: {user_msg}")
    print("🤖 AI 思考中...")

    try:
        response = await agent.process(user_msg, [])
        print(f"\n🤖 AI: {response}\n")

        # 验证文件是否创建
        test_file = workspace / "test.txt"
        if test_file.exists():
            content = test_file.read_text()
            print(f"✅ 文件创建成功，内容: {content}")
            print("✅ 测试 2 通过")
        else:
            print("❌ 文件未创建")
            return False
    except Exception as e:
        print(f"\n❌ 测试 2 失败: {e}\n")
        return False

    # 测试 3: 列出目录
    print("\n" + "=" * 60)
    print("测试 3: 列出目录")
    print("=" * 60)

    user_msg = "列出 workspace 目录下的所有文件"
    print(f"\n👤 用户: {user_msg}")
    print("🤖 AI 思考中...")

    try:
        response = await agent.process(user_msg, [])
        print(f"\n🤖 AI: {response}\n")
        print("✅ 测试 3 通过")
    except Exception as e:
        print(f"\n❌ 测试 3 失败: {e}\n")
        return False

    print("\n" + "=" * 60)
    print("🎉 所有测试通过！Agent 工作正常")
    print("=" * 60)
    return True

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_agent())
    exit(0 if success else 1)
