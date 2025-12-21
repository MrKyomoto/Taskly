from datetime import datetime
import json
import re
from app.extensions import db
from app.models import (
    Staff,
    Student,
    StudentCourseRelation,
    StudentTARelation,
    Course,
    StaffCourseRelation,
    Homework,
    HomeworkSubmission,
    HomeworkGrading,
    CourseStatus,
    HomeworkType,
    StaffRole
)
from app.services.student_service import validate_password_strength, validate_phone_format
from werkzeug.security import check_password_hash, generate_password_hash


def authenticate_teacher(staff_no, password):
    """验证教师身份"""
    try:
        teacher = Staff.query.filter_by(
            staff_no=staff_no,
            role=StaffRole.teacher
        ).first()

        if not teacher:
            return False, "工号或密码错误"

        if not check_password_hash(teacher.password_hash, password):
            return False, "工号或密码错误"

        teacher_data = {
            "id": teacher.id,
            "staff_no": teacher.staff_no,
            "name": teacher.name,
            "email": teacher.email,
            "phone": teacher.phone
        }
        return True, teacher_data

    except Exception as e:
        db.session.rollback()
        return False, f"身份验证失败：{str(e)}"


def register_teacher(teacher_data):
    """教师注册服务"""
    required_fields = ["staff_no", "name", "password", "email", "phone"]
    # 校验必填字段
    for field in required_fields:
        if not teacher_data.get(field):
            return False, f"缺少必填字段：{field}"

    staff_no = teacher_data["staff_no"]
    name = teacher_data["name"]
    password = teacher_data["password"]
    email = teacher_data["email"]
    phone = teacher_data["phone"]
    
    # 密码强度校验
    is_valid, error_msg = validate_password_strength(password)
    if not is_valid:
        return False, error_msg

    # 手机号格式校验
    is_valid, error_msg = validate_phone_format(phone)
    if not is_valid:
        return False, error_msg

    try:
        existing_teacher = Staff.query.filter_by(staff_no=staff_no).first()
        if existing_teacher:
            return False, "该工号已注册"

        hashed_password = generate_password_hash(password)
        new_teacher = Staff(
            staff_no=staff_no,
            name=name,
            password_hash=hashed_password,
            role=StaffRole.teacher,
            email=email,
            phone=phone
        )
        db.session.add(new_teacher)
        db.session.commit()

        return True, {
            "id": new_teacher.id,
            "staff_no": new_teacher.staff_no,
            "name": new_teacher.name,
            "email": new_teacher.email,
            "phone": new_teacher.phone
        }

    except Exception as e:
        db.session.rollback()
        return False, f"注册失败：{str(e)}"


def get_teacher(teacher_id):
    """获取教师信息"""
    try:
        teacher = Staff.query.filter_by(
            id=teacher_id,
            role=StaffRole.teacher
        ).first()

        if not teacher:
            return False, "教师不存在"

        teacher_data = {
            "id": teacher.id,
            "staff_no": teacher.staff_no,
            "name": teacher.name,
            "email": teacher.email,
            "phone": teacher.phone,
            "create_time": teacher.create_time.isoformat() if teacher.create_time else None
        }
        return True, teacher_data

    except Exception as e:
        db.session.rollback()
        return False, f"获取教师信息失败：{str(e)}"


def update_teacher_profile(teacher_id, update_data):
    """更新教师资料"""
    allowed_fields = ["name", "email", "phone"]
    valid_data = {k: v for k, v in update_data.items() if k in allowed_fields}

    if not valid_data:
        return False, "没有可更新的有效字段（支持：姓名/邮箱/电话）"

    try:
        teacher = Staff.query.filter_by(
            id=teacher_id,
            role=StaffRole.teacher
        ).first()

        if not teacher:
            return False, "教师不存在"

        for field, value in valid_data.items():
            setattr(teacher, field, value)

        db.session.commit()

        return True, {
            "id": teacher.id,
            "staff_no": teacher.staff_no,
            "name": teacher.name,
            "email": teacher.email,
            "phone": teacher.phone
        }

    except Exception as e:
        db.session.rollback()
        return False, f"更新资料失败：{str(e)}"


