; ��װ�����ʼ���峣��
!define PRODUCT_NAME "�������ļ���������"
!define PRODUCT_VERSION "0.0.1"
!define PRODUCT_PUBLISHER "�������ؼ"
!define PRODUCT_WEB_SITE "https://github.com/zzmx-sudo/file_sharer-Desktop"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\file-sharer.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PROJECT_DIR "F:\GitSource\file_sharer-Desktop"
!define INSTALLER_NAME "${PROJECT_DIR}\build\installer\file-sharer.exe"

SetCompressor lzma

; ------ MUI �ִ����涨�� (1.67 �汾���ϼ���) ------
!include "MUI.nsh"

; MUI Ԥ���峣��
!define MUI_ABORTWARNING
!define MUI_ICON "${PROJECT_DIR}\build\file-sharer\icon.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; ����ѡ�񴰿ڳ�������
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

; ��ӭҳ��
!insertmacro MUI_PAGE_WELCOME
; ���Э��ҳ��
!define MUI_LICENSEPAGE_CHECKBOX
!insertmacro MUI_PAGE_LICENSE "${PROJECT_DIR}\build\file-sharer\license.txt"
; ��װĿ¼ѡ��ҳ��
!insertmacro MUI_PAGE_DIRECTORY
; ��װ����ҳ��
!insertmacro MUI_PAGE_INSTFILES
; ��װ���ҳ��
!define MUI_FINISHPAGE_RUN "$INSTDIR\file-sharer.exe"
!insertmacro MUI_PAGE_FINISH

; ��װж�ع���ҳ��
!insertmacro MUI_UNPAGE_INSTFILES

; ��װ�����������������
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"

; ��װԤ�ͷ��ļ�
!insertmacro MUI_RESERVEFILE_LANGDLL
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
; ------ MUI �ִ����涨����� ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
!system 'mkdir "${INSTALLER_NAME}\.."'
OutFile "${INSTALLER_NAME}"
InstallDir "$PROGRAMFILES\�������ļ���������"
InstallDirRegKey HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File "${PROJECT_DIR}\build\file-sharer\file-sharer.exe"
  CreateDirectory "$SMPROGRAMS\�������ļ���������"
  CreateShortCut "$SMPROGRAMS\�������ļ���������\�������ļ���������.lnk" "$INSTDIR\file-sharer.exe"
  CreateShortCut "$DESKTOP\�������ļ���������.lnk" "$INSTDIR\file-sharer.exe"
  SetOverwrite off
  File "${PROJECT_DIR}\build\file-sharer\pyproject.toml"
  File "${PROJECT_DIR}\build\file-sharer\file_sharing_backups.json"
  SetOverwrite ifnewer
  File /r "F:\GitSource\file_sharer-Desktop\build\file-sharer\*.*"
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\�������ļ���������\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\�������ļ���������\Uninstall.lnk" "$INSTDIR\uninst.exe"
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

#-- ���� NSIS �ű��༭�������� Function ���α�������� Section ����֮���д���Ա��ⰲװ�������δ��Ԥ֪�����⡣--#

Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

/******************************
 *  �����ǰ�װ�����ж�ز���  *
 ******************************/

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\file_sharing_backups.json"
  Delete "$INSTDIR\pyproject.toml"
  Delete "$INSTDIR\file-sharer.exe"

  Delete "$SMPROGRAMS\�������ļ���������\Uninstall.lnk"
  Delete "$SMPROGRAMS\�������ļ���������\Website.lnk"
  Delete "$DESKTOP\�������ļ���������.lnk"
  Delete "$SMPROGRAMS\�������ļ���������\�������ļ���������.lnk"

  RMDir "$SMPROGRAMS\�������ļ���������"

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

#-- ���� NSIS �ű��༭�������� Function ���α�������� Section ����֮���д���Ա��ⰲװ�������δ��Ԥ֪�����⡣--#

Function un.onInit
!insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "��ȷʵҪ��ȫ�Ƴ� $(^Name) ���������е������" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) �ѳɹ��ش����ļ�����Ƴ���"
FunctionEnd
