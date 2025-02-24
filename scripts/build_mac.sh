cd ..
PROJECT_PATH=`pwd`
PYTHON_ENV_DIR="/Users/mr.cheng/PY_ENVS/file_sharer"
PROJECT_NAME="FileSharer"
PRODUCT_VERSION="v0.1.0"
# 创建build文件夹
if [ -d "${PROJECT_PATH}/build" ]; then
  echo "build文件夹已存在, 跳过创建"
else
  echo "创建build文件夹..."
  mkdir "${PROJECT_PATH}/build"
fi
# 修改main_setup.py中PROJECT_PATH和PRODUCT_VERSION的值
sed -i '' "s~PROJECT_PATH = .*~PROJECT_PATH = \"$PROJECT_PATH/\"~g" ${PROJECT_PATH}/main_setup.py
sed -i '' "s~PRODUCT_VERSION = .*~PRODUCT_VERSION = \"$PRODUCT_VERSION\"~g" ${PROJECT_PATH}/main_setup.py
# 进入虚拟环境
if [ -d $PYTHON_ENV_DIR ]; then
  source $PYTHON_ENV_DIR/bin/activate
else
  echo Using the global python env
fi
# 使用py2app打包源码
echo "******************* Packaging the source code using py2app *******************"
cd ${PROJECT_PATH}/build
python ${PROJECT_PATH}/main_setup.py py2app
echo "[]" > ${PROJECT_PATH}/build/dist/${PROJECT_NAME}.app/Contents/Resources/file_sharing_backups.json

# 使用create-dmg打包成dmg文件
echo "******************* Packaging as MacOS installation program using create-dmg *******************"
if [ -d "${PROJECT_PATH}/build/dmg" ]; then
  rm -rf "${PROJECT_PATH}/build/dmg"
fi

mkdir "${PROJECT_PATH}/build/dmg"
if [ ! -d "${PROJECT_PATH}/build/installer" ]; then
  mkdir "${PROJECT_PATH}/build/installer"
fi

cp -r ${PROJECT_PATH}/build/dist/${PROJECT_NAME}.app ${PROJECT_PATH}/build/dmg/

cd ${PROJECT_PATH}/build/
if [ "$1" == "arm64" ]; then
  ARCH_NAME="arm64"
else
  ARCH_NAME="x64"
fi
# macos-13 runner Maybe due to `Resource busy` failure, try up to 5 times
for i in {1..5}; do
  create-dmg --volname "${PROJECT_NAME}" \
    --volicon "${PROJECT_PATH}/static/ui/icon.ico" \
    --window-pos 200 120 \
    --window-size 600 300 \
    --icon-size 100 \
    --icon "${PROJECT_NAME}.app" 175 120 \
    --hide-extension "${PROJECT_NAME}.app" \
    --app-drop-link 425 120 \
    "installer/file_sharer-desktop_${PRODUCT_VERSION}-macos-${ARCH_NAME}.dmg" \
    "./dmg/" && break || sleep 5
done

# return code 1 where create-img is failed
if [ ! -f "installer/file_sharer-desktop_${PRODUCT_VERSION}-macos-${ARCH_NAME}.dmg" ]; then
  echo "Failed to create-img! Exit Build."
  exit 1
fi

# 打包结束
echo ******************* Build complete! *******************
