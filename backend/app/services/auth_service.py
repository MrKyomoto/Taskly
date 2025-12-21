"""
统一认证服务
支持多表轮询：Admin -> Staff -> Student
"""
from app.extensions import db
from app.models import Admin, Staff, Student, StaffRole, StudentTARelation
from werkzeug.security import check_password_hash


def unified_authenticate(username, password):
    """
    统一认证函数，按优先级顺序查询：Admin -> Staff -> Student
    :param username: 用户名（可能是管理员用户名、工号或学号）
    :param password: 密码（明文）
    :return: (success, result) 
        成功时返回 (True, {"role": "admin|teacher|student", "user_data": {...}, "id": ...})
        失败时返回 (False, error_message)
    """
    try:
        # 优先级1: 查询管理员表（使用 username 字段）
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            if check_password_hash(admin.password_hash, password):
                return True, {
                    "role": "admin",
                    "id": admin.id,
                    "user_data": {
                        "id": admin.id,
                        "username": admin.username,
                        "name": admin.name,
                        "phone": admin.phone,
                        "create_time": admin.create_time.isoformat() if admin.create_time else None
                    }
                }
            else:
                # 密码错误，不再继续查询（安全考虑：避免信息泄露）
                return False, "用户名或密码错误"

        # 优先级2: 查询教职工表（使用 staff_no 字段）
        staff = Staff.query.filter_by(staff_no=username).first()
        if staff:
            if check_password_hash(staff.password_hash, password):
                role = "teacher" if staff.role == StaffRole.teacher else "ta"
                return True, {
                    "role": role,
                    "id": staff.id,
                    "user_data": {
                        "id": staff.id,
                        "staff_no": staff.staff_no,
                        "name": staff.name,
                        "email": staff.email,
                        "phone": staff.phone,
                        "role": staff.role.value if staff.role else None
                    }
                }
            else:
                # 密码错误
                return False, "工号或密码错误"

        # 优先级3: 查询学生表（使用 student_no 字段）
        student = Student.query.filter_by(student_no=username).first()
        if student:
            if check_password_hash(student.password_hash, password):
                # 检查该学生是否也是助教（通过 StudentTARelation 表）
                ta_relation = StudentTARelation.query.filter_by(student_id=student.id).first()
                # 如果学生是助教，返回 role 为 "ta"，否则为 "student"
                role = "ta" if ta_relation else "student"
                
                return True, {
                    "role": role,
                    "id": student.id,
                    "user_data": {
                        "id": student.id,
                        "student_no": student.student_no,
                        "name": student.name,
                        "email": student.email,
                        "phone": student.phone,
                        "create_time": student.create_time.isoformat() if student.create_time else None
                    }
                }
            else:
                # 密码错误
                return False, "学号或密码错误"

        # 所有表都没找到
        return False, "用户名或密码错误"

    except Exception as e:
        db.session.rollback()
        return False, f"认证失败：{str(e)}"


def check_identifier_exists(identifier):
    """
    检查账号是否存在（用于忘记密码功能）
    :param identifier: 账号（可能是管理员用户名、工号或学号）
    :return: (success, result)
        成功时返回 (True, {"role": "admin|teacher|student", "user_id": ...})
        失败时返回 (False, error_message)
    """
    try:
        # 优先级1: 查询管理员表
        admin = Admin.query.filter_by(username=identifier).first()
        if admin:
            return True, {"role": "admin", "user_id": admin.id}

        # 优先级2: 查询教职工表
        staff = Staff.query.filter_by(staff_no=identifier).first()
        if staff:
            role = "teacher" if staff.role == StaffRole.teacher else "ta"
            return True, {"role": role, "user_id": staff.id}

        # 优先级3: 查询学生表
        student = Student.query.filter_by(student_no=identifier).first()
        if student:
            # 检查该学生是否也是助教（通过 StudentTARelation 表）
            ta_relation = StudentTARelation.query.filter_by(student_id=student.id).first()
            # 如果学生是助教，返回 role 为 "ta"，否则为 "student"
            role = "ta" if ta_relation else "student"
            return True, {"role": role, "user_id": student.id}

        # 所有表都没找到
        return False, "账号不存在"

    except Exception as e:
        db.session.rollback()
        return False, f"查询失败：{str(e)}"

