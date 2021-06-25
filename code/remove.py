from cv2 import cv2
import numpy as np
from matplotlib import pyplot as plt
from detect_high_area import get_high_mask
from transform import transform_view
from adjust import adjust_brightness

def remove_high_area(path1, path2):
    img1 = cv2.imread(path1, cv2.IMREAD_UNCHANGED)   #基准图,读入默认是uint8格式的numpy array
    img2 = cv2.imread(path2, cv2.IMREAD_UNCHANGED)   #辅助图

    img1, adj_img2 = adjust_brightness(img1, img2)

    #辅助图视角转换
    transform_img2 = transform_view(img1, adj_img2)

    #检测基准图高光区域
    mask, flip_mask = get_high_mask(img1)

    high_area = cv2.bitwise_and(transform_img2, mask) #掩膜操作
    low_area = cv2.bitwise_and(img1, flip_mask) #掩膜操作
    result = cv2.addWeighted(low_area, 1, high_area, 1, 0)   #图像融合
    hShow= np.hstack((img1, img2, result))

    path = path1.split(".")
    path_contrast = path[0] + '_contrast.' + path[1]
    path_remove = path[0] + '_remove.' + path[1]
    '''
    if(cv2.imwrite(path, hShow)):
        return 1
    else:
        return 0
    
    cv2.namedWindow("remove", cv2.WINDOW_KEEPRATIO)
    cv2.namedWindow("contrast", cv2.WINDOW_KEEPRATIO)
    cv2.imshow('remove',result)
    cv2.imshow('contrast',hShow)
    '''
    cv2.imwrite(path_contrast, hShow)
    cv2.imwrite(path_remove, result)

    plt.figure()
    img1 = img1[:,:,[2,1,0]]
    plt.subplot(1,3,1)
    plt.imshow(img1)
    plt.title("Reference", fontsize= 20)

    img2 = img2[:,:,[2,1,0]]
    plt.subplot(1,3,2)
    plt.imshow(img2)
    plt.title("Auxiliary", fontsize= 20)

    result = result[:,:,[2,1,0]]
    plt.subplot(1,3,3)
    plt.imshow(result)
    plt.title("Restore",fontsize= 20)
    plt.show()
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()