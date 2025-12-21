"""
AI 辅助批改处理器
"""
from flask import jsonify
from app.services.ai_service import generate_ai_feedback


def handle_generate_feedback(text_content, image_urls=None):
    """处理 AI 生成反馈请求"""
    try:
        success, result = generate_ai_feedback(text_content, image_urls or [])
        if success:
            return jsonify(result), 200
        return jsonify({"error": result}), 400
    except Exception as e:
        return jsonify({"error": f"AI 批改失败：{str(e)}"}), 500


