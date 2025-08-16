"""
应用工厂函数，负责创建和配置 Flask 应用：
- 加载配置（Config 类）
- 初始化扩展（数据库、JWT、CORS 等）
- 注册路由蓝图（routers 中的模块）
"""
from flask import Flask
from app.config import Config
from app.extensions import db, jwt
from app.routers import student, staff, admin, course, homework


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # db && jwt 我不知道是什么,先存疑
    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(student.bp)
    app.register_blueprint(staff.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(course.bp)
    app.register_blueprint(homework.bp)

    return app
