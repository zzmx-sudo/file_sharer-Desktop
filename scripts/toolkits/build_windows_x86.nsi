Unicode true

; 安装程序初始定义常量
!define PRODUCT_NAME "FileSharer"
!define PRODUCT_VERSION "v0.1.0"
!define PRODUCT_PUBLISHER "大宝天天见丶"
!define PRODUCT_WEB_SITE "https://github.com/zzmx-sudo/file_sharer-Desktop"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\file-sharer.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PROJECT_DIR "F:\GitSource\file_sharer-Desktop"
!define INSTALLER_NAME "${PROJECT_DIR}\build\installer\file_sharer-desktop_${PRODUCT_VERSION}-win_x86.exe"

SetCompressor lzma
SetCompressorDictSize 32

; ------ MUI 现代界面定义 (1.67 版本以上兼容) ------
!include "MUI.nsh"

; MUI 预定义常量
!define MUI_ABORTWARNING
!define MUI_ICON "${PROJECT_DIR}\build\file-sharer\icon.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; 语言选择窗口常量设置
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

; 欢迎页面
!insertmacro MUI_PAGE_WELCOME
; 许可协议页面
!define MUI_LICENSEPAGE_CHECKBOX
!insertmacro MUI_PAGE_LICENSE "${PROJECT_DIR}\licenses\license.txt"
; 安装目录选择页面
!insertmacro MUI_PAGE_DIRECTORY
; 安装过程页面
!insertmacro MUI_PAGE_INSTFILES
; 安装完成页面
!define MUI_FINISHPAGE_RUN "$INSTDIR\file-sharer.exe"
!insertmacro MUI_PAGE_FINISH

; 安装卸载过程页面
!insertmacro MUI_UNPAGE_INSTFILES

; 安装界面包含的语言设置
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装预释放文件
!insertmacro MUI_RESERVEFILE_LANGDLL
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
; ------ MUI 现代界面定义结束 ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
!system 'mkdir "${INSTALLER_NAME}\.."'
OutFile "${INSTALLER_NAME}"
InstallDir "$PROGRAMFILES\FileSharer"
InstallDirRegKey HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File "${PROJECT_DIR}\build\file-sharer\file-sharer.exe"
  CreateDirectory "$SMPROGRAMS\FileSharer"
  CreateShortCut "$SMPROGRAMS\FileSharer\FileSharer.lnk" "$INSTDIR\file-sharer.exe" "" "$INSTDIR\icon.ico"
  CreateShortCut "$DESKTOP\FileSharer.lnk" "$INSTDIR\file-sharer.exe" "" "$INSTDIR\icon.ico"
  SetOverwrite off
  File "${PROJECT_DIR}\build\file-sharer\pyproject.toml"
  File "${PROJECT_DIR}\build\file-sharer\file_sharing_backups.json"
  SetOverwrite ifnewer
  File /r "${PROJECT_DIR}\build\file-sharer\*.*"
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\home.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\FileSharer\Website.lnk" "$INSTDIR\home.url"
  CreateShortCut "$SMPROGRAMS\FileSharer\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\file-sharer.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\file-sharer.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

#-- 根据 NSIS 脚本编辑规则，所有 Function 区段必须放置在 Section 区段之后编写，以避免安装程序出现未可预知的问题。--#

Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

/******************************
 *  以下是安装程序的卸载部分  *
 ******************************/

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\file_sharing_backups.json"
  Delete "$INSTDIR\pyproject.toml"
  Delete "$INSTDIR\file-sharer.exe"

  Delete "$SMPROGRAMS\FileSharer\Uninstall.lnk"
  Delete "$SMPROGRAMS\FileSharer\Website.lnk"
  Delete "$DESKTOP\FileSharer.lnk"
  Delete "$SMPROGRAMS\FileSharer\FileSharer.lnk"

  RMDir "$SMPROGRAMS\FileSharer"

  RMDir /r "$INSTDIR\yarl"
  RMDir /r "$INSTDIR\PyQt5"
  RMDir /r "$INSTDIR\pydantic_core"
  RMDir /r "$INSTDIR\psutil"
  RMDir /r "$INSTDIR\multidict"
  RMDir /r "$INSTDIR\logs"
  RMDir /r "$INSTDIR\frozenlist"
  RMDir /r "$INSTDIR\charset_normalizer"
  RMDir /r "$INSTDIR\certifi"
  RMDir /r "$INSTDIR\attrs-23.1.0.dist-info"
  RMDir /r "$INSTDIR\aiohttp"

  RMDir /r "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd

#-- 根据 NSIS 脚本编辑规则，所有 Function 区段必须放置在 Section 区段之后编写，以避免安装程序出现未可预知的问题。--#

Function un.onInit
!insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "您确实要完全移除 $(^Name) ，及其所有的组件？" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) 已成功地从您的计算机移除。"
FunctionEnd
