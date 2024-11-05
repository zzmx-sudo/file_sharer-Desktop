<p align="center"><a href="https://github.com/zzmx-sudo/file_sharer-LAN"><img src="https://github.com/zzmx-sudo/file_sharer-LAN/blob/master/docs/logo.png" alt="file_sharer logo"></a></p>

<p align="center">
    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="code style: black"></a>
</p>

<h2 align="center">文件共享助手桌面版</h2>

### 说明
一个基于 PyQt5 开发的文件共享工具, 集服务器和客户端于一身

工具特点:

- 既是服务端又是客户端
- 支持HTTP和FTP两种分享模式
- 支持断点续传/下载, 不惧下载中断
- 友好提示
- 还算不错的UI界面
- black style代码风格

所用技术栈:

- python3.8+
- PyQt5
- fastapi
- asyncio
- pyftpdlib

已支持的平台:

- windows7及以上
- MacOS 12及以上

软件变化请查看：[更新日志](https://github.com/zzmx-sudo/file_sharer-LAN/blob/master/CHANGELOG.md)<br>
软件下载请到：[发布页面](https://github.com/zzmx-sudo/file_sharer-Desktop/releases)<br>
或者到网盘下载：链接 `https://zzmx.lanzoue.com/b01fiitgd` 密码 `brjm`（若链接无法打开请百度：蓝奏云链接打不开）<br>
使用常见问题或发布问题请转至：[常见问题](https://github.com/zzmx-sudo/file_sharer-Desktop/issues)

目前本项目的原始发布地址只有**GitHub**及**蓝奏网盘**, 请认准本项目署名: **大宝天天见丶**, 其他渠道均为第三方转载发布, 与本项目无关！

### 使用方式

#### 安装包使用方式

下载系统对应版本安装包后按正常软件安装方式点击安装, 安装完成后通过桌面快捷方式打开即可

#### 源码使用方式

* 安装python 3.8及以上版本
* 通过命令 `pip install -r requirements.txt` 安装第三方依赖
* 运行main.py

### UI界面

<p><a href="https://github.com/zzmx-sudo/file_sharer-LAN"><img src="https://github.com/zzmx-sudo/file_sharer-LAN/blob/master/docs/app.png" alt="UI界面"></a></p>

### 贡献代码

本项目欢迎PR, 但为了PR能够顺利合入, 需要注意以下几点:

- PR目标分支: `master`
- 对于添加新功能的PR，建议在PR前先创建issue说明，以确认该功能是否确实需要
- 对于修复Bug PR，请提供修复前后的说明及重现方式
- 其他类型的PR则适当附上说明

### 项目协议

本项目基于 [MIT License](https://github.com/zzmx-sudo/file_sharer-Desktop/blob/master/LICENSE) 许可证发行, 以下协议是对 MIT License 的补充, 如有冲突, 以以下协议为准。

词语约定: 本协议中的"本项目"指文件共享助手桌面版项目; "使用者"指签署本协议的使用者; "分享者"指利用本项目分享文件的使用者; "开发者"指的是复制本项目并自行更改另发布的人员。

1. 本项目出发点为提高作者开发能力和提高作者行业融入度, 欢迎大家对本项目包括界面、功能、方向等积极讨论, 请勿有贬低、排斥、暴力等一切不友好言论。
2. 使用者切勿寻找并利用本项目漏洞对分享者服务器进行攻击, 若发生一切后果自负。
3. 开发者切勿对程序嵌入木马, 并建议发布时附上您的署名。

若你使用了本项目，将代表你接受以上协议。
