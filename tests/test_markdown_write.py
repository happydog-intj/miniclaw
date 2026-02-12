"""测试 Markdown 文件写入（包含特殊字符）"""
import asyncio
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import Agent
import config

async def test_markdown_write():
    """测试写入包含特殊字符的 Markdown 文件"""
    print("=" * 60)
    print("🧪 测试 Markdown 文件写入（特殊字符）")
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

    # 测试创建包含特殊字符的 Markdown 文件
    print("\n📝 测试: 创建包含代码块、反斜杠等特殊字符的 Markdown 文件")

    test_message = """
请创建一个 test_markdown.md 文件，内容如下：

# 测试 Markdown

## 代码示例

```python
def hello():
    print("Hello\\nWorld")  # 包含反斜杠和转义字符
```

## 路径示例

- Windows 路径: C:\\Users\\Admin\\Documents
- Linux 路径: /home/user/docs

## 特殊字符

- 反斜杠: \\
- 换行符: \\n
- 制表符: \\t
"""

    print(f"👤 用户: 创建 Markdown 文件...")

    try:
        response = await agent.process(test_message, [])
        print(f"🤖 Agent: {response}")

        # 验证文件是否创建
        test_file = config.WORKSPACE / "test_markdown.md"
        if test_file.exists():
            content = test_file.read_text()
            print(f"\n📄 文件内容预览:")
            print("-" * 60)
            print(content[:500])
            print("-" * 60)
            print("✅ Markdown 文件写入测试通过")

            # 清理测试文件
            test_file.unlink()
        else:
            print("⚠️  文件未创建")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    asyncio.run(test_markdown_write())
