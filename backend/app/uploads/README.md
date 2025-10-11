- 用于存储上传的图片，服务于 backend/app/util/image_upload
  - 相当于一个图床


```
uploads/
└── course/                  # 顶级目录：按课程组织
    └── {course_id}/         # 课程ID（如3）
        └── hw/              # 作业目录
            └── {hw_id}/     # 作业ID（全局主键，如5，对应Homework.id）
                ├── post/    # 作业发布的图片资源（老师上传，共享）
                │   ├── cover.png       # 老师上传的作业封面图
                │   └── example1.jpg    # 老师上传的示例图
                └── submit/  # 学生提交的作业资源
                    └── student/
                        ├── {student_id1}/  # 学生1提交的图片
                        │   ├── answer1.png
                        │   └── answer2.jpg
                        └── {student_id2}/  # 学生2提交的图片
                            └── answer.png
```
