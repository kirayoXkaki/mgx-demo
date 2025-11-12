#!/bin/bash
# 实时监控后端日志脚本

LOG_FILE="/Users/jianzhixu/Desktop/mgx/metadev/workspace/mgx_backend/api.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 🔍 MGX 后端日志实时监控 ===${NC}"
echo ""

if [ ! -f "$LOG_FILE" ]; then
    echo -e "${YELLOW}⚠️  日志文件不存在: $LOG_FILE${NC}"
    echo ""
    echo "请先启动后端服务。"
    exit 1
fi

echo -e "${GREEN}📋 日志文件: $LOG_FILE${NC}"
echo -e "${GREEN}📊 文件大小: $(ls -lh "$LOG_FILE" | awk '{print $5}')${NC}"
echo ""
echo -e "${YELLOW}💡 提示: 按 Ctrl+C 退出监控${NC}"
echo -e "${YELLOW}💡 过滤选项:${NC}"
echo "   - 只看错误: grep --color=always -i 'error\\|exception\\|traceback' | tail -f"
echo "   - 只看警告: grep --color=always -i 'warning' | tail -f"
echo "   - 只看请求: grep --color=always -i 'GET\\|POST\\|PUT\\|DELETE' | tail -f"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 实时监控日志，高亮显示重要信息
tail -f "$LOG_FILE" | while IFS= read -r line; do
    # 高亮错误
    if echo "$line" | grep -qi "error\|exception\|traceback\|failed"; then
        echo -e "${RED}$line${NC}"
    # 高亮警告
    elif echo "$line" | grep -qi "warning"; then
        echo -e "${YELLOW}$line${NC}"
    # 高亮成功/启动信息
    elif echo "$line" | grep -qi "started\|complete\|success\|200\|201"; then
        echo -e "${GREEN}$line${NC}"
    # 普通信息
    else
        echo "$line"
    fi
done

