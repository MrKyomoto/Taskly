"""
成绩导出服务
"""
from app.extensions import db
from app.models import (
    Course,
    Student,
    Homework,
    HomeworkSubmission,
    HomeworkGrading,
    StudentCourseRelation,
)
from io import BytesIO
import pandas as pd
from datetime import datetime

# 尝试导入 openpyxl
try:
    import openpyxl
except ImportError:
    openpyxl = None


def export_course_grades(course_id, homework_ids=None, student_ids=None):
    """
    导出课程成绩为 Excel 文件
    :param course_id: 课程ID
    :param homework_ids: 可选，作业ID列表，仅导出这些作业；为 None 时导出该课程所有作业
    :param student_ids: 可选，学生ID列表，仅导出这些学生；为 None 时导出该课程所有学生
    :return: (success, result) 成功返回 (True, BytesIO对象)，失败返回 (False, error_message)
    """
    if pd is None or openpyxl is None:
        return False, "请先安装 pandas 和 openpyxl: pip install pandas openpyxl"
    
    try:
        # 1. 验证课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return False, "课程不存在"

        # 2. 获取该课程的学生（可选按 student_ids 过滤）
        student_query = StudentCourseRelation.query.filter_by(course_id=course_id)
        if student_ids:
            student_query = student_query.filter(
                StudentCourseRelation.student_id.in_(student_ids)
            )
        student_relations = student_query.all()
        
        if not student_relations:
            return False, "该课程暂无学生"

        # 3. 获取该课程的作业（可选按 homework_ids 过滤，按创建时间排序）
        homework_query = Homework.query.filter_by(course_id=course_id)
        if homework_ids:
            homework_query = homework_query.filter(Homework.id.in_(homework_ids))
        homeworks = homework_query.order_by(Homework.create_time.asc()).all()

        # 4. 构建数据
        data = []
        for relation in student_relations:
            student = Student.query.get(relation.student_id)
            if not student:
                continue

            row = {
                '学号': student.student_no,
                '姓名': student.name,
            }

            # 为每个作业添加分数列
            total_score = 0
            graded_count = 0
            for homework in homeworks:
                # 查找该学生的提交记录
                submission = HomeworkSubmission.query.filter_by(
                    student_id=student.id,
                    homework_id=homework.id
                ).first()

                if submission and submission.is_graded:
                    # 查找评分记录
                    grading = HomeworkGrading.query.filter_by(
                        submission_id=submission.id
                    ).first()
                    if grading and grading.score is not None:
                        score = grading.score
                        row[f"作业{homework.course_hw_no}"] = score
                        total_score += score
                        graded_count += 1
                    else:
                        # 有提交但没有评分，用 "--" 表示
                        row[f"作业{homework.course_hw_no}"] = "--"
                else:
                    # 未提交，同样用 "--" 表示
                    row[f"作业{homework.course_hw_no}"] = "--"

            # 计算平均分
            if graded_count > 0:
                row["平均分"] = round(total_score / graded_count, 2)
            else:
                row["平均分"] = 0

            data.append(row)

        # 5. 创建 DataFrame
        df = pd.DataFrame(data)

        # 6. 生成 Excel 文件（使用 utf-8-sig 编码避免中文乱码）
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="成绩单", index=False)
        
        output.seek(0)

        return True, output

    except Exception as e:
        db.session.rollback()
        return False, f"导出失败：{str(e)}"

