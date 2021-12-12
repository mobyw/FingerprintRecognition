#
# 为 GUI 封装的函数 不可直接运行
# Author: Xiaohei
# Updatetime: 2021-12-01
#

import cv2
import os
import numpy
import pickle
from enhance import image_enhance


def get_descriptors(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)
    img = image_enhance.image_enhance(img)
    img = numpy.array(img, dtype=numpy.uint8)

    # Threshold
    ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    # Normalize to 0 and 1 range
    img[img == 255] = 1

    # Harris corners
    harris_corners = cv2.cornerHarris(img, 3, 3, 0.04)
    harris_normalized = cv2.normalize(harris_corners, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32FC1)
    threshold_harris = 125

    # Extract keypoints
    keypoints = []
    for x in range(0, harris_normalized.shape[0]):
        for y in range(0, harris_normalized.shape[1]):
            if harris_normalized[x][y] > threshold_harris:
                keypoints.append(cv2.KeyPoint(y, x, 1))

    # Define descriptor
    orb = cv2.ORB_create()

    # Compute descriptors
    _, des = orb.compute(img, keypoints)

    return keypoints, des


def match(des1, path, name_lst):
    avg_lst = []

    if name_lst:
        for name in name_lst:
            with open("{}/{}".format(path, name), "rb+") as f:
                des2 = pickle.load(f)
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = sorted(bf.match(des1, des2), key=lambda match: match.distance)
            score = 0

            for match in matches:
                score += match.distance

            avg = score / len(matches)
            avg_lst.append(avg)

        return avg_lst
    else:
        return None


def run_app(image_path, data_path):

    img1 = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if img1 is not None:
        img1 = cv2.resize(img1, dsize=(256, 364))
        kp1, des1 = get_descriptors(img1)
    else:
        raise Exception("Invalid image path!")

    address_lst = [name for name in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, name))]
    name_lst = list(address_lst)
    avgs = match(des1, data_path, name_lst)

    score_threshold = 40

    if avgs is not None:
        if min(avgs) < score_threshold:
            flag = True
            name = name_lst[avgs.index(min(avgs))]
        else:
            flag = False
            name = name_lst[avgs.index(min(avgs))]
            name1 = image_path.replace("\\", "/").split("/")[-1].split(".")[0]
            # name1 = input("Input a name to save the fingerprint: ")
            if name1:
                with open("{}/{}".format(data_path, name1), "wb+") as f:
                    pickle.dump(des1, f)
    else:
        flag = False
        name = "None"
        name1 = image_path.replace("\\", "/").split("/")[-1].split(".")[0]
        # name1 = input("Input a name to save the fingerprint: ")
        if name1:
            with open("{}/{}".format(data_path, name1), "wb+") as f:
                pickle.dump(des1, f)

    return flag, name
