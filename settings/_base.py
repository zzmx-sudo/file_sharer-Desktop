import os
import sys

from utils.public_func import (
    get_system,
    get_local_ip,
    generate_project_path,
    generate_product_version,
)
from model.public_types import ThemeColor, ColorCardStruct

"""
请移步 `development.py` 或 `production.py` 修改配置, 配置名称字母均大写才有效
"""

# 软件版本
VERSION: str = generate_product_version()

# 项目主目录
BASE_DIR: str = generate_project_path()
sys.path.insert(0, BASE_DIR)

# 当前操作系统
SYSTEM: str = get_system()

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

# 主题颜色
THEME_COLOR: ThemeColor = ThemeColor.Default

# 背景透明度
THEME_TRANSPARENCY: int = 100

# 全局色卡
COLOR_CARD: ColorCardStruct = ColorCardStruct.dispatch()

# 基本样式
BASIC_QSS = """
/* ///////////////////////////////////////////////////////////////////////////////
Global */
* {
	margin: 0;
	padding: 0;
	font-size: 14px;
	font-family: "KaiTi";
	background-position: center;
	background-repeat: no-reperat;
}

/* ///////////////////////////////////////////////////////////////////////////////
QWidget */
QWidget{
	color: rgb(0, 0, 0);
	border: none;
}

/* ///////////////////////////////////////////////////////////////////////////////
QComboBox */
QComboBox {
	background-color: %(QComboBoxBgColor)s;
	border-radius: 5%%;
	border: 2px solid #409eff;
	padding: 5px;
	padding-left: 10px;
}
QComboBox:hover {
	background-color: %(QComboBoxBorderColor)s;
}
QComboBox::drop-down {
	subcontrol-origin: padding;
	subcontrol-position: top right;
	width: 25px;
	border-left-width: 1px;
	border-left-color: #409eff;
	border-left-style: solid;
	border-top-right-radius: 3px;
	border-bottom-right-radius: 3px;
	background-image: url(:/icons/images/icon/down.png);
	background-position: center;
	background-repeat: no-reperat;
}
QComboBox::drop-down:hover {
	background-image: url(:/icons/images/icon/down-active.png);
}
QComboBox QAbstractItemView {
	color: rgb(0, 0, 0);
	background-color: rgb(236, 236, 236);
	padding: 10px;
	selection-background-color: #409eff;
}

/* ///////////////////////////////////////////////////////////////////////////////
QTableWidget */
QTableWidget {
	background-color: rgb(247, 247, 247);
	padding: 10px;
	border-radius: 5px;
	gridline-color: rgb(236, 236, 236);
	border-top: 2px solid #ffffff;
	border-bottom: 2px solid #409eff;
}
QTableWidget::item {
	padding-left: 5px;
	padding-right: 5px;
	gridline-color: rgb(236, 236, 236);
}
QTableWidget::item:selected {
	background-color: rgb(126, 199, 255);
}
QTableWidget::horizontalHeader {
	background-color: rgb(247, 247, 247);
}
QHeaderView::section {
	background-color: rgb(247, 247, 247);
	max-width: 100px;
	border: none;
	border-style: none;
}
QHeaderView::section:horizontal {
	border: 1px solid #409eff;
	background-color: rgb(247, 247, 247);
	padding: 3px;
	border-top-left-radius: 7px;
	border-top-right-radius: 7px;
}
QHeaderView::section:vertical {
	border: 1px solid rgb(44, 49, 60);
}

/* ///////////////////////////////////////////////////////////////////////////////
QScrollBar */
QScrollBar:horizontal {
	border: none;
    background: rgb(236, 236, 236);
    height: 8px;
    margin: 0 21px 0 21px;
	border-radius: 0px;
}
QScrollBar:vertical {
	border: none;
    background: rgb(236, 236, 236);
    width: 8px;
    margin: 21px 0 21px 0;
	border-radius: 0px;
}
QScrollBar::handle:horizontal {
	background: #409eff;
    min-width: 25px;
    border-radius: 4px
}
QScrollBar::handle:vertical {
    background: #409eff;
    min-height: 25px;
    border-radius: 4px
}
QScrollBar::add-line:horizontal {
	border: none;
    background: rgb(100, 100, 100);
    width: 20px;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    subcontrol-position: right;
    subcontrol-origin: margin;
}
QScrollBar::add-line:vertical {
    border: none;
    background: rgb(100, 100, 100);
    height: 20px;
    border-bottom-left-radius: 4px;
    border-bottom-right-radius: 4px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:horizontal {
	border: none;
    background: rgb(100, 100, 100);
    width: 20px;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    subcontrol-position: left;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:vertical {
    border: none;
    background: rgb(100, 100, 100);
    height: 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}
QScrollBar::up-arrow:vertical, QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:vertical, QScrollBar::down-arrow:horizontal {
	background: none;
}
QScrollBar::add-page:vertical, QScrollBar::add-page:horizontal, QScrollBar::sub-page:vertical, QScrollBar::sub-page:horizontal {
	background: none;
}

/* ///////////////////////////////////////////////////////////////////////////////
QCheckBox */
QCheckBox {
	spacing: 10px;
}
QCheckBox::indicator {
	border: 2px solid #409eff;
	width: 15px;
	height: 15px;
	border-radius: 9px;
	background: rgb(236, 236, 236);
}
QCheckBox::indicator:hover {
	background-color: #ffffff;
}
QCheckBox::indicator:checked {
	background-image: url(:/icons/images/icon/check.png);
}

/* ///////////////////////////////////////////////////////////////////////////////
QTooltip */
QToolTip {
	color: #409eff;
	background-color: rgba(236, 236, 236, 180);
	border: 1px solid #409eff;
	background-image: none;
	background-position: left center;
    background-repeat: no-repeat;
	border: none;
	border-left: 3px solid #409eff;
	text-align: left;
	padding-left: 8px;
	margin: 0px;
}

/* ///////////////////////////////////////////////////////////////////////////////
AppBg */
#AppBg {
	background-color: #ffffff;
	border: 1px solid #409eff;
}

/* ///////////////////////////////////////////////////////////////////////////////
QPushButton */
QPushButton {
	border: 2px solid rgb(126, 199, 255);
	border-radius: 5%%;
}
QPushButton:hover {
	border: 2px solid #409eff;
}
QPushButton:pressed {
	background-color: #409eff;
}
QPushButton:disabled {
	background-color: rgb(200, 200, 200);
	border: none;
}

/* ///////////////////////////////////////////////////////////////////////////////
Left Menu Box */
#leftMenuBox {
	background-color: rgb(222, 222, 222);
}
#leftMenuFrame {
	padding-bottom: 5px;
}
#leftBottomBox {
	padding: 0 5px;
}
#leftMenuBox .QPushButton:hover {
	background-color: #ffffff;
}
#leftMenuBox .QPushButton:pressed {
	background-color: #409eff;
}
#leftTopBox .QPushButton {
	border: none;
	border-radius: 0;
}
#settingButton {
	border: none;
}

/* ///////////////////////////////////////////////////////////////////////////////
Extra Box */
#extraBox {
	background-color: rgb(236, 236, 236);
}
/* ///////////////////////////////////////////////////////////////////////////////
Extra Top Box */
#extraTopBox {
	background-color: rgb(64, 158, 255);
	padding: 0 10px;
}
#extraTopBox .QLabel {
	color: #ffffff;
	font-size: 18px;
}
#extraTopBox .QPushButton {
	border: none;
}
#extraTopBox .QPushButton:hover {
	border: none;
	background-color: rgb(85, 170, 255);
}
#extraTopBox .QPushButton:pressed {
	background-color: #ffffff;
}
/* ///////////////////////////////////////////////////////////////////////////////
Extra Content Box */
#extraContentBox {
	margin: 10px 0;
}
#extraContentBox #saveShareBox, #saveSystemBox {
	padding-left: 15px;
}
#downloadPathBox, #logPathBox {
	padding: 10px;
}
#extraContentBox .QLabel {
	margin-bottom: 5px;
}
#extraContentBox .QLineEdit {
	border: 1px solid #409eff;
	border-radius: 3%%;
	margin-right: 10px;
	background-color: rgb(236, 236, 236);
	font: 12px "JetBrains Mono";
}
#extraContentBox .QRadioButton::indicator {
    width: 22px;
    height: 22px;
    margin: 2px;
    border-radius: 5px;
}
#extraContentBox .QRadioButton::indicator:hover {
    margin: 0px;
    width: 26px;
    height: 26px;
}
#extraContentBox .QRadioButton::indicator:checked {
    width: 24px;
    height: 24px;
    margin: 0px;
    border: 2px solid black;
}
#extraContentBox #Default::indicator {
    background-color: #409eff;
}
#extraContentBox #Red::indicator {
    background-color: red;
}
#extraContentBox #Orange::indicator {
    background-color: orange;
}
#extraContentBox #Yellow::indicator {
    background-color: yellow;
}
#extraContentBox #Green::indicator {
    background-color: green;
}
#extraContentBox #Cyan::indicator {
    background-color: cyan;
}
#extraContentBox #Blue::indicator {
    background-color: blue;
}
#extraContentBox #Purple::indicator {
    background-color: purple;
}

/* ///////////////////////////////////////////////////////////////////////////////
Extra Bottom Box */
#extraBottomBox #saveSettingButton {
	border: none;
	background-color: rgb(42, 188, 255);
	color: #ffffff;
}
#extraBottomBox #saveSettingButton:hover {
	border: none;
	background-color: rgb(64, 158, 255);
}
#extraBottomBox #saveSettingButton:pressed {
	border: 2px solid #ffffff;
}
#extraBottomBox #cancelSettingButton {
	border: none;
	background-color: rgb(217, 217, 217);
	color: rgb(0, 0, 0);
}
#extraBottomBox #cancelSettingButton:hover {
	border: none;
	background-color: rgb(184, 184, 184);
}
#extraBottomBox #cancelSettingButton:pressed {
	border: 2px solid #ffffff;
}

/* ///////////////////////////////////////////////////////////////////////////////
Content Box */
/* ///////////////////////////////////////////////////////////////////////////////
Content Top Box */
#contentTopBox {
	background-color: rgb(236, 236, 236);
	padding: 0 10px 0 20px;
}
#contentTitleBox .QLabel {
	font: 14px "JetBrains Mono";
}
#contentTopBox .QPushButton {
	border: none;
}
#contentTopBox .QPushButton:hover {
	border: none;
	background-color: #ffffff;
}
#contentTopBox .QPushButton:pressed {
	border: none;
	background-color: #409eff;
}
/* ///////////////////////////////////////////////////////////////////////////////
Content Bottom Box */
#contentBottomBox {
	background-color: rgb(246, 246, 246);
}
/* ///////////////////////////////////////////////////////////////////////////////
Content stackedWidget Box */
/* ///////////////////////////////////////////////////////////////////////////////
Content server Box */
#server {
	background-color: rgb(246, 246, 246);
}
#createShareButton {
	border: none;
	border-radius: 13%%;
	background-color: rgb(42, 188, 255);
	color: #ffffff;
}
#createShareButton:hover {
	border: none;
	background-color: rgb(64, 158, 255);
}
#createShareButton:pressed {
	border: 2px solid #ffffff;
}
#sharePathFrame .QLineEdit {
	border: 1px solid #409eff;
	border-radius: 5%%;
	margin-right: 10px;
}
/* ///////////////////////////////////////////////////////////////////////////////
Content client Box */
#clientParamFrame .QLineEdit {
	border: 1px solid #409eff;
	border-radius: 5%%;
	padding-left: 10px;
}
#fileListFrame .QTableWidget::item:selected {
	background-color: rgb(247, 247, 247);
}
/* ///////////////////////////////////////////////////////////////////////////////
Content Bottom Bar */
#contentBottomBar {
	background-color: rgb(236, 236, 236);
	color: rgb(97, 97, 97);
	padding: 0 10px;
}
"""
