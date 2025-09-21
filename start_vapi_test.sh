#!/bin/bash

echo "🚀 Starting VAPI Phone Call Testing Setup"
echo "=========================================="

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend not running. Starting backend..."
    python3 test_server.py &
    sleep 3
    echo "✅ Backend started"
else
    echo "✅ Backend already running"
fi

# Check if ngrok is running
if ! curl -s http://localhost:4040/api/tunnels > /dev/null; then
    echo "❌ ngrok not running. Please start ngrok in another terminal:"
    echo "   ngrok http 8000"
    echo ""
    echo "Then copy the https URL and update your VAPI webhook to:"
    echo "   https://YOUR_NGROK_URL.ngrok.io/webhooks/vapi"
else
    echo "✅ ngrok is running"
    # Get ngrok URL
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'])" 2>/dev/null)
    echo "🌐 Your ngrok URL: $NGROK_URL"
    echo "🔗 VAPI Webhook URL: $NGROK_URL/webhooks/vapi"
fi

echo ""
echo "📞 Ready for phone call testing!"
echo "1. Update VAPI webhook URL to: https://YOUR_NGROK_URL.ngrok.io/webhooks/vapi"
echo "2. Make a test call to your assistant"
echo "3. Check the backend logs for webhook data"

