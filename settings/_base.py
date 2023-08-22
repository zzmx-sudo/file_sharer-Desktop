import os
import platform

"""
请移步 `development.py` 或 `production.py` 修改配置, 配置名称字母均大写才有效
"""

# 项目主目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 当前操作系统
SYSTEM = platform.system()

# 是否为windows
IS_WINDOWS = SYSTEM == "Windows"

# 后端端口
WSGI_PORT = 8080

# 是否Debug
DEBUG = False

# 是否保存系统日志
SAVE_SYSTEM_LOG = False

# 是否保存用户浏览/下载日志
SAVE_USER_LOG = False

# 日志保存路径
LOGS_PATH = os.path.join(BASE_DIR, "logs")
if not os.path.isdir(LOGS_PATH): os.mkdir(LOGS_PATH)