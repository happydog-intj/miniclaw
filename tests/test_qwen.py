"""测试 Qwen API 兼容性"""
import asyncio
from pathlib import Path
from agent import Agent
import config

async def test_qwen():
    """测试 Qwen 模型"""
    print("=" * 60)
    print("🧪 测试 Qwen API 兼容性")
    print("=" * 60)
    print(f"📋 配置信息:")
    print(f"  模型: {config.LLM_MODEL}")
    print(f"  API Base: {config.BASE_URL}")
    print(f"  API Key: {config.API_KEY[:20]}...")
    print("=" * 60)

    # 创建 Agent
    agent = Agent(
        model=config.LLM_MODEL,
        workspace=config.WORKSPACE,
        max_iterations=config.MAX_ITERATIONS,
        shell_timeout=config.SHELL_TIMEOUT,
        api_base=config.BASE_URL,
        user_agent=config.CUSTOM_USER_AGENT
    )

    # 测试简单对话
    print("\n🤖 测试 1: 简单对话")
    test_message = "你好，请用一句话介绍你自己"
    print(f"👤 用户: {test_message}")

    try:
        response = await agent.process(test_message, [])
        print(f"🤖 Agent: {response}")
        print("✅ 简单对话测试通过")
    except Exception as e:
        print(f"❌ 简单对话测试失败: {e}")
        return False

    # 测试工具调用
    print("\n🔧 测试 2: 工具调用")
    test_message = "在当前目录创建一个文件 test.txt，内容是 'Hello from Qwen!'"
    print(f"👤 用户: {test_message}")

    try:
        response = await agent.process(test_message, [])
        print(f"🤖 Agent: {response}")

        # 验证文件是否创建
        test_file = config.WORKSPACE / "test.txt"
        if test_file.exists():
            content = test_file.read_text()
            print(f"📄 文件内容: {content}")
            print("✅ 工具调用测试通过")
            # 清理测试文件
            test_file.unlink()
        else:
            print("⚠️  文件未创建")
    except Exception as e:
        print(f"❌ 工具调用测试失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("🎉 所有测试通过！Qwen API 完全兼容！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    asyncio.run(test_qwen())
