@echo off

@rem 先使用pyinstaller打包源码
::python虚拟环境路径,若无请配空值
set PYTHON_ENV_DIR=D:\Envs\file-sharer
::工具包(构建工具脚本)路径
set TOOLKITS_DIR=%cd%\toolkits
::项目名称(同spec中项目名)
set PROJECT_NAME=file-sharer
::项目版本
set PRODUCT_VERSION=v0.0.1

cd ..
::项目路径
set PROJECT_DIR=%cd%

::进入虚拟环境打包源码
if %PYTHON_ENV_DIR% == "" (
    echo Using the global python env
) else (
    call %PYTHON_ENV_DIR%\Scripts\activate.bat
)
echo ******************* Packaging the source code using pyinstaller *******************
pyinstaller32 main.spec --distpath %PROJECT_DIR%\build

@rem 使用7z打包成绿色版
echo ******************* Packaging into a green version using 7z *******************
if exist %PROJECT_DIR\build\installer (
    echo installer dir is exists
) else (
    md %PROJECT_DIR%\build\installer
)
7z a %PROJECT_DIR%\build\installer\file_sharer-desktop_%PRODUCT_VERSION%-win_x86-green.7z %PROJECT_DIR%\build\%PROJECT_NAME%\

@rem 再用NSIS打包成Windows安装程序
echo ******************* Packaging as Windows installation program using NSIS *******************
::安装之前需修改nsi中PRODUCT_VERSION 和 PROJECT_DIR的值
makensis %TOOLKITS_DIR%\build_windows_x86.nsi

::打包结束
echo ******************* Build complete! *******************
pause