def update_teacher_password(teacher_id, old_password, new_password):
    """更新教师密码"""
    if len(new_password) < 8:
        return False, "新密码长度不能少于8位"
    if old_password == new_password:
        return False, "新密码不能与原密码相同"

    try:
        teacher = Staff.query.filter_by(
            id=teacher_id,
            role=StaffRole.teacher
        ).first()

        if not teacher:
            return False, "教师不存在"

        if not check_password_hash(teacher.password_hash, old_password):
            return False, "原密码验证失败"

        teacher.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True, ""

    except Exception as e:
        db.session.rollback()
        return False, f"密码更新失败：{str(e)}"


def get_teacher_courses(user_id, role="teacher"):
    """获取教师或助教负责的课程"""
    try:
        course_list = []
        
        if role == "ta":
            # 助教：通过 StudentTARelation 获取课程
            student = Student.query.get(user_id)
            if not student:
                return False, "学生不存在"
            
            # 查询该学生作为助教的课程
            ta_relations = StudentTARelation.query.filter_by(
                student_id=user_id
            ).all()
            
            for relation in ta_relations:
                course = Course.query.get(relation.course_id)
                if course:
                    # 统计已选人数
                    student_count = StudentCourseRelation.query.filter_by(
                        course_id=course.id
                    ).count()
                    
                    course_list.append({
                        "id": course.id,
                        "course_code": course.course_code,
                        "course_name": course.course_name,
                        "description": course.description,
                        "semester": course.semester,
                        "status": course.status.value,
                        "role": relation.role,  # 助教角色
                        "student_count": student_count,  # 已选人数
                        "create_time": course.create_time.isoformat()
                    })
        else:
            # 教师：通过 StaffCourseRelation 获取课程
            teacher = Staff.query.filter_by(id=user_id).first()
            if not teacher:
                return False, "教师不存在"

            # 查询教师或助教关联的课程（不限制角色）
            courses = db.session.query(
                Course, StaffCourseRelation.role
            ).join(
                StaffCourseRelation,
                Course.id == StaffCourseRelation.course_id
            ).filter(
                StaffCourseRelation.staff_id == user_id
            ).all()

            for course, role_name in courses:
                # 统计已选人数
                student_count = StudentCourseRelation.query.filter_by(
                    course_id=course.id
                ).count()
                
                course_list.append({
                    "id": course.id,
                    "course_code": course.course_code,
                    "course_name": course.course_name,
                    "description": course.description,
                    "semester": course.semester,
                    "status": course.status.value,
                    "role": role_name,  # 授课角色（如"主讲教师"）
                    "student_count": student_count,  # 已选人数
                    "create_time": course.create_time.isoformat()
                })

        return True, course_list

    except Exception as e:
        db.session.rollback()
        return False, f"获取课程失败：{str(e)}"


def generate_course_code():
    """
    生成唯一的课程邀请码（6位大写字母+数字）
    :return: 课程代码字符串
    """
    import random
    import string
    
    while True:
        # 生成6位随机码：3位大写字母 + 3位数字
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        numbers = ''.join(random.choices(string.digits, k=3))
        code = letters + numbers
        
        # 检查是否已存在
        existing = Course.query.filter_by(course_code=code).first()
        if not existing:
            return code


