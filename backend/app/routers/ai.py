"""
AI 辅助批改路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.util.parse_identity import parse_identity

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/generate-feedback', methods=['POST'])
@jwt_required()
def generate_feedback():
    """生成 AI 批改反馈（仅限教师和助教）"""
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400

    text_content = data.get('text_content', '')
    image_urls = data.get('image_urls', [])
    
    # 检查是否有内容：文本、图片或PDF任一不为空即可
    has_text = text_content and text_content.strip()
    has_images = image_urls and len(image_urls) > 0
    
    if not has_text and not has_images:
        return jsonify({"error": "提交内容不能为空，请至少包含文本、图片或PDF中的一种"}), 400

    from app.handlers.ai_handler import handle_generate_feedback
    return handle_generate_feedback(text_content, image_urls)


