import os
import platform
import sys

from utils.public_func import get_local_ip, generate_project_path

"""
请移步 `development.py` 或 `production.py` 修改配置, 配置名称字母均大写才有效
"""

# 项目主目录
BASE_DIR: str = generate_project_path()
sys.path.insert(0, BASE_DIR)

# 当前操作系统
SYSTEM: str = platform.system()

# 是否为windows
IS_WINDOWS: bool = SYSTEM == "Windows"

# 本机IP
LOCAL_HOST: str = get_local_ip()

# 后端端口
WSGI_PORT: int = 8080

# 是否Debug
DEBUG: bool = False

# 是否保存系统日志
SAVE_SYSTEM_LOG: bool = False

# 是否保存共享日志(包含用户浏览/下载记录)
SAVE_SHARER_LOG: bool = False

# 日志保存路径
LOGS_PATH: str = os.path.join(BASE_DIR, "logs")

# 下载目录路径
DOWNLOAD_DIR: str = os.path.join(BASE_DIR, "Download")
