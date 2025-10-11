from app.config import BACKEND_SERVER_IP, BACKEND_SERVER_PORT, BACKEND_DEBUG_MODE
from app import create_app

app = create_app()

# 创建数据库表（首次运行时）
# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    app.run(debug=BACKEND_DEBUG_MODE)
