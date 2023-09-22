@echo off

@rem 先使用pyinstaller打包源码
::python虚拟环境路径,若无请配空值
set PYTHON_ENV_DIR=D:\Envs\file-sharer
::工具包(构建工具脚本)路径
set TOOLKITS_DIR=%cd%\toolkits
::项目名称(同spec中项目名)
set PROJECT_NAME=file-sharer

cd ..
::项目路径
set PROJECT_DIR=%cd%

@echo on
::进入虚拟环境打包源码
@if %PYTHON_ENV_DIR% == "" (
    @echo Using the global python env
) else (
    @call %PYTHON_ENV_DIR%\Scripts\activate.bat
)
@echo ******************* Packaging the source code using pyinstaller *******************
@pyinstaller main.spec --distpath %PROJECT_DIR%\build

@rem 再用NSIS打包成Windows安装程序
@echo ******************* Packaging as Windows installation program using NSIS *******************
::makensis %TOOLKITS_DIR%\build_windows.nis

::打包结束
@echo ******************* build complete! *******************
@pause