"""
配置文件
"""
import os
from datetime import timedelta

# 文件上传配置
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 图片压缩配置
DEFAULT_QUALITY = 85  # 默认压缩质量
MIN_QUALITY = 60     # 最小压缩质量
MAX_QUALITY = 95     # 最大压缩质量
MAX_WIDTH = 1920     # 最大宽度
MAX_HEIGHT = 1080    # 最大高度

# 文件清理配置
FILE_RETENTION_DAYS = 7  # 文件保留天数
CLEANUP_INTERVAL = timedelta(hours=24)  # 清理间隔

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'app.log'

# 安全配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # 建议使用环境变量
SESSION_COOKIE_SECURE = True
PERMANENT_SESSION_LIFETIME = timedelta(days=1) 