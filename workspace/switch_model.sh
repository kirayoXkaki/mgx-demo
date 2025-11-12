#!/bin/bash
# 快速切换 LLM 模型的脚本

MODEL=$1

if [ -z "$MODEL" ]; then
    echo "用法: ./switch_model.sh <model_name>"
    echo ""
    echo "可用模型:"
    echo "  gpt-4o          - 最新最强模型（推荐）"
    echo "  gpt-4-turbo    - 当前默认模型"
    echo "  gpt-4          - 经典模型"
    echo "  gpt-3.5-turbo  - 经济型"
    echo "  gpt-5          - 如果可用"
    echo ""
    echo "示例: ./switch_model.sh gpt-4o"
    exit 1
fi

cd "$(dirname "$0")/mgx_backend"

if [ ! -f ".env" ]; then
    echo "❌ 错误: .env 文件不存在"
    exit 1
fi

# 备份原配置
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 更新模型配置
if grep -q "^OPENAI_MODEL=" .env; then
    sed -i '' "s/^OPENAI_MODEL=.*/OPENAI_MODEL=$MODEL/" .env
else
    echo "OPENAI_MODEL=$MODEL" >> .env
fi

echo "✅ 已将模型切换为: $MODEL"
echo ""
echo "当前配置:"
grep OPENAI_MODEL .env
echo ""
echo "⚠️  请重启后端服务以应用新配置:"
echo "  ./stop_backend.sh"
echo "  ./start_backend.sh"

