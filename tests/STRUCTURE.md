# 测试目录结构说明

## 目录内容

```
tests/
├── README.md                  # 测试文档（如何运行测试、配置要求等）
├── STRUCTURE.md               # 本文件（测试目录结构说明）
├── __init__.py                # Python 包初始化文件
├── test_agent.py              # Agent 核心功能完整测试
└── test_litellm_debug.py      # LiteLLM 配置调试工具
```

## 测试文件说明

### test_agent.py

**用途：** 全面测试 Agent 的核心功能

**测试内容：**
1. 简单问答（不使用工具）- 验证 LLM 基本调用
2. 文件操作（使用工具）- 验证 write_file 工具
3. 目录列表 - 验证 list_dir 工具

**运行方式：**
```bash
# 从项目根目录
python tests/test_agent.py

# 从 tests 目录
cd tests && python test_agent.py
```

**关键特性：**
- 自动加载项目根目录的 .env 配置
- 自动设置 Python 路径以导入项目模块
- 详细的测试输出，便于调试
- 返回退出码（0=成功，1=失败），适合 CI/CD

### test_litellm_debug.py

**用途：** 调试 LiteLLM 配置和 API 调用

**功能：**
- 显示当前的 API 配置（key、base URL、model）
- 启用 LiteLLM 详细日志
- 执行一次简单的 LLM 调用测试

**运行方式：**
```bash
# 从项目根目录
python tests/test_litellm_debug.py

# 从 tests 目录
cd tests && python test_litellm_debug.py
```

**适用场景：**
- 验证 API Key 是否正确配置
- 检查自定义端点是否可访问
- 调试 LiteLLM 调用问题
- 测试新的模型或端点

## 导入路径处理

所有测试文件都使用以下模式处理导入路径：

```python
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入项目模块
from agent import Agent
from config import ...

# 加载项目根目录的 .env 文件
load_dotenv(Path(__file__).parent.parent / ".env")
```

这样可以确保：
1. 从任何位置运行测试都能正确导入模块
2. 自动加载正确的配置文件
3. 不需要安装项目为 Python 包

## 添加新测试

要添加新的测试文件，请遵循以下规范：

1. **文件命名：** `test_<功能名>.py`
2. **文档字符串：** 文件开头添加清晰的描述
3. **导入处理：** 使用上述导入路径模式
4. **主函数：** 使用 `if __name__ == "__main__":` 使测试可直接运行
5. **退出码：** 成功返回 0，失败返回 1

**模板：**

```python
"""测试 <功能名>"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入项目模块
from agent import Agent

# 加载配置
load_dotenv(Path(__file__).parent.parent / ".env")

async def test_feature():
    """测试具体功能"""
    print("开始测试...")
    
    try:
        # 测试代码
        assert True, "测试条件"
        print("✅ 测试通过")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_feature())
    exit(0 if success else 1)
```

## 持续集成

测试可以集成到 CI/CD 流程：

**GitHub Actions 示例：**
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python tests/test_agent.py
          python tests/test_litellm_debug.py
```

## 测试数据

- 测试会在项目根目录的 `workspace/` 中创建临时文件
- `workspace/` 目录已在 `.gitignore` 中，不会被提交
- 每次运行测试都会清理或覆盖之前的测试文件

## 故障排查

常见问题和解决方案请参考 [README.md](README.md) 的故障排查部分。
