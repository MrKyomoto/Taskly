"""
配置类，存储项目所有配置参数：
- 数据库连接地址（SQLALCHEMY_DATABASE_URI）
- JWT 密钥（JWT_SECRET_KEY）
- 其他环境变量（如调试模式开关）
"""
import os
BACKEND_SERVER_IP = '127.0.0.1'
BACKEND_SERVER_PORT = 8000
BACKEND_DEBUG_MODE = True


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql:///root:root@127.0.0.1:3306/university_homework_system'
    # 自动更新追踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 手动保存数据库提交的改动
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    # TODO(这是啥,我不懂)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret'
