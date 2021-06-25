from cv2 import cv2
import numpy as np

'''
@function
检测输入图像高光区域
@parameter
img1:基准图像
@return
mask:三通道高光像素掩码
flip_mask:反高光像素掩码
'''
def get_high_mask(img1):
    b1, g1, r1 = cv2.split(img1)

    #cv2.imshow('img3', b1)
    rows, cols, _ = img1.shape
    chanel_min = np.zeros((rows, cols), dtype=img1.dtype)
    for row in range(rows):            #遍历高
            for col in range(cols):         #遍历宽
                chanel_min[row][col] = min(r1[row][col], g1[row][col], b1[row][col])

    mean_chanel_min = np.mean(chanel_min)
    msf_r1 = np.uint8(r1 - chanel_min + mean_chanel_min)
    msf_g1 = np.uint8(g1 - chanel_min + mean_chanel_min)
    msf_b1 = np.uint8(b1 - chanel_min + mean_chanel_min)

    #msf_img1 = cv2.merge([msf_b1, msf_g1, msf_r1])
    #cv2.imshow('img3', msf_r1)
    #cv2.imshow('img2', r1)

    '''for循环效率低
    mask_r1 = np.zeros((img1.shape[:2]),np.uint8)
    mask_g1 = np.zeros((img1.shape[:2]),np.uint8)
    mask_b1 = np.zeros((img1.shape[:2]),np.uint8)
    for row in range(rows):            #遍历高
            for col in range(cols):         #遍历宽
                if r1[row][col] > msf_r1[row][col] and r1[row][col] - msf_r1[row][col] >= 100:
                    mask_r1[row][col] = 255
                if g1[row][col] > msf_g1[row][col] and g1[row][col] - msf_g1[row][col] >= 100:
                    mask_g1[row][col] = 255
                if b1[row][col] > msf_b1[row][col] and b1[row][col] - msf_b1[row][col] >= 100:
                    mask_b1[row][col] = 255
    '''
    th = 40
    #获取b高光像素掩码
    mask_b1 = np.float32(b1) - np.float32(msf_b1)
    mask_b1[mask_b1<0] = 0
    mask_b1 = np.uint8(mask_b1 >= th)*255
    #获取g高光像素掩码
    mask_g1 = np.float32(g1) - np.float32(msf_g1)
    mask_g1[mask_g1<0] = 0
    mask_g1 = np.uint8(mask_g1 >= th)*255
    #获取r高光像素掩码
    mask_r1 = np.float32(r1) - np.float32(msf_r1)
    mask_r1[mask_r1<0] = 0
    mask_r1 = np.uint8(mask_r1 >= th)*255
    '''
    cv2.imshow('img1',b1)
    cv2.imshow('img2',msf_b1)
    '''
    k = np.ones((5, 5), np.uint8)
    #对掩码去噪，获得closing掩码
    opening_b = cv2.morphologyEx(mask_b1, cv2.MORPH_OPEN, k)#形态学拓展开运算，先腐蚀后膨胀，去除噪声
    closing_b = cv2.morphologyEx(opening_b, cv2.MORPH_CLOSE, k)#形态学拓展闭运算，先膨胀后腐蚀，去除物体内部小黑点
    opening_g = cv2.morphologyEx(mask_g1, cv2.MORPH_OPEN, k)
    closing_g = cv2.morphologyEx(opening_g, cv2.MORPH_CLOSE, k)
    opening_r = cv2.morphologyEx(mask_r1, cv2.MORPH_OPEN, k)
    closing_r = cv2.morphologyEx(opening_r, cv2.MORPH_CLOSE, k)

    mask = cv2.merge([closing_b, closing_g, closing_r]) #三通道高光像素掩码
    flip_mask = np.invert(mask) #反高光像素掩码
    return mask, flip_mask