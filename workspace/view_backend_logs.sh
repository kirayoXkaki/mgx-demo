#!/bin/bash
# 实时查看后端日志

LOG_FILE="mgx_backend/api.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "⚠️  日志文件不存在: $LOG_FILE"
    echo ""
    echo "请先启动后端服务："
    echo "  ./start_backend.sh"
    exit 1
fi

echo "📋 实时查看后端日志 (按 Ctrl+C 退出)"
echo "日志文件: $LOG_FILE"
echo "文件大小: $(ls -lh "$LOG_FILE" | awk '{print $5}')"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

tail -f "$LOG_FILE"

