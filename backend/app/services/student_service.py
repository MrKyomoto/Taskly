from app.models import Student, Course, StudentCourseRelation
from app.extensions import db
from werkzeug.security import check_password_hash


def verify_student_credentials(student_no, password):
    """验证学生登录信息"""
    student = Student.query.filter_by(student_no=student_no).first()
    if student and check_password_hash(student.password, password):
        return student
    return None


def get_student_by_id(student_id):
    """根据ID获取学生信息"""
    return Student.query.get(student_id)


def enroll_student_in_course(student_id, course_code):
    """学生选课"""
    # 检查课程是否存在且已审核通过
    course = Course.query.filter_by(
        course_code=course_code,
        status=CourseStatus.approved
    ).first()
    if not course:
        return False, "课程不存在或未通过审核"

    # 检查是否已选该课程
    existing = StudentCourseRelation.query.filter_by(
        student_id=student_id,
        course_id=course.id
    ).first()
    if existing:
        return False, "已选该课程"

    # 执行选课
    relation = StudentCourseRelation(
        student_id=student_id,
        course_id=course.id
    )
    db.session.add(relation)
    db.session.commit()
    return True, ""


def get_student_courses(student_id):
    """获取学生已选课程"""
    student = get_student_by_id(student_id)
    if not student:
        return []
    return student.courses  # 利用模型关联直接获取
