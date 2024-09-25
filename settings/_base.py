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
THEME_OPACITY: int = 100

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
	border: none;
	color: rgb(%(TextColor)s)
}

/* ///////////////////////////////////////////////////////////////////////////////
Background Image */
QComboBox::drop-down {
	background-image: url(:/icons/images/icon/%(DirName)s/down.png);
}
QCheckBox::indicator:checked {
	background-image: url(:/icons/images/icon/%(DirName)s/check.png);
}
#homeButton {
	background-image: url(:/icons/images/icon/%(DirName)s/home.png)
}
#serverButton {
	background-image: url(:/icons/images/icon/%(DirName)s/server.png)
}
#clientButton {
	background-image: url(:/icons/images/icon/%(DirName)s/client.png)
}
#downloadButton {
	background-image: url(:/icons/images/icon/%(DirName)s/download.png)
}
#settingButton {
	background-image: url(:/icons/images/icon/%(DirName)s/setting.png)
}
#minimizeButton {
	background-image: url(:/icons/images/icon/%(DirName)s/minimize.png)
}
#maximizeRestoreButton {
	background-image: url(:/icons/images/icon/%(DirName)s/maximize.png)
}
#closeAppButton {
	background-image: url(:/icons/images/icon/%(DirName)s/close.png);
}
#sharePathButton {
	background-image: url(:/icons/images/icon/%(DirName)s/folder.png)
}
#logPathButton {
	background-image: url(:/icons/images/icon/%(DirName)s/folder.png)
}
#downloadPathButton {
	background-image: url(:/icons/images/icon/%(DirName)s/folder.png)
}
#shareProjectButton {
	qproperty-icon: url(:/icons/images/icon/%(DirName)s/share.png);
	qproperty-iconSize: 16px 16px;
}
#browseProjectButton {
	qproperty-icon: url(:/icons/images/icon/%(DirName)s/browse.png);
	qproperty-iconSize: 16px 16px;
}

/* ///////////////////////////////////////////////////////////////////////////////
QLineEdit */
QLineEdit {
    background-color: rgba(%(BaseBgColor)s, %(ThemeOpacity).2f);
}

/* ///////////////////////////////////////////////////////////////////////////////
QPushButton */
QPushButton {
	border: 2px solid rgb(%(LightColor)s);
	border-radius: 5%%
}
QPushButton:hover {
	border: 2px solid rgb(%(BaseColor)s);
}
QPushButton:pressed {
	background-color: rgb(%(BaseColor)s);
}
QPushButton:disabled {
	background-color: rgb(%(Deep2BgColor)s);
	border: none;
}

/* ///////////////////////////////////////////////////////////////////////////////
QComboBox */
QComboBox {
	border-radius: 5%%;
	border: 2px solid rgb(%(LightColor)s);
	padding: 5px;
	padding-left: 10px;
	background-color: rgba(%(BaseBgColor)s, %(ThemeOpacity).2f)
}
QComboBox:hover {
	border: 2px solid rgb(%(BaseColor)s);
}
QComboBox::drop-down {
	subcontrol-origin: padding;
	subcontrol-position: top right;
	width: 25px;
	border-left-width: 1px;
	border-left-color: rgb(%(BaseColor)s);
	border-left-style: solid;
	background-position: center;
	background-repeat: no-reperat;
}
QComboBox QAbstractItemView {
    border-radius: 5%%;
	color: rgb(%(TextColor)s);
	border: 2px solid rgb(%(BaseColor)s);
	border-top: none;
	outline: 0px;
	padding: 5px;
	background-color: rgba(%(BaseBgColor)s, %(ThemeOpacity).2f);
	selection-background-color: rgb(%(BaseColor)s)
}

