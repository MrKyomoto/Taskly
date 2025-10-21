from datetime import datetime
import json
from app.extensions import db
from app.models import (
    Staff,
    Student,
    StudentCourseRelation,
    Course,
    StaffCourseRelation,
    Homework,
    HomeworkSubmission,
    HomeworkGrading,
    CourseStatus,
    HomeworkType,
    StaffRole
)
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

        if not check_password_hash(teacher.password, password):
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
    required_fields = ["staff_no", "name", "password"]
    for field in required_fields:
        if not teacher_data.get(field):
            return False, f"缺少必填字段：{field}"

    staff_no = teacher_data["staff_no"]
    name = teacher_data["name"]
    password = teacher_data["password"]
    email = teacher_data.get("email", "")
    phone = teacher_data.get("phone", "")

    try:
        existing_teacher = Staff.query.filter_by(staff_no=staff_no).first()
        if existing_teacher:
            return False, "该工号已注册"

        hashed_password = generate_password_hash(password)
        new_teacher = Staff(
            staff_no=staff_no,
            name=name,
            password=hashed_password,
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

        if not check_password_hash(teacher.password, old_password):
            return False, "原密码验证失败"

        teacher.password = generate_password_hash(new_password)
        db.session.commit()
        return True, ""

    except Exception as e:
        db.session.rollback()
        return False, f"密码更新失败：{str(e)}"


def get_teacher_courses(teacher_id):
    """获取教师教授的课程"""
    try:
        teacher = Staff.query.filter_by(
            id=teacher_id,
            role=StaffRole.teacher
        ).first()

        if not teacher:
            return False, "教师不存在"

        # 查询教师关联的课程
        courses = db.session.query(
            Course, StaffCourseRelation.role
        ).join(
            StaffCourseRelation,
            Course.id == StaffCourseRelation.course_id
        ).filter(
            StaffCourseRelation.staff_id == teacher_id
        ).all()

        course_list = []
        for course, role in courses:
            course_list.append({
                "id": course.id,
                "course_code": course.course_code,
                "course_name": course.course_name,
                "description": course.description,
                "semester": course.semester,
                "status": course.status.value,
                "role": role,  # 授课角色（如"主讲教师"）
                "create_time": course.create_time.isoformat()
            })

        return True, course_list

    except Exception as e:
        db.session.rollback()
        return False, f"获取课程失败：{str(e)}"


def create_course(teacher_id, course_data):
    """创建课程"""
    required_fields = ["course_code", "course_name", "semester"]
    for field in required_fields:
        if not course_data.get(field):
            return False, f"缺少必填字段：{field}"

    try:
        # 检查课程代码是否已存在
        existing_course = Course.query.filter_by(
            course_code=course_data["course_code"]
        ).first()
        if existing_course:
            return False, "课程代码已存在"

        new_course = Course(
            course_code=course_data["course_code"],
            course_name=course_data["course_name"],
            description=course_data.get("description", ""),
            semester=course_data["semester"],
            status=CourseStatus.pending  # 新建课程默认为待审核
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


def create_homework(course_id, teacher_id, homework_data):
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

        new_homework = Homework(
            course_id=course_id,
            publisher_id=teacher_id,
            course_hw_no=homework_data["course_hw_no"],
            title=homework_data["title"],
            content=homework_data["content"],
            image_urls=json.dumps(image_urls) if image_urls else None,
            type=hw_type,
            deadline=deadline
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

        homework_list = []
        for hw in homeworks:
            homework_list.append({
                "id": hw.id,
                "course_id": hw.course_id,
                "course_hw_no": hw.course_hw_no,
                "title": hw.title,
                "content": hw.content,
                "image_urls": json.loads(hw.image_urls) if hw.image_urls else [],
                "type": hw.type.value if hw.type else None,
                "deadline": hw.deadline.isoformat(),
                "create_time": hw.create_time.isoformat()
            })

        return True, homework_list

    except Exception as e:
        db.session.rollback()
        return False, f"获取作业失败：{str(e)}"


def get_student_submissions(course_id, homework_id):
    """获取学生作业提交列表"""
    try:
        # 验证作业是否属于该课程
        homework = Homework.query.filter_by(
            id=homework_id,
            course_id=course_id
        ).first()
        if not homework:
            return False, "该课程下无此作业"

        # 查询该作业的所有提交
        submissions = HomeworkSubmission.query.filter_by(
            homework_id=homework_id
        ).join(
            HomeworkSubmission.student
        ).all()

        submission_list = []
        for sub in submissions:
            # 获取评分信息
            grading = HomeworkGrading.query.filter_by(
                submission_id=sub.id
            ).first()

            submission_list.append({
                "id": sub.id,
                "student_id": sub.student_id,
                "student_name": sub.student.name,
                "student_no": sub.student.student_no,
                "text_content": sub.text_content,
                "image_urls": json.loads(sub.image_urls) if sub.image_urls else [],
                "submit_time": sub.submit_time.isoformat(),
                "is_graded": sub.is_graded,
                "grading": {
                    "score": grading.score if grading else None,
                    "annotation_data": json.loads(grading.annotation_data) if (grading and grading.annotation_data) else None,
                    "grade_time": grading.grade_time.isoformat() if grading else None
                } if sub.is_graded else None
            })

        return True, submission_list

    except Exception as e:
        db.session.rollback()
        return False, f"获取提交记录失败：{str(e)}"


def grade_submission(submission_id, grader_id, score, annotation_data=None):
    """批改作业"""
    try:
        # 验证提交是否存在
        submission = HomeworkSubmission.query.get(submission_id)
        if not submission:
            return False, "提交记录不存在"

        # 验证分数有效性
        if not isinstance(score, int) or score < 0 or score > 100:
            return False, "分数必须是0-100之间的整数"

        # 检查是否已批改
        existing_grading = HomeworkGrading.query.filter_by(
            submission_id=submission_id
        ).first()

        if existing_grading:
            # 更新现有评分
            existing_grading.score = score
            existing_grading.annotation_data = json.dumps(
                annotation_data) if annotation_data else None
            existing_grading.grade_time = datetime.utcnow()
            grading = existing_grading
        else:
            # 创建新评分记录
            grading = HomeworkGrading(
                submission_id=submission_id,
                grader_id=grader_id,
                score=score,
                annotation_data=json.dumps(
                    annotation_data) if annotation_data else None
            )
            db.session.add(grading)

        # 更新提交状态
        submission.is_graded = True
        db.session.commit()

        return True, {
            "submission_id": submission_id,
            "score": grading.score,
            "annotation_data": json.loads(grading.annotation_data) if grading.annotation_data else None,
            "grade_time": grading.grade_time.isoformat(),
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
            homework.deadline = datetime.fromisoformat(
                homework_data['deadline'])

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
