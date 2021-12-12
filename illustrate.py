#
# 指纹图片比对方法演示
# Author: Xiaohei
# Updatetime: 2021-12-12
#

import cv2
import sys
import numpy
from enhance import image_enhance
import matplotlib.pyplot as plt


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

    img[img == 1] = 255

    return keypoints, des, img


def main():

    if len(sys.argv) > 1:
        image_name1 = sys.argv[1]
        image_path1 = "./image/" + image_name1
    else:
        print("Please input the image1 path: ")
        image_path1 = input()

    if len(sys.argv) > 2:
        image_name2 = sys.argv[2]
        image_path2 = "./image/" + image_name2
    else:
        print("Please input the image2 path: ")
        image_path2 = input()

    img1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

    if img1 is not None:
        img1 = cv2.resize(img1, dsize=(256, 364))
        kp1, des1, _img1 = get_descriptors(img1)
    else:
        raise Exception("Invalid image1 path!")

    if img2 is not None:
        img2 = cv2.resize(img2, dsize=(256, 364))
        kp2, des2, _img2 = get_descriptors(img2)
    else:
        raise Exception("Invalid image2 path!")

    # Matching between descriptors
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(bf.match(des1, des2), key=lambda match: match.distance)

    # Plot keypoints
    img4 = cv2.drawKeypoints(_img1, kp1, outImage=None)
    img5 = cv2.drawKeypoints(_img2, kp2, outImage=None)
    f, axarr = plt.subplots(1, 2)
    axarr[0].imshow(img4)
    axarr[1].imshow(img5)
    plt.show()

    # Plot matches
    img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches, flags=2, outImg=None)
    plt.imshow(img3)
    plt.show()

    # Calculate score
    score = 0
    for match in matches:
        score += match.distance
    score_threshold = 40
    avg = score / len(matches)
    print("Avg distance: ", avg)
    print("Threshold: ", score_threshold)
    if avg < score_threshold:
        print("Fingerprint matches.")
    else:
        print("Fingerprint does not match.")


if __name__ == "__main__":
    try:
        main()
    except:
        raise