def create_course(teacher_id, course_data):
    """创建课程（支持手动指定课程号或自动生成）"""
    required_fields = ["course_name", "semester", "course_code"]
    for field in required_fields:
        if not course_data.get(field):
            return False, f"缺少必填字段：{field}"

    semester_str = course_data.get("semester", "")
    # 学期格式：年份 + - + Spring/Summer/Fall，例如 2024-Fall
    if not re.match(r"^\d{4}-(Spring|Summer|Fall)$", semester_str):
        return False, "学期格式不正确，应为：年份-Spring/Summer/Fall，例如 2024-Fall"

    course_code = course_data.get("course_code", "").strip()
    if not course_code:
        return False, "课程号不能为空"

    try:
        # 检查课程代码是否已存在
        existing = Course.query.filter_by(course_code=course_code).first()
        if existing:
            return False, "课程号已存在，请使用其他课程号"

        new_course = Course(
            course_code=course_code,
            course_name=course_data["course_name"],
            description=course_data.get("description", ""),
            semester=course_data["semester"],
            status=CourseStatus.approved  # 教师创建的课程直接设为已审核
        )
        db.session.add(new_course)
        db.session.flush()  # 获取新课程ID

        # 建立教师与课程的关联
        relation = StaffCourseRelation(
            staff_id=teacher_id,
            course_id=new_course.id,
            role=course_data.get("role", "主讲教师")
        )
        db.session.add(relation)
        db.session.commit()

        return True, {
            "id": new_course.id,
            "course_code": new_course.course_code,
            "course_name": new_course.course_name,
            "description": new_course.description,
            "semester": new_course.semester,
            "status": new_course.status.value
        }

    except Exception as e:
        db.session.rollback()
        return False, f"创建课程失败：{str(e)}"


def update_course(course_id, update_data):
    """更新课程信息"""
    allowed_fields = ["course_name", "description", "semester", "status"]
    valid_data = {k: v for k, v in update_data.items() if k in allowed_fields}

    if not valid_data:
        return False, "没有可更新的有效字段"

    try:
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        # 校验学期格式
        if "semester" in valid_data:
            semester_str = valid_data["semester"] or ""
            if not re.match(r"^\d{4}-(Spring|Summer|Fall)$", semester_str):
                return False, "学期格式不正确，应为：年份-Spring/Summer/Fall，例如 2024-Fall"

        # 处理状态枚举转换
        if "status" in valid_data:
            try:
                valid_data["status"] = CourseStatus(valid_data["status"])
            except ValueError:
                return False, "无效的课程状态"

        for field, value in valid_data.items():
            setattr(course, field, value)

        db.session.commit()

        return True, {
            "id": course.id,
            "course_code": course.course_code,
            "course_name": course.course_name,
            "description": course.description,
            "semester": course.semester,
            "status": course.status.value
        }

    except Exception as e:
        db.session.rollback()
        return False, f"更新课程失败：{str(e)}"


def create_homework(course_id, staff_id, homework_data):
    """创建作业"""
    required_fields = ["title", "content", "deadline", "course_hw_no"]
    for field in required_fields:
        if not homework_data.get(field):
            return False, f"缺少必填字段：{field}"

    try:
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        # 检查作业序号是否重复
        existing_hw = Homework.query.filter_by(
            course_id=course_id,
            course_hw_no=homework_data["course_hw_no"]
        ).first()
        if existing_hw:
            return False, f"该课程中作业序号 {homework_data['course_hw_no']} 已存在"

        # 处理截止时间
        try:
            deadline = datetime.fromisoformat(homework_data["deadline"])
        except ValueError:
            return False, "无效的截止时间格式（应为ISO格式）"

        # 处理作业类型
        hw_type = homework_data.get("type")
        if hw_type:
            try:
                hw_type = HomeworkType(hw_type)
            except ValueError:
                return False, "无效的作业类型"

        # 处理图片URLs
        image_urls = homework_data.get("image_urls", [])
        if image_urls and not isinstance(image_urls, list):
            return False, "image_urls 必须是数组"

        # 处理分数上限（默认为100）
        max_score = homework_data.get("max_score", 100)
        if not isinstance(max_score, int) or max_score <= 0:
            return False, "分数上限必须是大于0的整数"
        
        new_homework = Homework(
            course_id=course_id,
            publisher_id=staff_id,  # 支持教师或助教发布
            course_hw_no=homework_data["course_hw_no"],
            title=homework_data["title"],
            content=homework_data["content"],
            image_urls=json.dumps(image_urls) if image_urls else None,
            type=hw_type,
            deadline=deadline,
            max_score=max_score
        )
        db.session.add(new_homework)
        db.session.commit()

        return True, {
            "id": new_homework.id,
            "course_id": new_homework.course_id,
            "course_hw_no": new_homework.course_hw_no,
            "title": new_homework.title,
            "content": new_homework.content,
            "image_urls": json.loads(new_homework.image_urls) if new_homework.image_urls else [],
            "type": new_homework.type.value if new_homework.type else None,
            "deadline": new_homework.deadline.isoformat(),
            "create_time": new_homework.create_time.isoformat()
        }

    except Exception as e:
        db.session.rollback()
        return False, f"创建作业失败：{str(e)}"


