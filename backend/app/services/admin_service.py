from app.extensions import db
from app.models import (
    Admin,
    Staff,
    Student,
    Course,
    CourseStatus,
    StaffRole,
    StudentCourseRelation,
    StaffCourseRelation,
    StudentTARelation
)
from werkzeug.security import check_password_hash, generate_password_hash


def authenticate_admin(username, password):
    """验证管理员身份"""
    try:
        admin = Admin.query.filter_by(username=username).first()
        if not admin:
            return False, "用户名或密码错误"

        if not check_password_hash(admin.password_hash, password):
            return False, "用户名或密码错误"

        admin_data = {
            "id": admin.id,
            "username": admin.username,
            "name": admin.name,
            "phone": admin.phone,
            "create_time": admin.create_time.isoformat()
        }
        return True, admin_data

    except Exception as e:
        db.session.rollback()
        return False, f"认证失败：{str(e)}"


def register_admin(admin_data):
    """创建新管理员（需严格权限控制）"""
    required_fields = ["username", "name", "password"]
    for field in required_fields:
        if not admin_data.get(field):
            return False, f"缺少必填字段：{field}"

    username = admin_data["username"]
    name = admin_data["name"]
    password = admin_data["password"]
    phone = admin_data.get("phone", "")

    try:
        # 检查用户名是否已存在
        existing = Admin.query.filter_by(username=username).first()
        if existing:
            return False, "用户名已存在"

        # 创建新管理员
        new_admin = Admin(
            username=username,
            name=name,
            password_hash=generate_password_hash(password),
            phone=phone
        )
        db.session.add(new_admin)
        db.session.commit()

        return True, {
            "id": new_admin.id,
            "username": new_admin.username,
            "name": new_admin.name,
            "phone": new_admin.phone
        }

    except Exception as e:
        db.session.rollback()
        return False, f"创建失败：{str(e)}"


def get_all_teachers():
    """获取所有教师（仅role=teacher的Staff）"""
    try:
        teachers = Staff.query.filter_by(role=StaffRole.teacher).all()
        return True, [teacher.to_dict() for teacher in teachers]
    except Exception as e:
        db.session.rollback()
        return False, f"获取教师列表失败：{str(e)}"


def get_all_students():
    """获取所有学生"""
    try:
        students = Student.query.all()
        return True, [student.to_dict() for student in students]
    except Exception as e:
        db.session.rollback()
        return False, f"获取学生列表失败：{str(e)}"


def get_all_staff():
    """获取所有教职工（包括教师和助教）"""
    try:
        staff_list = Staff.query.all()
        return True, [staff.to_dict() for staff in staff_list]
    except Exception as e:
        db.session.rollback()
        return False, f"获取教职工失败：{str(e)}"


def create_staff(staff_data):
    """创建教职工（教师或助教）"""
    required_fields = ["staff_no", "name", "role"]
    for field in required_fields:
        if not staff_data.get(field):
            return False, f"缺少必填字段：{field}"

    staff_no = staff_data["staff_no"]
    name = staff_data["name"]
    # 如果未提供密码，使用默认密码123456
    password = staff_data.get("password", "123456")
    role_str = staff_data["role"]
    email = staff_data.get("email", "")
    phone = staff_data.get("phone", "")

    # 验证角色
    if role_str not in ["teacher", "ta"]:
        return False, "角色必须是teacher或ta"

    role = StaffRole.teacher if role_str == "teacher" else StaffRole.ta

    try:
        # 检查工号是否已存在
        existing = Staff.query.filter_by(staff_no=staff_no).first()
        if existing:
            return False, "工号已存在"

        # 创建新教职工
        new_staff = Staff(
            staff_no=staff_no,
            name=name,
            password_hash=generate_password_hash(password),
            role=role,
            email=email,
            phone=phone
        )
        db.session.add(new_staff)
        db.session.commit()

        return True, new_staff.to_dict()

    except Exception as e:
        db.session.rollback()
        return False, f"创建失败：{str(e)}"


def reset_user_password(user_type, user_id, default_password="123456"):
    """重置用户密码"""
    try:
        if user_type == "staff":
            user = Staff.query.get(user_id)
        elif user_type == "student":
            user = Student.query.get(user_id)
        else:
            return False, "用户类型错误"

        if not user:
            return False, "用户不存在"

        user.password_hash = generate_password_hash(default_password)
        db.session.commit()
        return True, f"密码已重置为：{default_password}"

    except Exception as e:
        db.session.rollback()
        return False, f"重置密码失败：{str(e)}"


