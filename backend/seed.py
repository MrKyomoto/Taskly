from app import create_app
from app.extensions import db
from app.models import (
    Admin, Student, Staff, Course,
    StaffRole, StudentCourseRelation, StaffCourseRelation, CourseStatus
)
from werkzeug.security import generate_password_hash

app = create_app()

def seed_data():
    with app.app_context():
        print("正在清空旧数据库...")
        db.drop_all()
        db.create_all()
        
        print("开始填充初始数据...")

        # ==========================================
        # 1. 创建用户 (密码统一为 123456)
        # ==========================================
        default_pwd = generate_password_hash('123456')

        # --- 管理员 ---
        admin = Admin(
            username='admin',
            name='系统管理员',
            password_hash=default_pwd,
            phone='13800000000'
        )
        db.session.add(admin)
        db.session.flush()  # 获取 admin.id

        # --- 老师 ---
        t1 = Staff(
            staff_no='T001',
            name='张教授',
            email='zhang@ustc.edu.cn',
            phone='+8613800138001',
            role=StaffRole.teacher,
            password_hash=default_pwd
        )
        t2 = Staff(
            staff_no='T002',
            name='李老师',
            email='li@ustc.edu.cn',
            phone='+8613900139002',
            role=StaffRole.teacher,
            password_hash=default_pwd
        )
        db.session.add_all([t1, t2])
        db.session.flush()  # 获取 t1.id, t2.id

        # --- 学生 (20个) ---
        students = []
        for i in range(1, 21):
            s = Student(
                student_no=f'S2024{i:03d}',  # 例如 S2024001
                name=f'学生{i}号',
                email=f'student{i}@mail.ustc.edu.cn',
                phone=f'+861300000{i:04d}',
                password_hash=default_pwd
            )
            students.append(s)
            db.session.add(s)
        
        db.session.commit()
        print(f"[OK] 创建用户完成: 1 Admin, 2 Teachers, {len(students)} Students")

        # ==========================================
        # 2. 创建课程与关系
        # ==========================================
        c1 = Course(
            course_name='高等数学 (Advanced Math)',
            course_code='MATH2024',
            semester='2024 Fall',
            description='高等数学基础课程，涵盖微积分、线性代数等内容。',
            status=CourseStatus.approved
        )
        c2 = Course(
            course_name='计算机基础 (CS101)',
            course_code='CS101',
            semester='2024 Fall',
            description='计算机科学入门课程，学习编程基础和算法。',
            status=CourseStatus.approved
        )
        
        db.session.add_all([c1, c2])
        db.session.flush()  # 获取 c1.id, c2.id
        
        # 建立教师-课程关系
        from app.models import StaffCourseRelation
        sc1 = StaffCourseRelation(staff_id=t1.id, course_id=c1.id, role='主讲教师')
        sc2 = StaffCourseRelation(staff_id=t2.id, course_id=c2.id, role='主讲教师')
        db.session.add_all([sc1, sc2])
        
        # 让所有学生都选这两门课
        for s in students:
            scr1 = StudentCourseRelation(student_id=s.id, course_id=c1.id)
            scr2 = StudentCourseRelation(student_id=s.id, course_id=c2.id)
            db.session.add_all([scr1, scr2])
            
        db.session.commit()
        print("[OK] 创建课程完成: 2 Courses")
        
        print("\n数据统计：")
        print(f"  - 管理员: 1人")
        print(f"  - 教师: 2人")
        print(f"  - 学生: 20人")
        print(f"  - 课程: 2门")
        print("\n数据库初始化完毕！")
        print("\n测试账号：")
        print("  - 管理员: admin / 123456")
        print("  - 教师1: T001 / 123456")
        print("  - 教师2: T002 / 123456")
        print("  - 学生: S2024001 ~ S2024020 / 123456")

if __name__ == '__main__':
    seed_data()
