#
# CLI 方式执行程序
# Author: Xiaohei
# Updatetime: 2021-12-01
#

import cv2
import os
import sys
import numpy
import pickle
import datetime
from enhance import image_enhance


data_path = "./data/"
address_lst = [name for name in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, name))]
name_lst = list(address_lst)


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


def match(des1):
    avg_lst = []

    if name_lst:
        for name in name_lst:
            with open("./data/{}".format(name), "rb+") as f:
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


def main():

    if len(sys.argv) > 1:
        image_name1 = sys.argv[1]
        image_path = "./image/" + image_name1
    else:
        print("Please input the image path: ")
        image_path = input()

    start = datetime.datetime.now()

    # print(image_path)
    img1 = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if img1 is not None:
        img1 = cv2.resize(img1, dsize=(256, 372))
        kp1, des1 = get_descriptors(img1)
    else:
        raise Exception("Invalid image path!")

    avgs = match(des1)
    # print(avgs)

    score_threshold = 33

    if avgs is not None:
        if min(avgs) < score_threshold:
            print("Fingerprint matches: ")
            print(name_lst[avgs.index(min(avgs))])
        else:
            print("Fingerprint does not match.")
            print("Most likely: ")
            print(name_lst[avgs.index(min(avgs))])
            # name1 = image_name1.split("/")[-1].split(".")[0]
            name1 = input("Input a name to save the fingerprint: ")
            if name1:
                with open("./data/{}".format(name1), "wb+") as f:
                    pickle.dump(des1, f)
    else:
        # name1 = image_name1.split("/")[-1].split(".")[0]
        name1 = input("Input a name to save the fingerprint: ")
        if name1:
            with open("./data/{}".format(name1), "wb+") as f:
                pickle.dump(des1, f)

    end = datetime.datetime.now()
    print('Total time: ' + str(end - start))


if __name__ == "__main__":
    try:
        main()
    except:
        raise
