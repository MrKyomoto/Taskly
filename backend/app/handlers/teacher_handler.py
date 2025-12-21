from flask import jsonify, send_file, request
from flask_jwt_extended import create_access_token
from datetime import datetime
from app.services.teacher_service import (
    authenticate_teacher,
    register_teacher,
    get_teacher,
    update_teacher_profile,
    update_teacher_password,
    get_teacher_courses,
    create_course,
    update_course,
    create_homework,
    get_course_homeworks,
    get_student_submissions,
    grade_submission,
    grade_unsubmitted_student,
    update_homework_service,
    delete_homework_service,
    get_course_students_service,
    publish_homework_grades_service,
)
from app.models import StaffCourseRelation
from app.util.auth import is_staff_in_course


def handle_teacher_login(data):
    """处理教师登录"""
    staff_no = data.get('staff_no')
    password = data.get('password')

    if not staff_no or not password:
        return jsonify({"error": "工号和密码不能为空"}), 400

    success, result = authenticate_teacher(staff_no, password)
    if not success:
        return jsonify({"error": result}), 401

    # 创建JWT令牌
    identity_str = f"teacher:{result['id']}"
    access_token = create_access_token(identity=identity_str)

    return jsonify({
        "access_token": access_token,
        "teacher": {
            "id": result["id"],
            "staff_no": result["staff_no"],
            "name": result["name"],
            "email": result["email"],
            "phone": result["phone"],
        }
    }), 200


def handle_teacher_register(data):
    """处理教师注册请求"""
    success, result = register_teacher(data)
    if success:
        return jsonify({
            "message": "注册成功",
            "teacher": {
                "id": result["id"],
                "staff_no": result["staff_no"],
                "name": result["name"],
                "email": result["email"],
                "phone": result["phone"],
            }
        }), 201
    return jsonify({"error": result}), 400


def handle_get_teacher_profile(teacher_id):
    """获取教师个人资料"""
    success, data = get_teacher(teacher_id)
    if success:
        return jsonify({
            "id": data["id"],
            "staff_no": data["staff_no"],
            "name": data["name"],
            "email": data["email"],
            "phone": data["phone"],
        }), 200
    return jsonify({"error": data}), 404


def handle_update_teacher_profile(teacher_id, update_data):
    """处理教师修改个人资料请求"""
    success, result = update_teacher_profile(teacher_id, update_data)
    if success:
        return jsonify({
            "message": "资料更新成功",
            "teacher": result
        }), 200
    if result == "教师不存在":
        return jsonify({"error": result}), 404
    return jsonify({"error": result}), 400


def handle_update_teacher_password(teacher_id, password_data):
    """处理教师修改密码请求"""
    old_password = password_data.get("old_password")
    new_password = password_data.get("new_password")

    if not old_password or not new_password:
        return jsonify({"error": "原密码和新密码不能为空"}), 400

    success, error_msg = update_teacher_password(
        teacher_id, old_password, new_password)
    if success:
        return jsonify({"message": "密码修改成功，请重新登录"}), 200
    return jsonify({"error": error_msg}), 400


