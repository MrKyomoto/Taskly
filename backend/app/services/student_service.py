# 模拟数据存储
mock_students = {
    1: {
        "id": 1,
        "student_no": "S2023001",
        "name": "张三",
        "password": "password123",  # MVP阶段使用明文，实际应哈希存储
        "email": "zhangsan@example.com",
        "phone": "13800138000"
    }
}

mock_courses = {
    1: {
        "id": 1,
        "code": "CS101",
        "name": "计算机基础",
        "description": "计算机入门课程"
    },
    2: {
        "id": 2,
        "code": "MA101",
        "name": "高等数学",
        "description": "大学数学基础"
    }
}

# 学生选课关系 (student_id: list of course_ids)
mock_enrollments = {
    1: [1, 2]
}


def authenticate_student(student_no, password):
    """验证学生身份"""
    for student in mock_students.values():
        if student["student_no"] == student_no and student["password"] == password:
            return student
    return None


def get_student(student_id):
    """根据ID获取学生信息"""
    return mock_students.get(student_id)


def get_student_courses(student_id):
    """获取学生已选课程"""
    if student_id not in mock_enrollments:
        return []

    course_ids = mock_enrollments[student_id]
    return [mock_courses[id] for id in course_ids if id in mock_courses]


def enroll_student_in_course(student_id, course_code):
    """学生选课"""
    # 查找课程
    course = next((c for c in mock_courses.values()
                  if c["code"] == course_code), None)
    if not course:
        return False, "课程不存在"

    # 初始化学生选课列表（如果不存在）
    if student_id not in mock_enrollments:
        mock_enrollments[student_id] = []

    # 检查是否已选该课程
    if course["id"] in mock_enrollments[student_id]:
        return False, "已选该课程"

    # 执行选课
    mock_enrollments[student_id].append(course["id"])
    return True, "选课成功"


def get_student_course_homeworks(student_id, course_id):
    return True
