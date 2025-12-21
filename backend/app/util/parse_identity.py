from flask import jsonify


def parse_identity(identity_str, expected_role=None):
    """
    解析JWT中的identity字符串（格式："role:id"）

    参数：
        identity_str: 从get_jwt_identity()获取的字符串
        expected_role: 期望的角色（如"student", "teacher", "staff"等，可选）
                      "staff" 表示支持 teacher 和 ta 两种角色

    返回：
        成功：(user_id, None) 元组
        失败：(None, error_response) 元组（error_response为Flask响应对象）
    """
    try:
        # 拆分角色和ID
        role, id_str = identity_str.split(':', 1)
        user_id = int(id_str)

        # 校验角色（如果指定了期望角色）
        if expected_role:
            if expected_role == "staff":
                # staff 表示支持 teacher 和 ta
                if role not in ["teacher", "ta"]:
                    return None, jsonify({"error": "仅教师或助教可访问"}), 403
            elif expected_role == "student_or_ta":
                # student_or_ta 表示支持 student 和 ta（助教也是学生）
                if role not in ["student", "ta"]:
                    return None, jsonify({"error": "仅学生或助教可访问"}), 403
            elif role != expected_role:
                return None, jsonify({"error": f"仅{expected_role}可访问"}), 403

        return user_id, None

    except (ValueError, TypeError):
        # 处理格式错误（如没有冒号、ID不是数字等）
        return None, jsonify({"error": "无效的身份信息"}), 401
