# FingerprintRecognition

Fingerprint Recognition using OpenCV-Python.

## Table of Contents

- [Install](#Install)
- [Usage](#usage)
- [Principle](#principle)
- [Acknowledgement](#acknowledgement)
- [License](#license)

## Install

This project uses [opencv-python](https://pypi.org/project/opencv-python/) and [scikit-image](https://pypi.org/project/scikit-image/) on [python3](https://www.python.org/). 

To install the requirements:

```sh
pip install -r requirements.txt
```

## Usage

There are both command line code and gui code in the repo. 

Use the command line code: 

```sh
python app.py
```

The full path of the image is required to recognize, such as `./image/101_1.tif`. If the image is not matched, a name is required to save in the data folder.

Parameters can be given at startup, the default path starts with `./image/` folder, only image name is needed when using the example images, like: 

```sh
python app.py 101_1.tif
```

Gui code provides both commmand line method and gui method, just read the help information to use it:

```sh
python app_gui.py --help
```

Or simplely use the gui method by:

```sh
python app_gui.py --gui
```

Browse the image and data path, then press the `OK` button, the results will be shown seconds later.

![gui](https://cdn.jsdelivr.net/gh/mobyw/images@main/Screenshots/FingerprintRecognize.jpg)

## Principle

### Enhance

Uses oriented gabor filter bank to enhance the fingerprint image. The orientation of the gabor filters are based on the orientation of the ridges. the shape of the gabor filter is based on the frequency and wavelength of the ridges.

### Match

Uses Harris corner detector to find the keypoints and get their SIFT (ORB) descriptors. Uses brute-force hamming distance and then analyzes the returned matches using thresholds.

### Recognize

Get the description of the input image, and match with all saved descriptions. If matched, print the result. If not, save the description to the data path.

## Acknowledgement

The project refers to [Fingerprint-Enhancement-Python](https://github.com/Utkarsh-Deshmukh/Fingerprint-Enhancement-Python) and [python-fingerprint-recognition](https://github.com/kjanko/python-fingerprint-recognition). Special thanks to their authors.

## License

[MIT](LICENSE) © mobyw
