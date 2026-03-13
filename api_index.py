#!/usr/bin/env python3
"""
ClickUp Webhook - Vercel Serverless (无 Flask)
"""

import json
import os

def handler(request):
    """Vercel Serverless Handler"""
    
    # 解析请求体
    try:
        body = json.loads(request.body) if hasattr(request, 'body') else {}
    except:
        body = {}
    
    event = body.get("event", "")
    print(f"收到 ClickUp Webhook: {event}")
    
    # 返回 200 OK
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "ok", "event": event})
    }
