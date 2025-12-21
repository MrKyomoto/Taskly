from datetime import datetime
from app.extensions import db
from app.models import (
    Homework,
    HomeworkSubmission,
    Student,
    StudentCourseRelation,
    StudentTARelation,
    Course,
    CourseStatus,
    StaffRole
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)
import json
import re


def validate_password_strength(password):
    """
    验证密码强度
    密码长度必须不少于 6 位
    密码必须包含字母、数字、特殊字符这三类中的至少两类
    :param password: 明文密码
    :return: (is_valid, error_msg) 有效返回(True, "")，无效返回(False, 错误信息)
    """
    if len(password) < 6:
        return False, "密码长度不能少于6位"
    
    # 检查是否包含字母、数字、特殊字符
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password))
    
    # 统计包含的字符类型数量
    type_count = sum([has_letter, has_digit, has_special])
    
    if type_count < 2:
        return False, "密码必须包含字母、数字、特殊字符这三类中的至少两类"
    
    return True, ""


def validate_phone_format(phone):
    """
    验证手机号格式
    接收包含区号的完整手机号字符串（如 +86138...）
    :param phone: 完整手机号字符串
    :return: (is_valid, error_msg) 有效返回(True, "")，无效返回(False, 错误信息)
    """
    if not phone or not isinstance(phone, str):
        return False, "手机号不能为空"
    
    phone = phone.strip()
    
    # 验证格式：+号开头，后面跟数字，总长度合理（+86 + 11位 = 14位，其他区号可能不同）
    # 支持常见格式：+86xxxxxxxxxxx, +1xxxxxxxxxx 等
    phone_pattern = r'^\+\d{10,15}$'
    
    if not re.match(phone_pattern, phone):
        return False, "手机号格式不正确，应为+号开头的国际格式（如：+8613812345678）"
    
    # 特别校验中国手机号（+86开头，后面11位数字）
    if phone.startswith('+86'):
        if len(phone) != 14:  # +86 + 11位数字 = 14位
            return False, "中国手机号应为+86开头后跟11位数字"
        if not re.match(r'^\+86[1-9]\d{10}$', phone):
            return False, "中国手机号格式不正确，应为+86开头后跟11位有效数字"
    
    return True, ""


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

        if not check_password_hash(student.password_hash, password):
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
    required_fields = ["student_no", "name", "password", "email", "phone"]
    # 校验必填字段
    for field in required_fields:
        if not student_data.get(field):
            return False, f"缺少必填字段：{field}"

    student_no = student_data["student_no"]
    name = student_data["name"]
    password = student_data["password"]
    email = student_data["email"]
    phone = student_data["phone"]

    # 密码强度校验
    is_valid, error_msg = validate_password_strength(password)
    if not is_valid:
        return False, error_msg

    # 手机号格式校验
    is_valid, error_msg = validate_phone_format(phone)
    if not is_valid:
        return False, error_msg

    try:
        existing_student = Student.query.filter_by(
            student_no=student_no).first()
        if existing_student:
            return False, "该学号已注册"

        hashed_password = generate_password_hash(password)

        new_student = Student(
            student_no=student_no,
            name=name,
            password_hash=hashed_password,
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

        # 如果更新手机号，先校验格式
        if 'phone' in valid_data:
            is_valid, error_msg = validate_phone_format(valid_data['phone'])
            if not is_valid:
                return False, error_msg

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
    is_valid, error_msg = validate_password_strength(new_password)
    if not is_valid:
        return False, error_msg
    
    if old_password == new_password:
        return False, "新密码不能与原密码相同"

    try:
        student = Student.query.get(student_id)
        if not student:
            return False, "学生不存在"

        # 验证原密码（注意：实际项目中数据库存储的是哈希值）
        if not check_password_hash(student.password_hash, old_password):
            return False, "原密码验证失败"

        student.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True, ""

    except Exception as e:
        db.session.rollback()
        return False, f"密码更新失败：{str(e)}"


def reset_student_password_by_student_no(student_no, old_password, new_password):
    """
    通过学号重置学生密码（用于登录界面）
    :param student_no: 学号
    :param old_password: 原密码（明文）
    :param new_password: 新密码（明文）
    :return: (success, error_msg) 成功返回(True, "")，失败返回(False, 错误信息)
    """
    # 密码强度校验
    is_valid, error_msg = validate_password_strength(new_password)
    if not is_valid:
        return False, error_msg
    
    if old_password == new_password:
        return False, "新密码不能与原密码相同"

    try:
        student = Student.query.filter_by(student_no=student_no).first()
        if not student:
            return False, "学号不存在"

        # 验证原密码
        if not check_password_hash(student.password_hash, old_password):
            return False, "原密码验证失败"

        student.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True, ""

    except Exception as e:
        db.session.rollback()
        return False, f"密码更新失败：{str(e)}"


def check_student_identifier(identifier):
    """
    检查学号是否存在
    :param identifier: 学号
    :return: (success, result) 成功返回(True, {"user_id": id})，失败返回(False, 错误信息)
    """
    try:
        student = Student.query.filter_by(student_no=identifier).first()
        if not student:
            return False, "学号不存在"
        return True, {"user_id": student.id}
    except Exception as e:
        return False, f"查询失败：{str(e)}"


def verify_student_contact(user_id, contact, method):
    """
    验证学生的邮箱或电话是否匹配
    :param user_id: 学生ID
    :param contact: 邮箱或电话
    :param method: 'email' 或 'phone'
    :return: (success, error_msg) 成功返回(True, "")，失败返回(False, 错误信息)
    """
    try:
        student = Student.query.get(user_id)
        if not student:
            return False, "学生不存在"
        
        if method == 'email':
            if student.email != contact:
                return False, "邮箱不匹配，请输入注册时填写的邮箱"
        elif method == 'phone':
            if student.phone != contact:
                return False, "电话不匹配，请输入注册时填写的电话"
        else:
            return False, "无效的验证方式"
        
        return True, ""
    except Exception as e:
        return False, f"验证失败：{str(e)}"


def reset_student_password_with_verification(user_id, verification_code, new_password, stored_code):
    """
    通过验证码重置学生密码
    :param user_id: 学生ID
    :param verification_code: 用户输入的验证码
    :param new_password: 新密码（明文）
    :param stored_code: 存储的验证码
    :return: (success, error_msg) 成功返回(True, "")，失败返回(False, 错误信息)
    """
    # 验证验证码
    if verification_code != stored_code:
        return False, "验证码错误"
    
    # 密码强度校验
    is_valid, error_msg = validate_password_strength(new_password)
    if not is_valid:
        return False, error_msg
    
    try:
        student = Student.query.get(user_id)
        if not student:
            return False, "学生不存在"
        
        student.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True, ""
    except Exception as e:
        db.session.rollback()
        return False, f"密码重置失败：{str(e)}"


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

        # 同时查询该学生作为助教的课程（通过 StudentTARelation）
        ta_courses = db.session.query(
            Course, StudentTARelation.create_time
        ).join(
            StudentTARelation,
            Course.id == StudentTARelation.course_id
        ).filter(
            StudentTARelation.student_id == student_id
        ).all()

        # 合并课程列表，避免重复
        course_dict = {}
        for course, enroll_time in enrolled_courses:
            course_dict[course.id] = {
                'course': course,
                'enroll_time': enroll_time,
                'is_ta': False
            }
        
        # 添加助教课程（如果不在已选课程列表中）
        for course, create_time in ta_courses:
            if course.id not in course_dict:
                course_dict[course.id] = {
                    'course': course,
                    'enroll_time': create_time,
                    'is_ta': True
                }

        course_list = []
        for course_id, course_data in course_dict.items():
            course = course_data['course']
            enroll_time = course_data['enroll_time']
            is_ta = course_data['is_ta']
            
            # 查询该课程的教师信息（通过 StaffCourseRelation）
            from app.models import StaffCourseRelation, Staff
            staff_relations = StaffCourseRelation.query.filter_by(
                course_id=course.id
            ).all()
            
            # 获取教师名称（优先显示主讲教师，如果没有则显示第一个教师）
            teacher_name = None
            for relation in staff_relations:
                staff = Staff.query.get(relation.staff_id)
                if staff:
                    # 优先显示角色为 'teacher' 的教师（主讲教师）
                    if staff.role.value == 'teacher':
                        teacher_name = staff.name
                        break  # 找到主讲教师就停止
                    # 如果没有主讲教师，使用第一个找到的助教
                    elif not teacher_name:
                        teacher_name = staff.name
            
            course_list.append({
                "id": course.id,
                "course_code": course.course_code,
                "course_name": course.course_name,
                "description": course.description,
                "semester": course.semester,
                "status": course.status.value if course.status else None,
                "enroll_time": enroll_time.isoformat() if enroll_time else None,
                "teacher_name": teacher_name  # 添加教师名称
            })

        return True, course_list
    except Exception as e:
        db.session.rollback()
        return False, f"获取课程失败:{str(e)}"


def get_course_teachers_for_student(student_id, course_id):
    """
    获取课程的教师列表（学生端使用）
    :param student_id: 学生ID
    :param course_id: 课程ID
    :return: (success, result)
    """
    try:
        # 检查学生是否选了这个课程，或者是否是助教
        enrollment = StudentCourseRelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        ta_relation = StudentTARelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        
        if not enrollment and not ta_relation:
            return False, "未选此课程，无权查看"
        
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"
        
        # 查询该课程的所有教师（通过 StaffCourseRelation）
        from app.models import StaffCourseRelation, Staff, StaffRole
        staff_relations = StaffCourseRelation.query.filter_by(
            course_id=course_id
        ).all()
        
        teacher_list = []
        for relation in staff_relations:
            staff = Staff.query.get(relation.staff_id)
            if staff and staff.role == StaffRole.teacher:  # 只返回教师，不包括助教
                teacher_list.append({
                    "id": staff.id,
                    "staff_no": staff.staff_no,
                    "name": staff.name,
                    "email": staff.email,
                    "phone": staff.phone,
                    "role": relation.role,  # 授课角色（如"主讲教师"）
                })
        
        return True, teacher_list
    
    except Exception as e:
        db.session.rollback()
        return False, f"获取教师列表失败：{str(e)}"


def get_course_tas_for_student(student_id, course_id):
    """
    获取课程的助教列表（学生端使用）
    :param student_id: 学生ID
    :param course_id: 课程ID
    :return: (success, result)
    """
    try:
        # 检查学生是否选了这个课程，或者是否是助教
        enrollment = StudentCourseRelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        ta_relation = StudentTARelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        
        if not enrollment and not ta_relation:
            return False, "未选此课程，无权查看"
        
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"
        
        # 查询该课程的所有助教（通过 StudentTARelation）
        # StudentTARelation 已在文件顶部导入
        ta_relations = StudentTARelation.query.filter_by(
            course_id=course_id
        ).all()
        
        ta_list = []
        for relation in ta_relations:
            student = Student.query.get(relation.student_id)
            if student:
                ta_list.append({
                    "id": student.id,
                    "student_no": student.student_no,
                    "name": student.name,
                    "email": student.email,
                    "phone": student.phone,
                    "role": relation.role,
                })
        
        return True, ta_list
    
    except Exception as e:
        db.session.rollback()
        return False, f"获取助教列表失败：{str(e)}"


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

        # 检查学生是否选了这个课程，或者是否是助教
        enrollment = StudentCourseRelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        ta_relation = StudentTARelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        
        if not enrollment and not ta_relation:
            return False, "未在该班级课程中,无法查看作业"

        homeworks = Homework.query.filter_by(
            course_id=course_id
        ).order_by(
            Homework.course_hw_no.asc(),
            Homework.deadline.asc()
        ).all()

        homework_list = []
        for hw in homeworks:
            is_overdue = datetime.utcnow() > hw.deadline if hw.deadline else False

            # 查询学生是否已提交该作业
            submission = HomeworkSubmission.query.filter_by(
                student_id=student_id,
                homework_id=hw.id
            ).first()

            # 构建提交状态信息
            submission_status = None
            if submission:
                # 检查是否已过ddl，且教师已“发布成绩”，学生才能看到成绩
                current_time = datetime.utcnow()
                is_after_deadline = hw.deadline and current_time > hw.deadline

                # 检查是否有批改记录（不管is_graded的值）
                from app.models import HomeworkGrading
                grading = HomeworkGrading.query.filter_by(submission_id=submission.id).first()

                # 如果已过ddl、教师已发布成绩且有批改记录，获取成绩信息
                score = None
                is_graded_visible = False
                if grading and is_after_deadline and getattr(hw, "grades_published", False):
                    score = grading.score
                    is_graded_visible = True
                    # 如果ddl已过且已发布成绩，更新is_graded状态，确保后续查询正确
                    if not submission.is_graded:
                        submission.is_graded = True
                        db.session.commit()

                submission_status = {
                    "id": submission.id,
                    # 学生只能在 ddl 之后且老师发布成绩后，看到“已批改”状态
                    "is_graded": is_graded_visible,
                    "submit_time": submission.submit_time.isoformat() if submission.submit_time else None,
                    # 只有 ddl 后且老师发布成绩后才包含分数
                    "score": score,
                }

            # 解析 image_urls（数据库存储的是 JSON 字符串）
            image_urls = []
            if hw.image_urls:
                try:
                    import json
                    image_urls = json.loads(hw.image_urls) if isinstance(hw.image_urls, str) else hw.image_urls
                    if not isinstance(image_urls, list):
                        image_urls = []
                except (json.JSONDecodeError, TypeError):
                    image_urls = []

            homework_list.append({
                "id": hw.id,
                "course_hw_no": hw.course_hw_no,
                "title": hw.title,
                "content": hw.content,
                "image_urls": image_urls,  # 已解析为数组
                "type": hw.type.value if hw.type else None,
                "deadline": hw.deadline.isoformat() if hw.deadline else None,
                "max_score": hw.max_score or 100,  # 分数上限，默认为100
                "create_time": hw.create_time.isoformat() if hw.create_time else None,
                "is_overdue": is_overdue,
                "submission": submission_status,  # 提交状态，如果已提交则包含基本信息
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
        # 检查学生是否选了这个课程，或者是否是助教
        is_enrolled = StudentCourseRelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        ta_relation = StudentTARelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        
        if not is_enrolled and not ta_relation:
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

        # 5. 检查是否已过ddl，且老师已发布成绩，才能看到批改信息
        current_time = datetime.utcnow()
        is_after_deadline = homework.deadline and current_time > homework.deadline
        
        # 检查是否有批改记录（不管is_graded的值）
        from app.models import HomeworkGrading
        import json
        grading = HomeworkGrading.query.filter_by(submission_id=submission.id).first()
        
        # 如果已过ddl且老师已发布成绩且有批改记录，获取批改信息
        grading_info = None
        is_graded_visible = False
        if grading and is_after_deadline and getattr(homework, "grades_published", False):
            grading_info = {
                "score": grading.score,
                "ai_feedback": grading.ai_feedback,
                "annotation_data": json.loads(grading.annotation_data) if grading.annotation_data else [],
                "grade_time": grading.grade_time.strftime("%Y-%m-%d %H:%M:%S") if grading.grade_time else None,
                "grader_name": None  # 如果需要显示批改人，可以从 Staff 表查询
            }
            # 获取批改人信息
            if grading.grader_id:
                from app.models import Staff
                grader = Staff.query.get(grading.grader_id)
                if grader:
                    grading_info["grader_name"] = grader.name
            is_graded_visible = True
            # 如果ddl已过，更新is_graded状态，确保后续查询正确
            if not submission.is_graded:
                submission.is_graded = True
                db.session.commit()

        # 6. 构造返回数据
        result = {
            "id": submission.id,
            "homework_id": submission.homework_id,
            "text_content": submission.text_content,
            "image_urls": image_urls,
            "submit_time": submission.submit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_graded": is_graded_visible  # 学生只能看到ddl后的批改状态
        }
        if grading_info:
            result.update(grading_info)
        
        return True, result

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
    # 检查学生是否选了这个课程，或者是否是助教
    has_enrolled = StudentCourseRelation.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()
    ta_relation = StudentTARelation.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()
    
    if not has_enrolled and not ta_relation:
        return False, "未在该班级课程中,无权提交作业"

    existing_submission = HomeworkSubmission.query.filter_by(
        student_id=student_id,
        homework_id=homework_id
    ).first()

    image_urls_json = json.dumps(image_urls) if image_urls else None

    try:
        if existing_submission:
            # 重新提交时，删除之前的批改记录，使其重新进入未批改状态
            from app.models import HomeworkGrading
            existing_grading = HomeworkGrading.query.filter_by(
                submission_id=existing_submission.id
            ).first()
            if existing_grading:
                db.session.delete(existing_grading)
            
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
