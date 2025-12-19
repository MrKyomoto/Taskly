from app.extensions import db
from app.models import (
    Admin,
    Staff,
    Student,
    Course,
    CourseStatus,
    StaffRole,
    StudentCourseRelation,
    StaffCourseRelation
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
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            return False, "用户名已存在"

        # 密码强度校验
        if len(password) < 8:
            return False, "密码长度不能少于8位"

        hashed_password = generate_password_hash(password)
        new_admin = Admin(
            username=username,
            name=name,
            password_hash=hashed_password,
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
    """获取所有教师列表"""
    try:
        teachers = Staff.query.filter_by(role=StaffRole.teacher).all()
        teacher_list = []
        for teacher in teachers:
            teacher_list.append({
                "id": teacher.id,
                "staff_no": teacher.staff_no,
                "name": teacher.name,
                "email": teacher.email,
                "phone": teacher.phone,
                "role": "teacher",
                "create_time": teacher.create_time.isoformat()
            })
        return True, teacher_list
    except Exception as e:
        db.session.rollback()
        return False, f"获取教师失败：{str(e)}"


def get_all_staff():
    """获取所有教职工列表（包括教师和助教）"""
    try:
        staff_list = Staff.query.all()
        result = []
        for staff in staff_list:
            result.append({
                "id": staff.id,
                "staff_no": staff.staff_no,
                "name": staff.name,
                "email": staff.email,
                "phone": staff.phone,
                "role": staff.role.value if staff.role else None,
                "create_time": staff.create_time.isoformat() if staff.create_time else None
            })
        return True, result
    except Exception as e:
        db.session.rollback()
        return False, f"获取教职工失败：{str(e)}"


def create_staff(staff_data):
    """创建教职工（教师或助教）"""
    required_fields = ["staff_no", "name", "password", "role"]
    for field in required_fields:
        if not staff_data.get(field):
            return False, f"缺少必填字段：{field}"

    staff_no = staff_data["staff_no"]
    name = staff_data["name"]
    password = staff_data["password"]
    role_str = staff_data["role"]
    email = staff_data.get("email", "")
    phone = staff_data.get("phone", "")

    # 验证角色
    if role_str not in ["teacher", "ta"]:
        return False, "角色必须为 teacher 或 ta"

    try:
        existing_staff = Staff.query.filter_by(staff_no=staff_no).first()
        if existing_staff:
            return False, "该工号已存在"

        # 密码强度校验
        if len(password) < 6:
            return False, "密码长度不能少于6位"

        hashed_password = generate_password_hash(password)
        role_enum = StaffRole.teacher if role_str == "teacher" else StaffRole.ta
        
        new_staff = Staff(
            staff_no=staff_no,
            name=name,
            password_hash=hashed_password,
            role=role_enum,
            email=email,
            phone=phone
        )
        db.session.add(new_staff)
        db.session.commit()

        return True, {
            "id": new_staff.id,
            "staff_no": new_staff.staff_no,
            "name": new_staff.name,
            "email": new_staff.email,
            "phone": new_staff.phone,
            "role": new_staff.role.value
        }
    except Exception as e:
        db.session.rollback()
        return False, f"创建失败：{str(e)}"


def reset_user_password(user_type, user_id, default_password="123456"):
    """重置用户密码（教师/学生）"""
    try:
        if user_type == "staff":
            user = Staff.query.get(user_id)
        elif user_type == "student":
            user = Student.query.get(user_id)
        else:
            return False, "用户类型必须为 staff 或 student"

        if not user:
            return False, "用户不存在"

        hashed_password = generate_password_hash(default_password)
        user.password_hash = hashed_password
        db.session.commit()

        return True, f"密码已重置为：{default_password}"
    except Exception as e:
        db.session.rollback()
        return False, f"重置密码失败：{str(e)}"


def get_all_students():
    """获取所有学生列表"""
    try:
        students = Student.query.all()
        student_list = []
        for student in students:
            student_list.append({
                "id": student.id,
                "student_no": student.student_no,
                "name": student.name,
                "email": student.email,
                "phone": student.phone,
                "create_time": student.create_time.isoformat()
            })
        return True, student_list
    except Exception as e:
        db.session.rollback()
        return False, f"获取学生失败：{str(e)}"


def approve_course(course_id, approve_status):
    """审核课程（通过/驳回）"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        if course.status != CourseStatus.pending:
            return False, f"课程当前状态为{course.status.value}，无需审核"

        course.status = CourseStatus.approved if approve_status else CourseStatus.rejected
        db.session.commit()
        return True, f"课程已{'通过' if approve_status else '驳回'}审核"
    except Exception as e:
        db.session.rollback()
        return False, f"审核失败：{str(e)}"


def get_all_courses():
    """获取所有课程（含待审核）"""
    try:
        courses = Course.query.all()
        course_list = []
        for course in courses:
            course_list.append({
                "id": course.id,
                "course_code": course.course_code,
                "course_name": course.course_name,
                "description": course.description,
                "semester": course.semester,
                "status": course.status.value,
                "create_time": course.create_time.isoformat()
            })
        return True, course_list
    except Exception as e:
        db.session.rollback()
        return False, f"获取课程失败：{str(e)}"


def delete_user(user_type, user_id):
    """删除用户（教师/学生）"""
    try:
        if user_type == 'teacher':
            # 仅删除教师角色用户
            user = Staff.query.filter_by(
                id=user_id, role=StaffRole.teacher).first()
            # 级联删除教师与课程的关联
            StaffCourseRelation.query.filter_by(staff_id=user_id).delete()
        else:
            user = Student.query.get(user_id)
            # 级联删除学生选课记录
            StudentCourseRelation.query.filter_by(student_id=user_id).delete()

        if not user:
            return False, f"{'教师' if user_type == 'teacher' else '学生'}不存在"

        db.session.delete(user)
        db.session.commit()
        return True, f"{'教师' if user_type == 'teacher' else '学生'}已删除"
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
            "create_time": admin.create_time.isoformat()
        }
    except Exception as e:
        db.session.rollback()
        return False, f"获取资料失败：{str(e)}"


def update_admin_profile(admin_id, update_data):
    """更新管理员资料（支持name/phone）"""
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
        return True, {
            "id": admin.id,
            "username": admin.username,
            "name": admin.name,
            "phone": admin.phone
        }
    except Exception as e:
        db.session.rollback()
        return False, f"更新失败：{str(e)}"


def update_admin_password(admin_id, old_password, new_password):
    """更新管理员密码"""
    if len(new_password) < 8:
        return False, "新密码长度不能少于8位"
    if old_password == new_password:
        return False, "新密码不能与原密码相同"

    try:
        admin = Admin.query.get(admin_id)
        if not admin:
            return False, "管理员不存在"

        if not check_password_hash(admin.password_hash, old_password):
            return False, "原密码验证失败"

        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True, ""
    except Exception as e:
        db.session.rollback()
        return False, f"密码更新失败：{str(e)}"
