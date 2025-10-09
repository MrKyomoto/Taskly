from datetime import datetime
from app.extensions import db
from app.models import (
    Homework,
    HomeworkSubmission,
    Student,
    StudentCourseRelation,
    Course
)
import json
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
    """
    获取学生已选课程的所有作业
    :param student_id: 学生ID
    :param course_id: 课程ID
    :return: (success, data/error_msg) 成功时返回作业列表，失败时返回错误信息
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return False, "学生不存在"

        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        enrollment = StudentCourseRelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        if not enrollment:
            return False, "未在该班级课程中,无法查看作业"

        homeworks = Homework.query.filter_by(
            course_id=course_id
        ).order_by(
            Homework.deadline.asc()
        ).all()

        homework_list = []
        for hw in homeworks:
            is_overdue = datetime.utcnow() > hw.deadline if hw.deadline else False

            homework_list.append({
                "id": hw.id,
                "title": hw.title,
                "content": hw.content,
                "image_urls": hw.image_urls,  # NOTE: frontend should parse the json str into array
                "type": hw.type.value if hw.type else None,
                "deadline": hw.deadline.isoformat() if hw.deadline else None,
                "create_time": hw.create_time.isoformat() if hw.create_time else None,
                "is_overdue": is_overdue,
            })

        return True, homework_list

    except Exception as e:
        db.session.rollback()
        return False, f"获取作业失败:{str(e)}"


def submit_homework(student_id, homework_id, text_content, image_urls):
    """
    提交学生作业
    :param student_id: 学生ID
    :param homework_id: 作业ID
    :param text_content: 文本内容
    :param image_urls: 图片URL列表
    :return: (success, message)
    """
    homework = Homework.query.get(homework_id)
    if not homework:
        return False, "作业不存在"

    course_id = homework.course_id
    has_enrolled = StudentCourseRelation.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()
    if not has_enrolled:
        return False, "未在该班级课程中,无权提交作业"

    existing_submission = HomeworkSubmission.query.filter_by(
        student_id=student_id,
        homework_id=homework_id
    ).first()

    image_urls_json = json.dumps(image_urls) if image_urls else None

    try:
        if existing_submission:
            existing_submission.text_content = text_content
            existing_submission.image_urls = image_urls_json
            existing_submission.submit_time = datetime.utcnow()
            existing_submission.is_graded = False
            message = "作业重新提交成功"
        else:
            new_submission = HomeworkSubmission(
                homework_id=homework_id,
                student_id=student_id,
                text_content=text_content,
                image_urls=image_urls_json,
                submit_time=datetime.utcnow(),
                is_graded=False
            )
            db.session.add(new_submission)
            message = "作业提交成功"

        db.session.commit()
        return True, message
    except Exception as e:
        db.session.rollback()
        return False, f"提交失败:{str(e)}"
