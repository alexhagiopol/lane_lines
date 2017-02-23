# import dependencies
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
import os
import math
import shutil
import statistics

# prepare filesystem for input and output
in_dir_name = "test_images/"
out_dir_name = "result_images/"
if os.path.exists(out_dir_name):
    shutil.rmtree(out_dir_name)
os.mkdir(out_dir_name)
input_image_filenames = os.listdir(in_dir_name)

# set tuning parameters for algortithms
# gaussian blurring param:
kernel_size = 5  # Gaussian blur kernel must be odd number
# canny edge detection params:
low_thresh = 50  # low gradient threshold
hi_thresh = 150  # high gradient threshold
# hough transform params:
rho = 1  # distance resolution of the accumulator in pixels
theta = np.pi / 180  # angle resolution of the accumulator in radians
threshold = 2  # votes needed to return line (>threshold).
min_line_len = 50
max_line_gap = 20

for image_filename in input_image_filenames:
    print("processing image: ", image_filename)
    raw_image = cv2.imread(os.path.join(in_dir_name, image_filename))
    gray_image = cv2.cvtColor(raw_image, cv2.COLOR_RGB2GRAY)

    # gaussian blur + canny edge detection
    gaussian_image = cv2.GaussianBlur(gray_image, (kernel_size, kernel_size), 0)
    edges_image = cv2.Canny(gaussian_image, low_thresh, hi_thresh)

    # crop
    mask = np.zeros_like(edges_image)
    imshape = raw_image.shape
    vertices = np.array([[(75, imshape[0]), (imshape[1] / 2 - 50, imshape[0] / 2 + 50), (imshape[1] / 2 + 50, imshape[0] / 2 + 50), (imshape[1] - 75, imshape[0])]], dtype=np.int32)
    cv2.fillPoly(mask, vertices, 255)
    masked_edges_image = cv2.bitwise_and(edges_image, mask)

    # lines via hough transform
    lines = cv2.HoughLinesP(masked_edges_image, rho, theta, threshold, np.array([]), min_line_len, max_line_gap)

    # extract + lines from hough data structure. Associate slope so we can sort by it.
    pos_lines = [[x1, y1, x2, y2, (y2 - y1) / (x2 - x1)] for [[x1, y1, x2, y2]] in lines if (y2 - y1) / (x2 - x1) >= 0]  # lines with + slope.
    pos_lines.sort(key=lambda p: p[4])  # sort by slope
    x1, y1, x2, y2, pos_M = pos_lines[len(pos_lines) // 2 - 1]  # find line with median slope
    pos_B = y1 - pos_M*x1  # compute y intercept
    # compute lane line
    pos_Y1 = int(imshape[0])
    pos_X1 = int((pos_Y1 - pos_B) / pos_M)
    pos_Y2 = int(imshape[0] / 2 + 50)
    pos_X2 = int((pos_Y2 - pos_B) / pos_M)

    # extract - lines from hough data structure. Associate slope so we can sort by it.
    neg_lines = [[x1, y1, x2, y2, (y2 - y1) / (x2 - x1)] for [[x1, y1, x2, y2]] in lines if (y2 - y1) / (x2 - x1) < 0]  # lines with - slope.
    neg_lines.sort(key=lambda n: n[4])  # sort by slope
    x1, y1, x2, y2, neg_M = neg_lines[len(neg_lines) // 2 - 1]  # find line with median slope
    neg_B = y1 - neg_M * x1  # compute y intercept
    # compute lane line
    neg_Y1 = int(imshape[0])
    neg_X1 = int((neg_Y1 - neg_B) / neg_M)
    neg_Y2 = int(imshape[0] / 2 + 50)
    neg_X2 = int((neg_Y2 - neg_B) / neg_M)

    # draw lines and save image
    line_image = np.copy(raw_image)
    cv2.line(raw_image, (pos_X1, pos_Y1), (pos_X2, pos_Y2), (0, 0, 255), 10)
    cv2.line(raw_image, (neg_X1, neg_Y1), (neg_X2, neg_Y2), (0, 0, 255), 10)
    processed_image = raw_image
    cv2.imwrite(os.path.join(out_dir_name, "processed_" + image_filename), processed_image)