#!/usr/bin/env python3
"""
ClickUp Webhook 飞书通知 - Vercel Serverless 版本
"""

import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# 环境变量（在 Vercel 后台配置）
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL", "")
YOUR_USER_ID = os.getenv("YOUR_USER_ID", "132200511")

def send_feishu(title, content, url=""):
    """发送飞书卡片通知"""
    if not FEISHU_WEBHOOK_URL:
        print("未配置飞书 webhook")
        return False

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "red"
            },
            "elements": [{"tag": "markdown", "content": content}]
        }
    }

    if url:
        card["card"]["elements"].append({
            "tag": "action",
            "actions": [{
                "tag": "button",
                "text": {"tag": "plain_text", "content": "查看任务"},
                "type": "primary",
                "url": url
            }]
        })

    import requests
    try:
        r = requests.post(FEISHU_WEBHOOK_URL, json=card, timeout=10)
        print(f"飞书通知发送结果: {r.status_code}")
        return True
    except Exception as e:
        print(f"发送失败: {e}")
        return False

@app.route("/", methods=["POST"])
def handle_webhook():
    """处理 ClickUp Webhook"""
    payload = request.json
    event = payload.get("event", "")
    task = payload.get("task", {})

    print(f"收到事件: {event}")

    if event == "taskCommentPosted":
        history_items = payload.get("history_items", [])
        for item in history_items:
            if item.get("field") == "comment":
                after = item.get("after", {})
                mentions = after.get("mentions", [])

                for mention in mentions:
                    if str(mention.get("id")) == YOUR_USER_ID:
                        title = "📢 你被 @ 了！"
                        content = f"**任务**: {task.get('name')}\n**评论**: {after.get('text', '')}"
                        send_feishu(title, content, task.get("url", ""))
                        return jsonify({"status": "ok", "mentioned": True})

    elif event == "taskAssigneeUpdated":
        history_items = payload.get("history_items", [])
        for item in history_items:
            if "assignee" in item.get("field", ""):
                after = item.get("after", {})
                if str(after.get("id")) == YOUR_USER_ID:
                    title = "📋 任务被分配给你"
                    content = f"**任务**: {task.get('name')}\n**分配人**: {after.get('username', '')}"
                    send_feishu(title, content, task.get("url", ""))
                    return jsonify({"status": "ok", "assigned": True})

    return jsonify({"status": "ok"})

# Vercel 入口
def handler(environ, start_response):
    return app(environ, start_response)
