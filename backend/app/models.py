"""
定义数据库表结构和关系，通过 SQLAlchemy ORM 映射到 MySQL 表
"""
from datetime import datetime
from app.extensions import db
import enum

# 枚举类型定义


class StaffRole(enum.Enum):
    teacher = 'teacher'
    ta = 'ta'


class CourseStatus(enum.Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'


class HomeworkType(enum.Enum):
    short = 'short'
    long = 'long'

# 学生表


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_no = db.Column(db.String(30), unique=True,
                           nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)  # 存储哈希值
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联：学生-课程（多对多）
    courses = db.relationship(
        'Course', secondary='student_course_relation', backref='students')

# 教职工表（老师/助教）


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_no = db.Column(db.String(30), unique=True,
                         nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum(StaffRole), nullable=False)
    password = db.Column(db.String(100), nullable=False)  # 存储哈希值
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联：教职工-课程（多对多）
    courses = db.relationship(
        'Course', secondary='staff_course_relation', backref='staffs')

# 管理员表


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True,
                         nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)  # 存储哈希值
    phone = db.Column(db.String(20))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

# 课程表


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True,
                            nullable=False, index=True)
    course_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    semester = db.Column(db.String(20), nullable=False)
    status = db.Column(db.Enum(CourseStatus),
                       default=CourseStatus.pending, index=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联：课程-作业（一对多）
    homeworks = db.relationship(
        'Homework', backref='course', cascade='all, delete-orphan')

# 学生-课程关联表（多对多）


class StudentCourseRelation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(
        'student.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey(
        'course.id', ondelete='CASCADE'), nullable=False)
    enroll_time = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint(
        'student_id', 'course_id', name='unique_student_course'),)

# 教职工-课程关联表（多对多）


class StaffCourseRelation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey(
        'staff.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey(
        'course.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 授课角色（如"主讲教师"）

    __table_args__ = (db.UniqueConstraint(
        'staff_id', 'course_id', name='unique_staff_course'),)

# 作业表


class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey(
        'course.id', ondelete='CASCADE'), nullable=False)
    publisher_id = db.Column(
        db.Integer, db.ForeignKey('staff.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)  # 文本内容
    image_urls = db.Column(db.Text)  # JSON格式存储图片URL
    type = db.Column(db.Enum(HomeworkType))
    deadline = db.Column(db.DateTime, nullable=False, index=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联：作业-提交记录（一对多）
    submissions = db.relationship(
        'HomeworkSubmission', backref='homework', cascade='all, delete-orphan')

# 作业提交表


class HomeworkSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey(
        'homework.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey(
        'student.id', ondelete='CASCADE'), nullable=False)
    text_content = db.Column(db.Text)  # 提交文本
    image_urls = db.Column(db.Text)  # JSON格式存储图片URL
    submit_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_graded = db.Column(db.Boolean, default=False)  # 是否批改

    __table_args__ = (db.UniqueConstraint(
        'student_id', 'homework_id', name='unique_student_homework'),)

# 作业批改表


class HomeworkGrading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey(
        'homework_submission.id', ondelete='CASCADE'), nullable=False)
    grader_id = db.Column(
        db.Integer, db.ForeignKey('staff.id'), nullable=False)
    score = db.Column(db.Integer)
    annotation_data = db.Column(db.Text)  # JSON格式存储批改标注
    ai_feedback = db.Column(db.Text)
    grade_time = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint(
        'submission_id', name='unique_submission'),)
