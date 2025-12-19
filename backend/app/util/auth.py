from app.models import StaffCourseRelation


def is_staff_in_course(staff_id, course_id):
    """验证教师是否属于该课程"""
    relation = StaffCourseRelation.query.filter_by(
        staff_id=staff_id,
        course_id=course_id
    ).first()
    return bool(relation)