/* ///////////////////////////////////////////////////////////////////////////////
QTableWidget */
QTableWidget {
	background-color: rgba(%(BaseBgColor)s, %(ThemeOpacity).2f);
	padding: 10px;
	border-radius: 5px;
	gridline-color: rgb(%(LightColor)s);
	border-top: 2px solid rgb(%(SpecialHovColor)s);
	border-bottom: 2px solid rgb(%(BaseColor)s);
}
QTableWidget::item {
	padding-left: 5px;
	padding-right: 5px;
	gridline-color: rgb(%(BaseBgColor)s);
}
QTableWidget::item:selected {
	background-color: rgb(%(LightColor)s);
}
QHeaderView::section {
	background-color: rgb(%(LightBgColor)s);
	max-width: 100px;
	border: none;
	border-style: none;
	font-size: 15px;
	font-weight: bold;
}
QHeaderView::section:horizontal {
	border: 1px solid rgb(%(BaseColor)s);
	background-color: rgb(%(LightBgColor)s);
	padding: 3px;
	border-top-left-radius: 7px;
	border-top-right-radius: 7px;
}
QHeaderView::section:vertical {
	border: 1px solid rgb(%(DeepColor)s);
}

/* ///////////////////////////////////////////////////////////////////////////////
QScrollBar */
QScrollBar:horizontal {
	border: none;
    background: rgb(%(BaseBgColor)s);
    height: 8px;
    margin: 0 21px 0 21px;
	border-radius: 0px;
}
QScrollBar:vertical {
	border: none;
    background: rgb(%(BaseBgColor)s);
    width: 8px;
    margin: 21px 0 21px 0;
	border-radius: 0px;
}
QScrollBar::handle:horizontal {
	background: rgb(%(BaseColor)s);
    min-width: 25px;
    border-radius: 4px
}
QScrollBar::handle:vertical {
    background: rgb(%(BaseColor)s);
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
	border: 2px solid rgb(%(BaseColor)s);
	width: 15px;
	height: 15px;
	border-radius: 9px;
	background: rgba(%(BaseBgColor)s, %(ThemeOpacity).2f);
}
QCheckBox::indicator:hover {
	background-color: rgb(%(SpecialHovColor)s);
}

/* ///////////////////////////////////////////////////////////////////////////////
QSlider */
QSlider::groove:horizontal {
    border-radius: 4px;
    height: 8px;
	margin: 0px;
	background-color: rgb(%(DeepBgColor)s);
	border: 1px solid rgb(%(LightColor)s);
}
QSlider::groove:horizontal:hover {
	border: 2px solid rgb(%(BaseColor)s);
	border-radius: 5px
}
QSlider::sub-page::horizontal {
    background-color: rgb(%(BaseColor)s);
    border-radius: 4px
}
QSlider::handle:horizontal {
    background-color: rgb(%(LightColor)s);
    border: none;
    height: 20px;
    width: 20px;
    margin: -6px 0px;
	border-radius: 10px;
}
QSlider::handle:horizontal:hover {
    background-color: rgb(%(DeepColor)s);
}

/* ///////////////////////////////////////////////////////////////////////////////
QTooltip */
QToolTip {
	color: rgb(%(BaseColor)s);
	background-color: rgba(%(BaseBgColor)s, %(ThemeOpacity).2f);
	border: 1px solid rgb(%(BaseColor)s);
	background-image: none;
	background-position: left center;
    background-repeat: no-repeat;
	border: none;
	border-left: 3px solid rgb(%(BaseColor)s);
	text-align: left;
	padding-left: 8px;
	margin: 0px;
}

/* ///////////////////////////////////////////////////////////////////////////////
AppBg */
#AppBg {
	background-color: rgba(%(BaseBgColor)s, %(ThemeOpacity).2f);
	border: 1px solid rgb(%(BaseColor)s);
}

/* ///////////////////////////////////////////////////////////////////////////////
Left Menu Box */
#leftMenuBox {
	background-color: rgba(%(DeepBgColor)s, %(ThemeOpacity).2f);
}
#leftMenuFrame {
	padding-bottom: 5px;
}
#leftBottomBox {
	padding: 0 5px;
}
#leftMenuBox .QPushButton:hover {
	background-color: rgb(%(SpecialHovColor)s);
}
#leftMenuBox .QPushButton:pressed {
	background-color: rgb(%(BaseColor)s);
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
	background-color: rgba(%(BaseBgColor)s, %(ThemeOpacity).2f);
}

