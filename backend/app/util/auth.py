from app.models import StaffCourseRelation, StudentTARelation


def is_staff_in_course(staff_id, course_id, role=None):
    """
    验证教师或助教是否属于该课程
    :param staff_id: 教师ID或学生ID（如果是助教）
    :param course_id: 课程ID
    :param role: 角色（'teacher' 或 'ta'），如果为None则自动判断
    :return: bool
    """
    # 如果是助教，通过 StudentTARelation 检查
    if role == "ta":
        ta_relation = StudentTARelation.query.filter_by(
            student_id=staff_id,
            course_id=course_id
        ).first()
        return bool(ta_relation)
    
    # 如果是教师，通过 StaffCourseRelation 检查
    # 如果 role 为 None，先尝试作为教师检查
    relation = StaffCourseRelation.query.filter_by(
        staff_id=staff_id,
        course_id=course_id
    ).first()
    if relation:
        return True
    
    # 如果没有找到教师关系，尝试作为助教检查（兼容性）
    if role is None:
        ta_relation = StudentTARelation.query.filter_by(
            student_id=staff_id,
            course_id=course_id
        ).first()
        return bool(ta_relation)
    
    return False
