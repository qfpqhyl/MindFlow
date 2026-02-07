#!/bin/bash

API_KEY="$1"

if [ -z "$API_KEY" ]; then
    echo "❌ 请提供 API Key"
    echo "用法: bash test_minimax.sh YOUR_API_KEY"
    exit 1
fi

echo "========================================="
echo "测试 MiniMax M2.1 模型"
echo "========================================="
echo ""
echo "API Key: ${API_KEY:0:15}...${API_KEY: -4}"
echo ""

echo "📡 发送请求到 NVIDIA API..."
echo "URL: https://integrate.api.nvidia.com/v1/chat/completions"
echo "模型: minimaxai/minimax-m2.1"
echo ""

# 使用 curl 添加详细输出和超时设置
echo "⏱️  请求中...（最长等待30秒）"
echo ""

RESPONSE=$(curl -s --max-time 30 \
  -X POST \
  "https://integrate.api.nvidia.com/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimaxai/minimax-m2.1",
    "messages": [
      {
        "role": "user",
        "content": "你好"
      }
    ],
    "max_tokens": 50
  }')

CURL_EXIT_CODE=$?

echo ""
echo "========================================="
echo "curl 退出码: $CURL_EXIT_CODE"
echo "========================================="
echo ""

if [ $CURL_EXIT_CODE -eq 28 ]; then
    echo "❌ 请求超时（30秒）"
    echo ""
    echo "可能的原因:"
    echo "  1. 网络连接问题"
    echo "  2. NVIDIA API 响应慢"
    echo "  3. 防火墙阻止了连接"
    echo ""
    echo "建议:"
    echo "  - 检查网络连接"
    echo "  - 尝试使用 VPN"
    echo "  - 稍后再试"
    exit 1
elif [ $CURL_EXIT_CODE -ne 0 ]; then
    echo "❌ 请求失败，退出码: $CURL_EXIT_CODE"
    echo ""
    echo "详细输出:"
    echo "$RESPONSE"
    exit 1
fi

# 检查响应是否为空
if [ -z "$RESPONSE" ]; then
    echo "❌ 响应为空"
    echo ""
    echo "服务器没有返回任何数据"
    exit 1
fi

# 尝试解析 JSON
echo "$RESPONSE" | python3 -m json.tool > /tmp/minimax_response.json 2>&1
JSON_VALID=$?

if [ $JSON_VALID -eq 0 ]; then
    # 检查是否有错误
    if echo "$RESPONSE" | grep -q '"error"'; then
        echo "❌ API 返回错误"
        echo ""
        python3 -c "import sys,json; data=json.load(sys.stdin); print('错误信息:', data.get('error', {}).get('message', 'Unknown error'))" < /tmp/minimax_response.json
        exit 1
    fi
    
    # 提取内容
    CONTENT=$(python3 -c "import sys,json; data=json.load(sys.stdin); print(data['choices'][0]['message']['content'])" < /tmp/minimax_response.json 2>/dev/null)
    
    if [ -n "$CONTENT" ]; then
        echo "✅ 请求成功！"
        echo ""
        echo "📝 AI 回复:"
        echo "========================================="
        echo "$CONTENT"
        echo "========================================="
    else
        echo "⚠️  响应格式异常"
        cat /tmp/minimax_response.json
    fi
else
    echo "⚠️  响应不是有效的 JSON"
    echo ""
    echo "原始响应（前500字符）:"
    echo "========================================="
    echo "$RESPONSE" | head -c 500
    echo "========================================="
fi

