# 配置示例

本文档展示如何配置 MiniClaw 以适配不同的使用场景。

## 基础配置

### 使用 OpenAI GPT-4o-mini（默认）

```env
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=gpt-4o-mini
```

### 使用 Anthropic Claude

```env
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=claude-3-5-sonnet-20241022
```

## 高级配置

### 使用自定义 API 端点

如果你使用私有部署或第三方 API 网关：

```env
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
API_KEY=your-api-key
BASE_URL=https://your-custom-endpoint.com/v1
LLM_MODEL=gpt-4o-mini
```

**说明：**
- `BASE_URL`: API 端点
- `CUSTOM_USER_AGENT`: 必须设置，否则请求会被拒绝
- `LLM_MODEL`: 使用 Claude 模型名称

### 使用 vLLM 或其他兼容 OpenAI 的端点

```env
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
API_KEY=dummy-key  # vLLM 通常不需要真实的 key
BASE_URL=http://localhost:8000/v1
LLM_MODEL=your-model-name
```

## 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `TELEGRAM_TOKEN` | ✅ | Telegram Bot Token | `1234567890:ABC...` |
| `API_KEY` | ✅ | LLM API Key（支持 OpenAI、Anthropic 等） | `sk-...` 或 `sk-ant-...` |
| `LLM_MODEL` | ❌ | 模型名称，默认 `gpt-4o-mini` | `gpt-4o`, `claude-3-5-sonnet-20241022` |
| `BASE_URL` | ❌ | 自定义 API 端点 | `https://api.openai.com/v1` |
| `CUSTOM_USER_AGENT` | ❌ | 自定义 User-Agent | `miniclaw` |

## 功能特性

### 自定义 API 端点的好处

1. **私有部署**: 使用公司内部部署的 LLM 服务
2. **API 网关**: 通过统一网关管理多个模型
3. **成本优化**: 使用更便宜的第三方服务
4. **合规要求**: 满足数据不出境的要求

### User-Agent 的作用

某些企业级 API 网关或安全策略会检查 HTTP User-Agent 头：

- **身份识别**: 标识调用方的应用身份
- **流量控制**: 基于 User-Agent 进行限流或路由
- **安全策略**: 只允许特定 User-Agent 访问

## 故障排查

### 问题：连接被拒绝

**可能原因：**
- API 端点不正确
- 网络连接问题
- 需要设置 User-Agent

**解决方法：**
1. 检查 `BASE_URL` 是否正确
2. 尝试设置 `CUSTOM_USER_AGENT`
3. 检查网络连接和防火墙设置

### 问题：认证失败

**可能原因：**
- API Key 错误或过期
- 模型名称不匹配

**解决方法：**
1. 确认 API Key 有效
2. 检查 `LLM_MODEL` 与你的 API Key 匹配

### 问题：请求超时

**可能原因：**
- 自定义端点响应慢
- 网络延迟

**解决方法：**
- 可以在 `config.py` 中调整超时设置（未来版本将支持环境变量配置）

## 参考 nanobot 的实现

MiniClaw 参考了 [nanobot](https://github.com/yourusername/nanobot) 的设计：

- **自定义 model key**: 支持在 LiteLLM 调用时传递 `api_base` 参数
- **User-Agent 支持**: 通过 `extra_headers` 传递自定义 HTTP 头

核心代码片段（来自 nanobot）：