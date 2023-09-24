cd ..
PROJECT_PATH=`pwd`
PYTHON_ENV_DIR="/Users/mr.cheng/PY_ENVS/file_sharer"
PROJECT_NAME="file-sharer"
PRODUCT_VERSION="v0.0.1"
# 创建build文件夹
if [ -d "${PROJECT_PATH}/build" ]; then
  echo "build文件夹已存在, 跳过创建"
else
  echo "创建build文件夹..."
  mkdir "${PROJECT_PATH}/build"
fi
# 创建mac版spec文件, 从windows版spec中拷贝并替换必要值
cp ${PROJECT_PATH}/main.spec ${PROJECT_PATH}/build/main_mac.spec
sed -i '' 's/\\\\/\//g' ${PROJECT_PATH}/build/main_mac.spec
# 路径中有/, 故sed命令中分隔符用~代替
sed -i '' "s~PROJECT_PATH = .*~PROJECT_PATH = \"$PROJECT_PATH/\"~g" ${PROJECT_PATH}/build/main_mac.spec
# 添加app参数
echo "\napp = BUNDLE(
    coll,
    name='${PROJECT_NAME}.app',
    icon=PROJECT_PATH+'static/ui/icon.ico',
    bundle_identifier=None,
)" >> ${PROJECT_PATH}/build/main_mac.spec
# 进入虚拟环境
if [ $PYTHON_ENV_DIR != "" ]; then
  source $PYTHON_ENV_DIR/bin/activate
else
  echo Using the global python env
fi
# 使用pyinstaller打包源码
echo "******************* Packaging the source code using pyinstaller *******************"
pyinstaller ${PROJECT_PATH}/build/main_mac.spec --distpath ${PROJECT_PATH}/build

# 使用create-dmg打包成dmg文件
echo "******************* Packaging as MacOS installation program using create-dmg *******************"
if [ -d "${PROJECT_PATH}/build/dmg" ]; then
  rm -rf "${PROJECT_PATH}/build/dmg"
fi

mkdir "${PROJECT_PATH}/build/dmg"
if [ ! -d "${PROJECT_PATH}/build/installer" ]; then
  mkdir "${PROJECT_PATH}/build/installer"
fi

cp -r ${PROJECT_PATH}/build/${PROJECT_NAME}.app ${PROJECT_PATH}/build/dmg/

cd ${PROJECT_PATH}/build/
create-dmg --volname "文件共享助手" \
  --volicon "${PROJECT_NAME}/icon.ico" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "${PROJECT_NAME}.app" 175 120 \
  --hide-extension "${PROJECT_NAME}.app" \
  --app-drop-link 425 120 \
  "installer/file_sharer-desktop_${PRODUCT_VERSION}-macos.dmg" \
  "./dmg/"

# 打包结束
echo ******************* Build complete! *******************