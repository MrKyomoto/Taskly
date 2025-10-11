from app.config import BACKEND_SERVER_IP, BACKEND_SERVER_PORT, BACKEND_DEBUG_MODE
from app import create_app

app = create_app()

# 创建数据库表（首次运行时）
# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    app.run(
        host=BACKEND_SERVER_IP,
        port=BACKEND_SERVER_PORT,
        debug=BACKEND_DEBUG_MODE,
    )  # 生产环境需关闭debug
