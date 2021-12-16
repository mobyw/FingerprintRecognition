# 指纹识别

基于 OpenCV-Python 的指纹识别项目。

## 目录

- [安装](#安装)
- [使用](#使用)
- [原理](#原理)
- [致谢](#致谢)
- [协议](#协议)

## 安装

工程基于 [python3](https://www.python.org/) 平台上的 [opencv-python](https://pypi.org/project/opencv-python/) 和 [scikit-image](https://pypi.org/project/scikit-image/) 。

安装依赖:

```sh
pip install -r requirements.txt
```

## 使用

提供命令行和图像界面两种操作方法。

命令行程序: 

```sh
python app.py
```

运行后需要输入图像的地址，比如 `./image/101_1.tif` 。如果未识别到匹配图片，需要输入名字以保存到库中。

参数也可以在启动时通过参数列表给出，并以 `./image/` 开头，使用示例文件夹中的图片时只需给出图像文件名：

```sh
python app.py 101_1.tif
```

GUI 版程序提供命令行和 GUI 两种操作方式，可以通过帮助命令查看使用方式：

```sh
python app_gui.py --help
```

或者直接使用 GUI 方式：

```sh
python app_gui.py --gui
```

选择图片和库的路径，点击 `OK` 等待几秒钟即可得到结果。

![gui](https://cdn.jsdelivr.net/gh/mobyw/images@main/Screenshots/FingerprintRecognize.jpg)

## 原理

### 图像增强

使用定向 Gabor 滤波器组来增强指纹图像。 Gabor 滤波器的方向基于脊的方向。 Gabor 滤波器的形状基于脊的频率和波长。

### 指纹匹配

使用 Harris 角点获取特征点，并获取其 SIFT (ORB) 二进制描述符，并使用 Brute-force 匹配获取特征点的二进制描述符，然后使用阈值比较返回的匹配结果。

### 指纹识别

获取输入图像的描述符，并与所有保存的描述符匹配。如果有匹配项，则展示出结果。如果没有，就将描述符保存到库中。

## 致谢

本设计参考了 [Fingerprint-Enhancement-Python](https://github.com/Utkarsh-Deshmukh/Fingerprint-Enhancement-Python) 和 [python-fingerprint-recognition](https://github.com/kjanko/python-fingerprint-recognition) 两个工程，对这些工程的原作者表示感谢。

## 协议

[MIT](LICENSE) © mobyw
