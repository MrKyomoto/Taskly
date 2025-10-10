from datetime import datetime
from app.extensions import db
from app.models import (
    Homework,
    HomeworkSubmission,
    Student,
    StudentCourseRelation,
    Course,
    CourseStatus
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
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
    """
    验证学生身份（统一返回格式：(success, data/error_msg)）
    :param student_no: 学号
    :param password: 明文密码
    :return: 成功时返回 (True, 学生信息字典)，失败时返回 (False, 错误信息)
    """
    try:
        student = Student.query.filter_by(student_no=student_no).first()
        if not student:
            return False, "学号或密码错误"  # 不暴露"学生不存在"，防止信息泄露

        if not check_password_hash(student.password, password):
            return False, "学号或密码错误"  # 统一错误提示

        # 3. 验证成功，返回学生信息（不含敏感字段）
        student_data = {
            "id": student.id,
            "student_no": student.student_no,
            "name": student.name,
            "email": student.email,
            "phone": student.phone
        }
        return True, student_data

    except Exception as e:
        db.session.rollback()
        return False, f"身份验证失败：{str(e)}"


def register_student(student_data):
    """
    学生注册服务
    :param student_data: 包含注册信息的字典（student_no, name, password, email, phone）
    :return: (success, data/error_msg) 成功返回学生信息，失败返回错误信息
    """
    required_fields = ["student_no", "name", "password"]
    # 校验必填字段
    for field in required_fields:
        if not student_data.get(field):
            return False, f"缺少必填字段：{field}"

    student_no = student_data["student_no"]
    name = student_data["name"]
    password = student_data["password"]
    email = student_data.get("email", "")
    phone = student_data.get("phone", "")

    try:
        existing_student = Student.query.filter_by(
            student_no=student_no).first()
        if existing_student:
            return False, "该学号已注册"

        hashed_password = generate_password_hash(password)

        new_student = Student(
            student_no=student_no,
            name=name,
            password=hashed_password,
            email=email,
            phone=phone
        )
        db.session.add(new_student)
        db.session.commit()

        return True, {
            "id": new_student.id,
            "student_no": new_student.student_no,
            "name": new_student.name,
            "email": new_student.email,
            "phone": new_student.phone
        }

    except Exception as e:
        db.session.rollback()
        return False, f"注册失败：{str(e)}"


def get_student(student_id):
    """
    根据ID获取学生信息（从数据库查询）
    :param student_id: 学生ID
    :return: (success, data/error_msg) 成功时返回学生信息字典，失败时返回错误信息
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return False, "学生不存在"

        student_data = {
            "id": student.id,
            "student_no": student.student_no,
            "name": student.name,
            "email": student.email,
            "phone": student.phone,
            "create_time": student.create_time.isoformat() if student.create_time else None
        }

        return True, student_data

    except Exception as e:
        db.session.rollback()
        return False, f"获取学生信息失败：{str(e)}"


def update_student_profile(student_id, update_data):
    """
    更新学生个人资料
    :param student_id: 学生ID
    :param update_data: 待更新的字段字典（支持name/email/phone）
    :return: (success, data/error_msg) 成功返回更新后的信息，失败返回错误信息
    """
    # 允许修改的字段（限制范围，防止恶意更新）
    allowed_fields = ["name", "email", "phone"]
    # 过滤无效字段
    valid_data = {k: v for k, v in update_data.items() if k in allowed_fields}

    if not valid_data:
        return False, "没有可更新的有效字段（支持：姓名/邮箱/电话）"

    try:
        # 查询学生是否存在
        student = Student.query.get(student_id)
        if not student:
            return False, "学生不存在"

        # 更新字段
        for field, value in valid_data.items():
            setattr(student, field, value)  # 动态设置属性

        db.session.commit()

        # 返回更新后的非敏感信息
        return True, {
            "id": student.id,
            "student_no": student.student_no,  # 学号不允许修改，仍返回当前值
            "name": student.name,
            "email": student.email,
            "phone": student.phone
        }

    except Exception as e:
        db.session.rollback()
        return False, f"更新资料失败：{str(e)}"


def update_student_password(student_id, old_password, new_password):
    """
    修改学生密码
    :param student_id: 学生ID
    :param old_password: 原密码（明文）
    :param new_password: 新密码（明文）
    :return: (success, error_msg) 成功返回(True, "")，失败返回(False, 错误信息)
    """
    # 密码强度校验
    if len(new_password) < 8:
        return False, "新密码长度不能少于8位"
    if old_password == new_password:
        return False, "新密码不能与原密码相同"

    try:
        student = Student.query.get(student_id)
        if not student:
            return False, "学生不存在"

        # 验证原密码（注意：实际项目中数据库存储的是哈希值）
        if not check_password_hash(student.password, old_password):
            return False, "原密码验证失败"

        student.password = generate_password_hash(new_password)
        db.session.commit()
        return True, ""

    except Exception as e:
        db.session.rollback()
        return False, f"密码更新失败：{str(e)}"


def get_student_courses(student_id):
    """
    获取学生已选课程列表（从数据库查询）
    :param student_id: 学生ID
    :return: (success, data/error_msg) 成功时返回课程列表，失败时返回错误信息
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return False, "学生不存在"

        # NOTE: 通过 StudentCourseRelation 关联查询该学生已选择的所有课程,同时获取选课的时间
        enrolled_courses = db.session.query(
            Course, StudentCourseRelation.enroll_time
        ).join(
            StudentCourseRelation,
            Course.id == StudentCourseRelation.course_id
        ).filter(
            StudentCourseRelation.student_id == student_id
        ).all()

        course_list = []
        for course, enroll_time in enrolled_courses:
            course_list.append({
                "id": course.id,
                "course_code": course.course_code,
                "course_name": course.course_name,
                "description": course.description,
                "semester": course.semester,
                "status": course.status.value if course.status else None,
                "enroll_time": enroll_time.isoformat() if enroll_time else None
            })

        return True, course_list
    except Exception as e:
        db.session.rollback()
        return False, f"获取课程失败:{str(e)}"


def enroll_course(student_id, course_code):
    """
    学生选课功能（基于数据库操作）
    :param student_id: 学生ID
    :param course_code: 课程代码（如"CS101"）
    :return: (success, message) 成功时返回True和成功消息，失败时返回False和错误信息
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return False, "学生不存在"

        course = Course.query.filter_by(course_code=course_code).first()
        if not course:
            return False, "课程不存在"

        if course.status != CourseStatus.approved:
            return False, f"课程状态为{course.status.value}，无法选课"

        existing_relation = StudentCourseRelation.query.filter_by(
            student_id=student_id,
            course_id=course.id
        ).first()
        if existing_relation:
            return False, "已选修该课程，无需重复选课"

        new_enrollment = StudentCourseRelation(
            student_id=student_id,
            course_id=course.id,
            enroll_time=datetime.utcnow()
        )
        db.session.add(new_enrollment)
        db.session.commit()

        return True, f"成功选修课程: {course.course_name}"

    except Exception as e:
        db.session.rollback()
        return False, f"选课失败：{str(e)}"


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


def get_student_homework_submission(student_id, course_id, homework_id):
    """
    获取学生在某课程中某作业的提交内容
    :param student_id: 学生ID
    :param course_id: 课程ID（用于权限校验）
    :param homework_id: 作业ID
    :return: (success, data/error_msg) 成功返回提交内容，失败返回错误信息
    """
    try:
        is_enrolled = StudentCourseRelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        if not is_enrolled:
            return False, "未选修该课程，无权限查看"

        # 2. 校验作业是否属于该课程
        homework = Homework.query.filter_by(
            id=homework_id,
            course_id=course_id
        ).first()
        if not homework:
            return False, "该课程下无此作业"

        # 3. 查询学生的提交记录
        submission = HomeworkSubmission.query.filter_by(
            student_id=student_id,
            homework_id=homework_id
        ).first()

        if not submission:
            return False, "未提交该作业"

        # 4. 处理图片URL（将相对路径转为可访问URL）
        image_urls = []
        if submission.image_urls:
            import json
            # 数据库存储的是JSON字符串，需解析
            relative_paths = json.loads(submission.image_urls)
            for path in relative_paths:
                image_urls.append({
                    "image_url": path
                })

        # 5. 构造返回数据
        return True, {
            "id": submission.id,
            "homework_id": submission.homework_id,
            "text_content": submission.text_content,
            "image_urls": image_urls,
            "submit_time": submission.submit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_graded": submission.is_graded
        }

    except Exception as e:
        return False, f"获取提交内容失败：{str(e)}"


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