def approve_course(course_id, approve_status):
    """审核课程"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        if approve_status:
            course.status = CourseStatus.approved
            message = "课程已通过审核"
        else:
            course.status = CourseStatus.rejected
            message = "课程已驳回"

        db.session.commit()
        return True, message

    except Exception as e:
        db.session.rollback()
        return False, f"审核失败：{str(e)}"


def get_all_courses():
    """获取所有课程"""
    try:
        courses = Course.query.all()
        course_list = []
        for course in courses:
            course_dict = {
                "id": course.id,
                "course_code": course.course_code,
                "course_name": course.course_name,
                "description": course.description,
                "semester": course.semester,
                "status": course.status.value if course.status else None,
                "create_time": course.create_time.isoformat() if course.create_time else None
            }
            course_list.append(course_dict)
        return True, course_list
    except Exception as e:
        db.session.rollback()
        return False, f"获取课程列表失败：{str(e)}"


def delete_user(user_type, user_id):
    """删除用户（教师或学生）"""
    try:
        if user_type == "teacher":
            user = Staff.query.get(user_id)
            if not user:
                return False, "教师不存在"
            if user.role != StaffRole.teacher:
                return False, "该用户不是教师"
        elif user_type == "student":
            user = Student.query.get(user_id)
            if not user:
                return False, "学生不存在"
        else:
            return False, "用户类型错误"

        # 删除关联关系
        if user_type == "teacher":
            StaffCourseRelation.query.filter_by(staff_id=user_id).delete()
        else:
            StudentCourseRelation.query.filter_by(student_id=user_id).delete()

        db.session.delete(user)
        db.session.commit()
        return True, "用户已删除"

    except Exception as e:
        db.session.rollback()
        return False, f"删除失败：{str(e)}"


def get_admin_profile(admin_id):
    """获取管理员个人资料"""
    try:
        admin = Admin.query.get(admin_id)
        if not admin:
            return False, "管理员不存在"

        return True, {
            "id": admin.id,
            "username": admin.username,
            "name": admin.name,
            "phone": admin.phone,
            "create_time": admin.create_time.isoformat() if admin.create_time else None
        }
    except Exception as e:
        db.session.rollback()
        return False, f"获取资料失败：{str(e)}"


def update_admin_profile(admin_id, update_data):
    """更新管理员资料"""
    allowed_fields = ["name", "phone"]
    valid_data = {k: v for k, v in update_data.items() if k in allowed_fields}

    if not valid_data:
        return False, "没有可更新的字段（支持：name/phone）"

    try:
        admin = Admin.query.get(admin_id)
        if not admin:
            return False, "管理员不存在"

        for field, value in valid_data.items():
            setattr(admin, field, value)

        db.session.commit()
        return True, admin.to_dict() if hasattr(admin, 'to_dict') else {
            "id": admin.id,
            "username": admin.username,
            "name": admin.name,
            "phone": admin.phone
        }
    except Exception as e:
        db.session.rollback()
        return False, f"更新失败：{str(e)}"


def update_admin_password(admin_id, data):
    """更新管理员密码"""
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return False, "旧密码和新密码不能为空"

    if len(new_password) < 6:
        return False, "新密码长度不能少于6位"

    try:
        admin = Admin.query.get(admin_id)
        if not admin:
            return False, "管理员不存在"

        if not check_password_hash(admin.password_hash, old_password):
            return False, "旧密码错误"

        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True, "密码已更新"

    except Exception as e:
        db.session.rollback()
        return False, f"更新密码失败：{str(e)}"


def create_student(student_data):
    """创建学生"""
    required_fields = ["student_no", "name"]
    for field in required_fields:
        if not student_data.get(field):
            return False, f"缺少必填字段：{field}"

    student_no = student_data["student_no"]
    name = student_data["name"]
    # 如果未提供密码，使用默认密码123456
    password = student_data.get("password", "123456")
    email = student_data.get("email", "")
    phone = student_data.get("phone", "")

    try:
        # 检查学号是否已存在
        existing = Student.query.filter_by(student_no=student_no).first()
        if existing:
            return False, "学号已存在"

        # 创建新学生
        new_student = Student(
            student_no=student_no,
            name=name,
            password_hash=generate_password_hash(password),
            email=email,
            phone=phone
        )
        db.session.add(new_student)
        db.session.commit()

        return True, new_student.to_dict()

    except Exception as e:
        db.session.rollback()
        return False, f"创建失败：{str(e)}"


def update_student(student_id, update_data):
    """更新学生信息（支持name/email/phone）"""
    allowed_fields = ["name", "email", "phone"]
    valid_data = {k: v for k, v in update_data.items() if k in allowed_fields}

    if not valid_data:
        return False, "没有可更新的字段（支持：name/email/phone）"

    try:
        student = Student.query.get(student_id)
        if not student:
            return False, "学生不存在"

        for field, value in valid_data.items():
            setattr(student, field, value)

        db.session.commit()
        return True, student.to_dict()
    except Exception as e:
        db.session.rollback()
        return False, f"更新失败：{str(e)}"


def update_staff(staff_id, update_data):
    """更新教职工信息（支持name/email/phone）"""
    allowed_fields = ["name", "email", "phone"]
    valid_data = {k: v for k, v in update_data.items() if k in allowed_fields}

    if not valid_data:
        return False, "没有可更新的字段（支持：name/email/phone）"

    try:
        staff = Staff.query.get(staff_id)
        if not staff:
            return False, "教职工不存在"

        for field, value in valid_data.items():
            setattr(staff, field, value)

        db.session.commit()
        return True, staff.to_dict()
    except Exception as e:
        db.session.rollback()
        return False, f"更新失败：{str(e)}"


def create_course(course_data):
    """创建课程"""
    required_fields = ["course_code", "course_name", "semester"]
    for field in required_fields:
        if not course_data.get(field):
            return False, f"缺少必填字段：{field}"

    course_code = course_data["course_code"]
    course_name = course_data["course_name"]
    semester = course_data["semester"]
    description = course_data.get("description", "")

    try:
        # 检查课程代码是否已存在
        existing = Course.query.filter_by(course_code=course_code).first()
        if existing:
            return False, "课程代码已存在"

        # 创建新课程
        new_course = Course(
            course_code=course_code,
            course_name=course_name,
            semester=semester,
            description=description,
            status=CourseStatus.pending
        )
        db.session.add(new_course)
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
        return False, f"创建失败：{str(e)}"


def update_course(course_id, update_data):
    """更新课程信息（支持course_name/semester/description）"""
    allowed_fields = ["course_name", "semester", "description"]
    valid_data = {k: v for k, v in update_data.items() if k in allowed_fields}

    if not valid_data:
        return False, "没有可更新的字段（支持：course_name/semester/description）"

    try:
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

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
        return False, f"更新失败：{str(e)}"


def close_course(course_id):
    """课程结课"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        if course.status == CourseStatus.closed:
            return False, "课程已经结课"

        course.status = CourseStatus.closed
        db.session.commit()
        return True, "课程已结课"
    except Exception as e:
        db.session.rollback()
        return False, f"结课失败：{str(e)}"


