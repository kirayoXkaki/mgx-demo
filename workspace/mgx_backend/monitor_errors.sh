#!/bin/bash
# 只监控错误和异常的日志

LOG_FILE="/Users/jianzhixu/Desktop/mgx/metadev/workspace/mgx_backend/api.log"

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}=== ⚠️  错误和异常监控 ===${NC}"
echo ""

if [ ! -f "$LOG_FILE" ]; then
    echo "日志文件不存在: $LOG_FILE"
    exit 1
fi

echo "只显示 ERROR、EXCEPTION、TRACEBACK、FAILED 等关键词"
echo "按 Ctrl+C 退出"
echo ""

tail -f "$LOG_FILE" | grep --color=always -i -E "error|exception|traceback|failed|critical|fatal"

