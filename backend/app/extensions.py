"""
统一管理 Flask 扩展实例（避免循环导入问题）：
- db：SQLAlchemy 实例（数据库 ORM）
- jwt：JWTManager 实例（身份认证）
- cors：CORS 实例（解决跨域）
"""
# 统一管理 Flask 扩展，避免循环导入
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import pymysql
pymysql.install_as_MySQLdb()

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()  # 解决前端跨域问题
