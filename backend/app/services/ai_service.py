"""
AI 辅助批改服务
"""
import json
import os


def generate_ai_feedback(text_content, image_urls=None):
    """
    生成 AI 批改反馈
    :param text_content: 学生作业文本内容
    :param image_urls: 学生作业图片/PDF URL列表
    :return: (success, result) 成功返回 {"score": int, "feedback": str}，失败返回错误信息
    """
    try:
        # 检查是否有配置 API Key
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('DEEPSEEK_API_KEY') or os.getenv('KIMI_API_KEY')
        
        if not api_key:
            # 如果没有配置 API Key，返回模拟数据用于测试
            return True, generate_mock_feedback(text_content, image_urls or [])
        
        # TODO: 实际调用大模型 API
        # 这里可以根据配置选择不同的模型（OpenAI/DeepSeek/Kimi）
        # 暂时返回模拟数据
        return True, generate_mock_feedback(text_content, image_urls or [])
        
    except Exception as e:
        return False, f"AI 批改失败：{str(e)}"


def generate_mock_feedback(text_content, image_urls=None):
    """
    生成模拟的批改反馈（用于测试）
    :param text_content: 学生作业文本内容
    :param image_urls: 学生作业图片/PDF URL列表
    :return: {"score": int, "feedback": str}
    """
    # 检查是否有PDF文件
    has_pdf = False
    if image_urls:
        for url in image_urls:
            url_str = str(url).lower()
            if url_str.endswith('.pdf') or '.pdf' in url_str:
                has_pdf = True
                break
    
    # 简单的评分逻辑（模拟）
    text_length = len(text_content.strip()) if text_content else 0
    has_images = image_urls and len(image_urls) > 0
    
    # 根据文本长度、图片/PDF数量和质量评分（简单模拟）
    if has_pdf:
        # 有PDF文件，基础分数较高
        if text_length > 0:
            score = 85
            feedback = "作业包含PDF文件和文本内容，内容较为完整。建议在PDF中标注重点，并补充更多文字说明。"
        else:
            score = 80
            feedback = "作业包含PDF文件，但缺少文字说明。建议补充文字描述，说明PDF中的关键内容。"
    elif has_images:
        # 有图片文件
        if text_length > 0:
            score = 80
            feedback = "作业包含图片和文本内容，内容基本完整。建议补充更多文字说明，并确保图片清晰可读。"
        else:
            score = 75
            feedback = "作业包含图片，但缺少文字说明。建议补充文字描述，说明图片中的关键内容。"
    elif text_length < 50:
        score = 60
        feedback = "作业内容较为简短，建议补充更多细节和深入分析。"
    elif text_length < 200:
        score = 75
        feedback = "作业内容基本完整，但可以进一步展开论述，增加实例和论证。"
    elif text_length < 500:
        score = 85
        feedback = "作业内容较为充实，逻辑清晰，但仍有改进空间，可以增加更多创新观点。"
    else:
        score = 90
        feedback = "作业内容丰富，论述充分，逻辑清晰，表现优秀。建议继续保持，并尝试从更多角度思考问题。"
    
    return {
        "score": score,
        "feedback": feedback
    }


def call_openai_api(text_content, api_key):
    """
    调用 OpenAI API（示例，需要根据实际情况实现）
    """
    # TODO: 实现 OpenAI API 调用
    # import openai
    # openai.api_key = api_key
    # response = openai.ChatCompletion.create(...)
    pass


def call_deepseek_api(text_content, api_key):
    """
    调用 DeepSeek API（示例，需要根据实际情况实现）
    """
    # TODO: 实现 DeepSeek API 调用
    pass


def call_kimi_api(text_content, api_key):
    """
    调用 Kimi API（示例，需要根据实际情况实现）
    """
    # TODO: 实现 Kimi API 调用
    pass

