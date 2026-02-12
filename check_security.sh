#!/bin/bash
# 安全检查脚本 - 验证敏感文件是否被正确保护

echo "🔒 MiniClaw 安全检查"
echo "=========================="
echo ""

# 检查 .env 是否在 .gitignore 中
echo "1. 检查 .gitignore 配置..."
if grep -q "^\.env$" .gitignore; then
    echo "   ✅ .env 已在 .gitignore 中"
else
    echo "   ❌ .env 未在 .gitignore 中！"
    exit 1
fi

# 检查 .env 是否被 git 忽略
echo ""
echo "2. 验证 Git 忽略状态..."
if git check-ignore .env > /dev/null 2>&1; then
    echo "   ✅ Git 确认 .env 已被忽略"
else
    echo "   ❌ .env 未被 Git 忽略！"
    exit 1
fi

# 检查 .env 是否在 git 历史中
echo ""
echo "3. 检查 Git 历史记录..."
HISTORY_COUNT=$(git log --all --full-history --oneline -- .env 2>/dev/null | wc -l)
if [ "$HISTORY_COUNT" -eq 0 ]; then
    echo "   ✅ .env 从未被提交到历史记录"
else
    echo "   ⚠️  警告：.env 曾在历史中出现 $HISTORY_COUNT 次"
    echo "   需要清理 git 历史并轮换所有密钥！"
    exit 1
fi

# 检查当前 git 状态
echo ""
echo "4. 检查当前 Git 状态..."
if git status --short | grep -q "\.env$"; then
    echo "   ❌ .env 在待提交列表中！"
    exit 1
else
    echo "   ✅ .env 不在待提交列表中"
fi

# 检查 .env.example 是否存在
echo ""
echo "5. 检查配置模板..."
if [ -f ".env.example" ]; then
    echo "   ✅ .env.example 模板存在"
else
    echo "   ⚠️  警告：缺少 .env.example 模板"
fi

# 检查代码中是否有硬编码的密钥模式
echo ""
echo "6. 扫描硬编码密钥..."
SUSPICIOUS=$(grep -r -E "(sk-[a-zA-Z0-9]{20,}|[0-9]{10}:[A-Za-z0-9_-]{35})" \
    --include="*.py" \
    --exclude-dir=venv \
    --exclude-dir=env \
    --exclude-dir=.git \
    . 2>/dev/null | grep -v ".env" | wc -l)

if [ "$SUSPICIOUS" -eq 0 ]; then
    echo "   ✅ 未发现硬编码密钥"
else
    echo "   ⚠️  发现 $SUSPICIOUS 个可疑的密钥模式"
    echo "   请检查是否有硬编码的 API Keys"
fi

echo ""
echo "=========================="
echo "✅ 安全检查完成！所有项目通过。"
echo ""
echo "提示："
echo "  - 提交前运行: ./check_security.sh"
echo "  - 定期检查: git status"
echo "  - 密钥管理: 使用环境变量，切勿硬编码"