/* ///////////////////////////////////////////////////////////////////////////////
Extra Top Box */
#extraTopBox {
	background-color: rgba(%(BaseColor)s, %(ThemeOpacity).2f);
	padding: 0 10px;
}
#extraTopBox .QLabel {
	color: rgb(%(SpecialHovColor)s);
	font-size: 18px;
}
#extraTopBox .QPushButton {
	border: none;
}
#extraTopBox .QPushButton:hover {
	border: none;
	background-color: rgb(%(DeepColor)s);
}
#extraTopBox .QPushButton:pressed {
	background-color: rgb(%(SpecialHovColor)s);
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
	border: 1px solid rgb(%(BaseColor)s);
	border-radius: 3%%;
	margin-right: 10px;
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
    background-color: rgb(64, 158, 255);
}
#extraContentBox #Red::indicator {
    background-color: rgb(241, 80, 80);
}
#extraContentBox #Orange::indicator {
    background-color: rgb(240, 165, 0);
}
#extraContentBox #Yellow::indicator {
    background-color: rgb(230, 200, 50);
}
#extraContentBox #Green::indicator {
    background-color: rgb(0, 180, 0);
}
#extraContentBox #Cyan::indicator {
    background-color: rgb(30, 180, 180);
}
#extraContentBox #Blue::indicator {
    background-color: rgb(90, 90, 220);
}
#extraContentBox #Purple::indicator {
    background-color: rgb(128, 0, 128);
}

/* ///////////////////////////////////////////////////////////////////////////////
Extra Bottom Box */
#extraBottomBox #saveSettingButton {
	border: none;
	background-color: rgb(%(BaseColor)s);
	color: rgb(%(SpecialHovColor)s);
}
#extraBottomBox #saveSettingButton:hover {
	border: none;
	background-color: rgb(%(DeepColor)s);
}
#extraBottomBox #saveSettingButton:pressed {
	border: 2px solid rgb(%(SpecialHovColor)s);
}
#extraBottomBox #cancelSettingButton {
	border: none;
	background-color: rgb(%(DeepBgColor)s);
	color: rgb(%(TextColor)s);
}
#extraBottomBox #cancelSettingButton:hover {
	border: none;
	background-color: rgb(%(Deep2BgColor)s);
}
#extraBottomBox #cancelSettingButton:pressed {
	border: 2px solid rgb(%(SpecialHovColor)s);
}

/* ///////////////////////////////////////////////////////////////////////////////
Content Box */
/* ///////////////////////////////////////////////////////////////////////////////
Content Top Box */
#contentTopBox {
	background-color: rgba(%(DeepBgColor)s, %(ThemeOpacity).2f);
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
	background-color: rgb(%(SpecialHovColor)s);
}
#contentTopBox .QPushButton:pressed {
	border: none;
	background-color: rgb(%(BaseColor)s);
}

/* ///////////////////////////////////////////////////////////////////////////////
Content Bottom Box */
#contentBottomBox {
	background-color: rgba(%(BaseBgColor)s, %(ThemeOpacity).2f);
}

/* ///////////////////////////////////////////////////////////////////////////////
Content stackedWidget Box */
/* ///////////////////////////////////////////////////////////////////////////////
Content server Box */
#createShareButton {
	border: none;
	border-radius: 13%%;
	background-color: rgb(%(BaseColor)s);
	color: rgb(%(SpecialHovColor)s);
}
#createShareButton:hover {
	border: none;
	background-color: rgb(%(DeepColor)s);
}
#createShareButton:pressed {
	border: 2px solid rgb(%(SpecialHovColor)s);
}
#sharePathFrame .QLineEdit {
	border: 1px solid rgb(%(BaseColor)s);
	border-radius: 5%%;
	margin-right: 10px;
	padding-left: 5px;
}

/* ///////////////////////////////////////////////////////////////////////////////
Content client Box */
#clientParamFrame .QLineEdit {
	border: 1px solid rgb(%(BaseColor)s);
	border-radius: 5%%;
	padding-left: 5px;
}

/* ///////////////////////////////////////////////////////////////////////////////
Content Bottom Bar */
#contentBottomBar {
	background-color: rgba(%(DeepBgColor)s, %(ThemeOpacity).2f);
	color: rgb(97, 97, 97);
	padding: 0 10px;
}
"""