def delete_course(course_id):
    """删除课程"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        # 级联删除课程与学生的关联
        StudentCourseRelation.query.filter_by(course_id=course_id).delete()
        # 级联删除课程与教职工的关联
        StaffCourseRelation.query.filter_by(course_id=course_id).delete()

        db.session.delete(course)
        db.session.commit()
        return True, "课程已删除"
    except Exception as e:
        db.session.rollback()
        return False, f"删除失败：{str(e)}"


def add_teacher_to_course(course_id, staff_no):
    """
    管理员添加教师到课程
    :param course_id: 课程ID
    :param staff_no: 教师工号
    :return: (success, result)
    """
    try:
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        # 查找教师（必须是teacher角色）
        teacher = Staff.query.filter_by(staff_no=staff_no, role=StaffRole.teacher).first()
        if not teacher:
            return False, "该工号不存在或不是教师"

        # 检查是否已经添加过
        existing = StaffCourseRelation.query.filter_by(
            staff_id=teacher.id,
            course_id=course_id
        ).first()
        if existing:
            return False, "该教师已经加入此课程"

        # 创建关联
        relation = StaffCourseRelation(
            staff_id=teacher.id,
            course_id=course_id,
            role="主讲教师"
        )
        db.session.add(relation)
        db.session.commit()

        return True, {
            "teacher_id": teacher.id,
            "teacher_name": teacher.name,
            "teacher_staff_no": teacher.staff_no
        }

    except Exception as e:
        db.session.rollback()
        return False, f"添加教师失败：{str(e)}"


def add_ta_to_course_admin(course_id, student_no):
    """
    管理员添加助教到课程（助教从学生中选择，使用学号）
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


def add_student_to_course(course_id, student_no):
    """
    管理员添加学生到课程
    :param course_id: 课程ID
    :param student_no: 学生学号
    :return: (success, result)
    """
    try:
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        # 查找学生
        student = Student.query.filter_by(student_no=student_no).first()
        if not student:
            return False, "该学号不存在"

        # 检查是否已经添加过
        existing = StudentCourseRelation.query.filter_by(
            student_id=student.id,
            course_id=course_id
        ).first()
        if existing:
            return False, "该学生已经加入此课程"

        # 创建关联
        from datetime import datetime
        relation = StudentCourseRelation(
            student_id=student.id,
            course_id=course_id,
            enroll_time=datetime.utcnow()
        )
        db.session.add(relation)
        db.session.commit()

        return True, {
            "student_id": student.id,
            "student_name": student.name,
            "student_no": student.student_no
        }

    except Exception as e:
        db.session.rollback()
        return False, f"添加学生失败：{str(e)}"
