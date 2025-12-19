"""
AI 辅助批改服务
"""
import json
import os


def generate_ai_feedback(text_content):
    """
    生成 AI 批改反馈
    :param text_content: 学生作业文本内容
    :return: (success, result) 成功返回 {"score": int, "feedback": str}，失败返回错误信息
    """
    try:
        # 检查是否有配置 API Key
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('DEEPSEEK_API_KEY') or os.getenv('KIMI_API_KEY')
        
        if not api_key:
            # 如果没有配置 API Key，返回模拟数据用于测试
            return True, generate_mock_feedback(text_content)
        
        # TODO: 实际调用大模型 API
        # 这里可以根据配置选择不同的模型（OpenAI/DeepSeek/Kimi）
        # 暂时返回模拟数据
        return True, generate_mock_feedback(text_content)
        
    except Exception as e:
        return False, f"AI 批改失败：{str(e)}"


def generate_mock_feedback(text_content):
    """
    生成模拟的批改反馈（用于测试）
    :param text_content: 学生作业文本内容
    :return: {"score": int, "feedback": str}
    """
    # 简单的评分逻辑（模拟）
    text_length = len(text_content.strip())
    
    # 根据文本长度和内容质量评分（简单模拟）
    if text_length < 50:
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

