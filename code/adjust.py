from cv2 import cv2
import numpy as np

'''
@function
辅助图亮度调整
@parameter
img1:基准图像
img2:辅助图
@return
img1:基准图
adj_img2:亮度调整后的辅助图
'''
def adjust_brightness(img1, img2):
    hsv_img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)    #RGB图像转换到HSV图像, H:0-180, S：0-255, V：0-255
    hsv_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

    _, _, v1 = cv2.split(hsv_img1)   #hsv 通道拆分
    h2, s2, v2 = cv2.split(hsv_img2)

    mean_v1 = np.mean(v1)   #基准图像素的平均亮度
    mean_v2 = np.mean(v2)   #辅助图像素的平均亮度

    adj_v2 = v2 + (mean_v1 - mean_v2) * (1 + (mean_v2 - v2)/255)    #对辅助图亮度进行矫正
    adj_v2_unit8 = np.uint8(adj_v2)     #对图像进行处理后通常会变成float格式，查看图片时需转换成uint8格式
    adj_hsv_img2 = cv2.merge([h2, s2, adj_v2_unit8])    #调整后的v2与h2，s2进行合并
    adj_img2 = cv2.cvtColor(adj_hsv_img2, cv2.COLOR_HSV2BGR)    #合并HSV图像转换到RGB图像,完成辅助图亮度调整
    
    return img1, adj_img2