def handle_get_teacher_courses(user_id, role="teacher"):
    """获取教师或助教负责的课程"""
    success, data = get_teacher_courses(user_id, role)
    if success:
        return jsonify({
            "course_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_create_course(teacher_id, course_data):
    """处理创建课程"""
    success, result = create_course(teacher_id, course_data)
    if success:
        return jsonify({
            "message": "课程创建成功",
            "course": result
        }), 201
    return jsonify({"error": result}), 400


def handle_update_course(teacher_id, course_id, update_data):
    """处理更新课程"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    # 验证教师是否有权限修改该课程
    # 使用 is_staff_in_course 函数，支持教师和助教
    if not is_staff_in_course(teacher_id, course_id):
        return jsonify({"error": "无权限修改该课程"}), 403

    success, result = update_course(course_id, update_data)
    if success:
        return jsonify({
            "message": "课程更新成功",
            "course": result
        }), 200
    return jsonify({"error": result}), 400


def handle_create_homework(staff_id, course_id, homework_data):
    """处理创建作业（支持教师和助教）"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    # 验证权限（教师或助教都可以创建作业）
    # 使用 is_staff_in_course 函数，它会自动检查 StaffCourseRelation 和 StudentTARelation
    if not is_staff_in_course(staff_id, course_id):
        return jsonify({"error": "无权限为该课程创建作业"}), 403

    success, result = create_homework(course_id, staff_id, homework_data)
    if success:
        return jsonify({
            "message": "作业创建成功",
            "homework": result
        }), 201
    return jsonify({"error": result}), 400


def handle_get_course_homeworks(user_id, course_id, role="teacher"):
    """获取课程作业列表（支持教师和助教）"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    # 统一权限验证：助教在教师端拥有和教师相同的权限
    # 不传 role 参数，让函数自动判断（会同时检查教师和助教关系）
    if not is_staff_in_course(user_id, course_id):
        return jsonify({"error": "无权限查看该课程作业"}), 403

    success, data = get_course_homeworks(course_id)
    if success:
        return jsonify({
            "homework_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_upload_homework_image(staff_id, course_id, homework_id, files):
    """处理教师上传作业文件（支持图片和PDF）"""
    from app.util.file_upload import upload_file
    success_urls = []
    error_messages = []

    try:
        course_id = int(course_id)
        homework_id = int(homework_id)
    except ValueError:
        response = jsonify({"error": "课程ID和作业ID必须为数字"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 400

    try:
        from app.models import Homework
        homework = Homework.query.filter_by(id=homework_id, course_id=course_id).first()
        if not homework:
            response = jsonify({"error": f"作业ID {homework_id} 不存在或不属于该课程"})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 404

        # 验证权限（支持教师和助教）
        from app.util.auth import is_staff_in_course
        # 从路由中获取role（如果有的话），否则is_staff_in_course会自动判断
        if not is_staff_in_course(staff_id, course_id):
            response = jsonify({"error": "无权限为该课程上传文件"})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 403

        for file in files:
            if file.filename == '':
                error_messages.append("存在空文件名的文件")
                continue

            try:
                # 调用单文件上传工具（支持图片和PDF）
                file_url = upload_file(
                    file=file,
                    course_id=course_id,
                    course_hw_no=homework.course_hw_no,
                    resource_type="post",
                    student_id=None
                )
                # upload_file返回URL字符串或错误响应(tuple)，需要检查
                if isinstance(file_url, tuple):
                    # 如果是错误响应，跳过
                    error_messages.append(f"文件 {file.filename} 上传失败")
                    continue
                # 如果是字符串URL，添加到成功列表
                if isinstance(file_url, str):
                    success_urls.append(file_url)
                else:
                    error_messages.append(f"文件 {file.filename} 上传失败：未知错误")
            except Exception as e:
                error_messages.append(f"文件 {file.filename} 上传失败: {str(e)}")

        # 构建响应
        if not success_urls:
            # 全部失败
            response = jsonify({
                "error": "所有文件上传失败",
                "details": error_messages
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            return response, 400
        else:
            # 部分或全部成功
            response = jsonify({
                "success_count": len(success_urls),
                "image_urls": success_urls,
                "errors": error_messages  # 记录失败的文件信息
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            return response, 201
    except Exception as e:
        response = jsonify({"error": f"上传处理失败:{str(e)}"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500


def handle_get_student_submissions(user_id, course_id, homework_id, role="teacher"):
    """获取学生作业提交列表（支持教师和助教）"""
    try:
        course_id = int(course_id)
        homework_id = int(homework_id)
    except ValueError:
        return jsonify({"error": "课程ID和作业ID必须为数字"}), 400

    # 统一权限验证：助教在教师端拥有和教师相同的权限
    # 不传 role 参数，让函数自动判断（会同时检查教师和助教关系）
    if not is_staff_in_course(user_id, course_id):
        return jsonify({"error": "无权限查看该课程提交记录"}), 403

    success, data = get_student_submissions(course_id, homework_id)
    if success:
        return jsonify({
            "submission_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_grade_submission(user_id, submission_id, grade_data, role="teacher"):
    """处理作业批改（支持教师和助教）"""
    try:
        submission_id = int(submission_id)
    except ValueError:
        return jsonify({"error": "提交ID必须为数字"}), 400

    # 先获取提交记录，验证权限
    from app.models import HomeworkSubmission, Homework
    submission = HomeworkSubmission.query.get(submission_id)
    if not submission:
        return jsonify({"error": "提交记录不存在"}), 404
    
    # 获取作业和课程信息
    homework = Homework.query.get(submission.homework_id)
    if not homework:
        return jsonify({"error": "作业不存在"}), 404
    
    course_id = homework.course_id
    
    # 统一权限验证：助教在教师端拥有和教师相同的权限
    # 不传 role 参数，让函数自动判断（会同时检查教师和助教关系）
    if not is_staff_in_course(user_id, course_id):
        return jsonify({"error": "无权限批改该课程作业"}), 403

    score = grade_data.get('score')
    annotation = grade_data.get('annotation_data')
    ai_feedback = grade_data.get('ai_feedback')  # 支持 AI 反馈

    if score is None:
        return jsonify({"error": "评分不能为空"}), 400

    success, result = grade_submission(
        submission_id=submission_id,
        grader_id=user_id,
        score=score,
        annotation_data=annotation,
        ai_feedback=ai_feedback
    )
    if success:
        return jsonify({
            "message": "批改成功",
            "grading": result
        }), 200
    return jsonify({"error": result}), 400


def handle_grade_unsubmitted_student(staff_id, course_id, homework_id, student_id, grade_data):
    """处理为未提交学生打0分"""
    # 权限验证
    if not is_staff_in_course(staff_id, course_id):
        return jsonify({"error": "无此课程权限"}), 403
    
    score = grade_data.get('score', 0)
    ai_feedback = grade_data.get('ai_feedback', '未提交作业')
    
    success, result = grade_unsubmitted_student(
        homework_id=homework_id,
        student_id=student_id,
        grader_id=staff_id,
        score=score,
        ai_feedback=ai_feedback
    )
    
    if success:
        return jsonify({
            "message": "批改成功",
            "grading": result
        }), 200
    return jsonify({"error": result}), 400

# 处理作业更新


def handle_update_homework(staff_id, course_id, homework_id, homework_data):
    # 权限验证
    if not is_staff_in_course(staff_id, course_id):
        return jsonify({"error": "无此课程权限"}), 403

    # 调用服务层
    success, result = update_homework_service(
        homework_id, course_id, homework_data)
    if success:
        return jsonify({"message": "作业更新成功"}), 200
    return jsonify({"error": result}), 400

# 处理作业删除


def handle_delete_homework(staff_id, course_id, homework_id):
    # 权限验证
    if not is_staff_in_course(staff_id, course_id):
        return jsonify({"error": "无此课程权限"}), 403

    # 调用服务层
    success, result = delete_homework_service(homework_id, course_id)
    if success:
        return jsonify({"message": "作业删除成功"}), 200
    return jsonify({"error": result}), 400

# 处理选课学生查询


def handle_get_course_students(staff_id, course_id):
    # 权限验证
    if not is_staff_in_course(staff_id, course_id):
        return jsonify({"error": "无此课程权限"}), 403

    # 调用服务层
    success, result = get_course_students_service(course_id)
    if success:
        return jsonify({
            "student_list": result,
            "count": len(result)
        }), 200
    return jsonify({"error": result}), 400


def handle_add_ta_to_course(teacher_id, course_id, data):
    """处理添加助教到课程"""
    # 权限验证：只有教师可以添加助教
    from app.models import Staff, StaffRole
    teacher = Staff.query.get(teacher_id)
    if not teacher or teacher.role != StaffRole.teacher:
        return jsonify({"error": "只有教师可以添加助教"}), 403

    # 验证课程权限
    if not is_staff_in_course(teacher_id, course_id):
        return jsonify({"error": "无此课程权限"}), 403

    student_no = data.get('student_no')
    if not student_no:
        return jsonify({"error": "学号不能为空"}), 400

    from app.services.teacher_service import add_ta_to_course
    success, result = add_ta_to_course(course_id, student_no)
    if success:
        return jsonify({
            "message": "助教添加成功",
            "ta": result
        }), 200
    return jsonify({"error": result}), 400


def handle_get_course_tas(staff_id, course_id):
    """获取课程的助教列表"""
    # 权限验证
    if not is_staff_in_course(staff_id, course_id):
        return jsonify({"error": "无此课程权限"}), 403

    from app.services.teacher_service import get_course_tas
    success, result = get_course_tas(course_id)
    if success:
        return jsonify({
            "ta_list": result,
            "count": len(result)
        }), 200
    return jsonify({"error": result}), 400


def handle_get_course_teachers(staff_id, course_id):
    """获取课程的教师列表"""
    # 权限验证
    if not is_staff_in_course(staff_id, course_id):
        return jsonify({"error": "无此课程权限"}), 403

    from app.services.teacher_service import get_course_teachers
    success, result = get_course_teachers(course_id)
    if success:
        return jsonify({
            "teacher_list": result,
            "count": len(result)
        }), 200
    return jsonify({"error": result}), 400


def handle_export_course_grades(staff_id, course_id, homework_ids=None, student_ids=None):
    """导出课程成绩为 Excel"""
    # 权限验证
    from app.util.auth import is_staff_in_course
    if not is_staff_in_course(staff_id, course_id):
        response = jsonify({"error": "无此课程权限"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 403
    
    try:
        from app.services.export_service import export_course_grades
        success, result = export_course_grades(
            course_id,
            homework_ids=homework_ids,
            student_ids=student_ids,
        )
        if success:
            # result 是 BytesIO 对象
            filename = f"课程成绩表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            response = send_file(
                result,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
            # 添加 CORS 头
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            return response
        else:
            # 导出失败，返回错误信息
            print(f"导出成绩失败: {result}")  # 调试日志
            response = jsonify({"error": result})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 400
    except Exception as e:
        # 捕获异常并返回详细错误信息
        import traceback
        error_msg = f"导出成绩时发生错误: {str(e)}"
        print(f"导出成绩异常: {error_msg}")
        print(traceback.format_exc())
        response = jsonify({"error": error_msg})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500


def handle_publish_homework_grades(user_id, course_id, homework_id, role="teacher"):
    """发布某次作业的成绩（支持教师和助教）"""
    # 统一权限验证：助教在教师端拥有和教师相同的权限
    # 不传 role 参数，让函数自动判断（会同时检查教师和助教关系）
    if not is_staff_in_course(user_id, course_id):
        return jsonify({"error": "无权限发布该课程成绩"}), 403
    
    success, message = publish_homework_grades_service(
        staff_id=user_id,
        course_id=course_id,
        homework_id=homework_id,
    )
    if success:
        return jsonify({"message": message}), 200
    return jsonify({"error": message}), 400