def get_course_homeworks(course_id):
    """获取课程作业列表"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        homeworks = Homework.query.filter_by(
            course_id=course_id
        ).order_by(Homework.course_hw_no).all()

        # 统计课程总学生数
        total_students = StudentCourseRelation.query.filter_by(
            course_id=course_id
        ).count()

        homework_list = []
        for hw in homeworks:
            # 统计该作业的提交数
            submission_count = HomeworkSubmission.query.filter_by(
                homework_id=hw.id
            ).count()

            # 统计该作业已批改人数（无论是否提交，凡有评分记录即视为已批改）
            graded_count = db.session.query(HomeworkGrading).join(
                HomeworkSubmission,
                HomeworkGrading.submission_id == HomeworkSubmission.id
            ).filter(
                HomeworkSubmission.homework_id == hw.id
            ).count()

            # 判断是否已过期
            is_overdue = datetime.utcnow() > hw.deadline if hw.deadline else False

            homework_list.append({
                "id": hw.id,
                "course_id": hw.course_id,
                "course_hw_no": hw.course_hw_no,
                "title": hw.title,
                "content": hw.content,
                "image_urls": json.loads(hw.image_urls) if hw.image_urls else [],
                "type": hw.type.value if hw.type else None,
                "deadline": hw.deadline.isoformat(),
                "max_score": hw.max_score or 100,  # 分数上限，默认为100
                "create_time": hw.create_time.isoformat(),
                "submission_count": submission_count,  # 提交人数
                "total_students": total_students,  # 总人数
                "graded_count": graded_count,  # 已批改人数
                "grades_published": getattr(hw, "grades_published", False),
                "is_overdue": is_overdue  # 是否已过期
            })

        return True, homework_list

    except Exception as e:
        db.session.rollback()
        return False, f"获取作业失败：{str(e)}"


def get_student_submissions(course_id, homework_id):
    """获取学生作业提交列表（包括未提交的学生，如果已过ddl）"""
    try:
        # 验证作业是否属于该课程
        homework = Homework.query.filter_by(
            id=homework_id,
            course_id=course_id
        ).first()
        if not homework:
            return False, "该课程下无此作业"

        # 检查是否已过ddl
        current_time = datetime.utcnow()
        is_after_deadline = homework.deadline and current_time > homework.deadline

        # 查询该作业的所有提交
        from app.models import Student
        from sqlalchemy.orm import joinedload
        submissions = HomeworkSubmission.query.filter_by(
            homework_id=homework_id
        ).options(
            joinedload(HomeworkSubmission.student)
        ).all()

        # 获取已提交的学生ID集合
        submitted_student_ids = {sub.student_id for sub in submissions}

        submission_list = []
        for sub in submissions:
            # 获取评分信息
            grading = HomeworkGrading.query.filter_by(
                submission_id=sub.id
            ).first()

            # 获取批改人信息
            grader_name = None
            if grading:
                grader = Staff.query.get(grading.grader_id)
                grader_name = grader.name if grader else "未知"

            # 确保学生信息存在
            student_name = sub.student.name if sub.student else "未知"
            student_no = sub.student.student_no if sub.student else "未知"

            submission_list.append({
                "id": sub.id,
                "student_id": sub.student_id,
                "student_name": student_name,
                "student_no": student_no,
                "text_content": sub.text_content,
                "image_urls": json.loads(sub.image_urls) if sub.image_urls else [],
                "submit_time": sub.submit_time.isoformat(),
                "is_graded": sub.is_graded,
                "has_submitted": True,  # 标记为已提交
                "grading": {
                    "score": grading.score if grading else None,
                    "ai_feedback": grading.ai_feedback if grading else None,
                    "annotation_data": json.loads(grading.annotation_data) if (grading and grading.annotation_data) else ([] if grading else None),
                    "grade_time": grading.grade_time.isoformat() if grading else None,
                    "grader_name": grader_name  # 批改人姓名
                } if sub.is_graded else None
            })

        # 如果已过ddl，添加未提交的学生
        if is_after_deadline:
            # 查询所有选课学生
            enrolled_students = db.session.query(
                Student.id,
                Student.student_no,
                Student.name
            ).join(
                StudentCourseRelation,
                Student.id == StudentCourseRelation.student_id
            ).filter(
                StudentCourseRelation.course_id == course_id
            ).all()

            # 添加未提交的学生
            for student in enrolled_students:
                if student.id not in submitted_student_ids:
                    # 检查是否有0分记录（已批改但未提交）
                    # 对于未提交的学生，我们需要查找是否有对应的提交记录（可能是空提交）
                    # 或者通过其他方式存储0分记录
                    # 这里先检查是否有空的提交记录（用于存储0分）
                    empty_submission = HomeworkSubmission.query.filter_by(
                        homework_id=homework_id,
                        student_id=student.id
                    ).first()
                    
                    is_graded_zero = False
                    grader_name = None
                    grading_info = None
                    
                    if empty_submission:
                        # 如果有空提交记录，检查是否有批改记录
                        grading = HomeworkGrading.query.filter_by(
                            submission_id=empty_submission.id
                        ).first()
                        if grading:
                            is_graded_zero = True
                            grader = Staff.query.get(grading.grader_id)
                            grader_name = grader.name if grader else "未知"
                            grading_info = {
                                "score": grading.score,
                                "ai_feedback": grading.ai_feedback,
                                "annotation_data": json.loads(grading.annotation_data) if (grading and grading.annotation_data) else [],
                                "grade_time": grading.grade_time.isoformat() if grading.grade_time else None,
                                "grader_name": grader_name
                            }
                    
                    submission_list.append({
                        "id": empty_submission.id if empty_submission else None,  # 未提交可能没有submission id
                        "student_id": student.id,
                        "student_name": student.name,
                        "student_no": student.student_no,
                        "text_content": None,
                        "image_urls": [],
                        "submit_time": None,
                        "is_graded": is_graded_zero,  # 如果已批0分则为True
                        "has_submitted": False,  # 标记为未提交
                        "grading": grading_info
                    })

        return True, submission_list

    except Exception as e:
        db.session.rollback()
        return False, f"获取提交记录失败：{str(e)}"


def grade_submission(submission_id, grader_id, score, annotation_data=None, ai_feedback=None):
    """批改作业（支持教师和助教）

    要求：教师打分必须 > 0 且 <= 作业分数上限，可为小数或整数。
    """
    try:
        # 验证提交是否存在
        submission = HomeworkSubmission.query.get(submission_id)
        if not submission:
            return False, "提交记录不存在"

        # 获取作业信息，检查ddl和分数上限
        from app.models import Homework
        homework = Homework.query.get(submission.homework_id)
        if not homework:
            return False, "作业不存在"

        max_score = homework.max_score or 100

        # 验证分数有效性：允许小数，但必须 >0 且 <= 上限
        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            return False, "分数必须是数字"

        if numeric_score <= 0 or numeric_score > max_score:
            return False, f"分数必须大于0且小于等于{max_score}"

        # 检查是否已过ddl
        current_time = datetime.utcnow()
        is_after_deadline = homework.deadline and current_time > homework.deadline

        # 检查是否已批改
        existing_grading = HomeworkGrading.query.filter_by(
            submission_id=submission_id
        ).first()

        if existing_grading:
            # 更新现有评分
            existing_grading.score = numeric_score
            existing_grading.annotation_data = json.dumps(
                annotation_data) if annotation_data else None
            existing_grading.ai_feedback = ai_feedback
            existing_grading.grader_id = grader_id  # 更新批改人
            existing_grading.grade_time = datetime.utcnow()
            grading = existing_grading
        else:
            # 创建新评分记录
            grading = HomeworkGrading(
                submission_id=submission_id,
                grader_id=grader_id,
                score=numeric_score,
                annotation_data=json.dumps(
                    annotation_data) if annotation_data else None,
                ai_feedback=ai_feedback
            )
            db.session.add(grading)

        # 更新提交状态：只有在ddl之后才标记为已批改（学生可见）
        # ddl前批改的数据会保存，但is_graded保持False，学生看不到
        submission.is_graded = is_after_deadline
        db.session.commit()

        # 获取批改人信息
        grader = Staff.query.get(grader_id)
        grader_name = grader.name if grader else "未知"

        return True, {
            "submission_id": submission_id,
            "score": grading.score,
            "annotation_data": json.loads(grading.annotation_data) if grading.annotation_data else [],
            "ai_feedback": grading.ai_feedback,
            "grader_name": grader_name,  # 批改人姓名
            "grade_time": grading.grade_time.isoformat(),
            "grader_id": grader_id
        }

    except Exception as e:
        db.session.rollback()
        return False, f"批改失败：{str(e)}"


def grade_unsubmitted_student(homework_id, student_id, grader_id, score=0, ai_feedback='未提交作业'):
    """为未提交的学生创建空提交记录并打0分"""
    try:
        from app.models import Homework, HomeworkSubmission, HomeworkGrading, Student
        
        # 验证作业是否存在
        homework = Homework.query.get(homework_id)
        if not homework:
            return False, "作业不存在"
        
        # 验证学生是否存在
        student = Student.query.get(student_id)
        if not student:
            return False, "学生不存在"
        
        # 验证分数不超过max_score（这里允许为0，用于未提交学生的一键0分）
        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            return False, "分数必须是数字"

        if numeric_score < 0 or numeric_score > homework.max_score:
            return False, f"分数必须在0-{homework.max_score}之间"
        
        # 检查是否已有提交记录（即使是空的）
        submission = HomeworkSubmission.query.filter_by(
            homework_id=homework_id,
            student_id=student_id
        ).first()
        
        if not submission:
            # 创建空的提交记录
            submission = HomeworkSubmission(
                homework_id=homework_id,
                student_id=student_id,
                text_content='',
                image_urls='[]',
                submit_time=datetime.utcnow()
            )
            db.session.add(submission)
            db.session.flush()  # 获取submission.id
        
        # 检查是否已有批改记录
        existing_grading = HomeworkGrading.query.filter_by(
            submission_id=submission.id
        ).first()
        
        if existing_grading:
            # 更新现有批改记录
            existing_grading.score = numeric_score
            existing_grading.ai_feedback = ai_feedback
            existing_grading.grader_id = grader_id
            existing_grading.grade_time = datetime.utcnow()
            grading = existing_grading
        else:
            # 创建新的批改记录
            grading = HomeworkGrading(
                submission_id=submission.id,
                grader_id=grader_id,
                score=numeric_score,
                ai_feedback=ai_feedback,
                annotation_data='[]'  # 空批注
            )
            db.session.add(grading)
        
        # 检查是否已过ddl，决定是否让学生看到批改
        current_time = datetime.utcnow()
        is_after_deadline = homework.deadline and current_time > homework.deadline
        submission.is_graded = is_after_deadline
        
        db.session.commit()
        
        # 获取批改人信息
        from app.models import Staff
        grader = Staff.query.get(grader_id)
        grader_name = grader.name if grader else "未知"
        
        return True, {
            "submission_id": submission.id,
            "score": grading.score,
            "ai_feedback": grading.ai_feedback,
            "annotation_data": [],
            "grader_name": grader_name,
            "grade_time": grading.grade_time.isoformat() if grading.grade_time else None,
            "grader_id": grader_id
        }
        
    except Exception as e:
        db.session.rollback()
        return False, f"批改失败：{str(e)}"

# 作业更新服务


def update_homework_service(homework_id, course_id, homework_data):
    try:
        # 查询作业
        homework = Homework.query.filter_by(
            id=homework_id, course_id=course_id).first()
        if not homework:
            return False, "作业不存在"

        # 更新作业字段
        if 'title' in homework_data:
            homework.title = homework_data['title']
        if 'content' in homework_data:
            homework.content = homework_data['content']
        if 'image_urls' in homework_data:
            homework.image_urls = json.dumps(homework_data['image_urls'])
        if 'deadline' in homework_data:
            try:
                # 处理截止时间格式（支持多种格式）
                deadline_str = homework_data['deadline']
                if isinstance(deadline_str, str):
                    # 尝试解析 ISO 格式
                    try:
                        deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                    except ValueError:
                        # 如果 ISO 格式失败，尝试其他格式
                        # 格式: YYYY-MM-DDTHH:mm:ss 或 YYYY-MM-DD HH:mm:ss
                        try:
                            if 'T' in deadline_str:
                                deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M:%S')
                            else:
                                deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            return False, f"无效的截止时间格式: {deadline_str}"
                else:
                    return False, "截止时间必须是字符串格式"
                homework.deadline = deadline
            except Exception as e:
                return False, f"处理截止时间失败: {str(e)}"
        if 'max_score' in homework_data:
            max_score = homework_data['max_score']
            if not isinstance(max_score, int) or max_score <= 0:
                return False, "分数上限必须是大于0的整数"
            homework.max_score = max_score

        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, f"更新失败: {str(e)}"

# 作业删除服务


def delete_homework_service(homework_id, course_id):
    try:
        # 查询作业
        homework = Homework.query.filter_by(
            id=homework_id, course_id=course_id).first()
        if not homework:
            return False, "作业不存在"

        # 删除作业
        db.session.delete(homework)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, f"删除失败: {str(e)}"

def publish_homework_grades_service(staff_id, course_id, homework_id):
    """
    发布某次作业的成绩：
    - 要求当前教师/助教已完成该课程所有学生的批改
    - 设置 Homework.grades_published = True
    """
    from app.util.auth import is_staff_in_course
    # 验证课程权限
    if not is_staff_in_course(staff_id, course_id):
        return False, "无此课程权限"

    try:
        homework = Homework.query.filter_by(id=homework_id, course_id=course_id).first()
        if not homework:
            return False, "作业不存在"

        # 统计总学生数
        total_students = StudentCourseRelation.query.filter_by(
            course_id=course_id
        ).count()
        if total_students == 0:
            return False, "该课程暂无学生"

        # 统计已批改人数（存在评分记录即视为已批改，包括未提交但被打0分的）
        graded_count = db.session.query(HomeworkGrading).join(
            HomeworkSubmission,
            HomeworkGrading.submission_id == HomeworkSubmission.id
        ).filter(
            HomeworkSubmission.homework_id == homework_id
        ).count()

        if graded_count < total_students:
            return False, f"仍有未批改的学生（已批改 {graded_count} / 共 {total_students}），暂不能发布成绩"

        homework.grades_published = True
        db.session.commit()
        return True, "成绩已发布"

    except Exception as e:
        db.session.rollback()
        return False, f"发布成绩失败: {str(e)}"


# 选课学生查询服务


def get_course_students_service(course_id):
    try:
        # 查询选课学生
        students = db.session.query(
            Student.id,
            Student.student_no,
            Student.name,
            Student.email,
            Student.phone,
            StudentCourseRelation.enroll_time
        ).join(
            StudentCourseRelation,
            Student.id == StudentCourseRelation.student_id
        ).filter(
            StudentCourseRelation.course_id == course_id
        ).all()

        # 格式化结果
        student_list = [{
            "id": s.id,
            "student_no": s.student_no,
            "name": s.name,
            "email": s.email,
            "phone": s.phone,
            "enroll_time": s.enroll_time.isoformat()
        } for s in students]

        return True, student_list
    except Exception as e:
        return False, f"查询失败: {str(e)}"


def add_ta_to_course(course_id, student_no):
    """
    添加助教到课程（助教从学生中选择，使用学号）
    :param course_id: 课程ID
    :param student_no: 学生学号
    :return: (success, result)
    """
    try:
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        # 查找学生（助教从学生中选择）
        student = Student.query.filter_by(student_no=student_no).first()
        if not student:
            return False, "该学号不存在"

        # 检查是否已经添加过（检查 StudentTARelation）
        existing_ta = StudentTARelation.query.filter_by(
            student_id=student.id,
            course_id=course_id
        ).first()
        if existing_ta:
            return False, "该学生已经作为助教加入此课程"

        # 创建学生-课程助教关联
        relation = StudentTARelation(
            student_id=student.id,
            course_id=course_id,
            role="助教"
        )
        db.session.add(relation)
        db.session.commit()

        return True, {
            "ta_id": student.id,
            "ta_name": student.name,
            "ta_student_no": student.student_no
        }

    except Exception as e:
        db.session.rollback()
        return False, f"添加助教失败：{str(e)}"


def get_course_tas(course_id):
    """
    获取课程的助教列表
    :param course_id: 课程ID
    :return: (success, result)
    """
    try:
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        # 查询该课程的所有助教（通过 StudentTARelation）
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
                    "create_time": relation.create_time.isoformat() if relation.create_time else None
                })

        return True, ta_list

    except Exception as e:
        db.session.rollback()
        return False, f"获取助教列表失败：{str(e)}"


def get_course_teachers(course_id):
    """
    获取课程的教师列表
    :param course_id: 课程ID
    :return: (success, result)
    """
    try:
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        # 查询该课程的所有教师（通过 StaffCourseRelation）
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


def check_teacher_identifier(identifier):
    """
    检查工号是否存在
    :param identifier: 工号
    :return: (success, result) 成功返回(True, {"user_id": id})，失败返回(False, 错误信息)
    """
    try:
        teacher = Staff.query.filter_by(staff_no=identifier, role=StaffRole.teacher).first()
        if not teacher:
            return False, "工号不存在"
        return True, {"user_id": teacher.id}
    except Exception as e:
        return False, f"查询失败：{str(e)}"


def verify_teacher_contact(user_id, contact, method):
    """
    验证教师的邮箱或电话是否匹配
    :param user_id: 教师ID
    :param contact: 邮箱或电话
    :param method: 'email' 或 'phone'
    :return: (success, error_msg) 成功返回(True, "")，失败返回(False, 错误信息)
    """
    try:
        teacher = Staff.query.get(user_id)
        if not teacher:
            return False, "教师不存在"
        
        if method == 'email':
            if teacher.email != contact:
                return False, "邮箱不匹配，请输入注册时填写的邮箱"
        elif method == 'phone':
            if teacher.phone != contact:
                return False, "电话不匹配，请输入注册时填写的电话"
        else:
            return False, "无效的验证方式"
        
        return True, ""
    except Exception as e:
        return False, f"验证失败：{str(e)}"


def reset_teacher_password_with_verification(user_id, verification_code, new_password, stored_code):
    """
    通过验证码重置教师密码
    :param user_id: 教师ID
    :param verification_code: 用户输入的验证码
    :param new_password: 新密码（明文）
    :param stored_code: 存储的验证码
    :return: (success, error_msg) 成功返回(True, "")，失败返回(False, 错误信息)
    """
    # 验证验证码
    if verification_code != stored_code:
        return False, "验证码错误"
    
    # 密码强度校验（复用student_service中的函数）
    from app.services.student_service import validate_password_strength
    is_valid, error_msg = validate_password_strength(new_password)
    if not is_valid:
        return False, error_msg
    
    try:
        teacher = Staff.query.get(user_id)
        if not teacher:
            return False, "教师不存在"
        
        teacher.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True, ""
    except Exception as e:
        db.session.rollback()
        return False, f"密码重置失败：{str(e)}"
