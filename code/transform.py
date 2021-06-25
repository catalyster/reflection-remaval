from cv2 import cv2
import numpy as np

'''
@function
SIFT特征提取，单应性变换
@parameter
img1:基准图像
adj_img2:亮度调整后的辅助图
@return
transform_img2:视角转换后的辅助图
'''
def transform_view(img1, adj_img2):
    sift = cv2.xfeatures2d.SIFT_create()     #构建sift对象
    gray_img1= cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) #转换为灰度图像
    kp1, des1 = sift.detectAndCompute(gray_img1, None)   #检测特征点kp1、计算特征描述符des1
    cv2.drawKeypoints(gray_img1, kp1, gray_img1, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)     #画图

    gray_img2= cv2.cvtColor(adj_img2, cv2.COLOR_BGR2GRAY) #转换为灰度图像
    kp2, des2 = sift.detectAndCompute(gray_img2, None)
    cv2.drawKeypoints(gray_img2, kp2, gray_img2, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    '''
    hmerge = np.hstack((gray_img1, gray_img2)) #水平拼接; np.vstack()竖直拼接
    cv2.imshow("img1", hmerge) #拼接显示为gray
    '''
    # 默认参数初始化BF匹配器
    bf = cv2.BFMatcher()
    #暴力匹配bf.match()方法返回的是最佳匹配，那么matches自然就是一个一维列表，所以只能使用drawMatches()
    matches = bf.knnMatch(des1,des2, k=2)   #返回每个点的k个匹配点
    '''
    DMatch.distance - Distance between descriptors
    DMatch.trainIdx - Index of the descriptor in train descriptors
    DMatch.queryIdx - Index of the descriptor in query descriptors
    DMatch.imgIdx - Index of the train image.
    '''
    # 应用比例测试
    good = []   #一维
    good_with_list = []     #二维
    for m,n in matches:
        if m.distance < 0.75*n.distance:        #如果最近距离除以次近距离小于某个阈值，则判定为一对匹配点，即去除错误匹配
            good.append(m)
            good_with_list.append([m])
    #对于drawMatchesKnn()，参数matches1to2和matchesMask是二维数组
    #match_img = cv2.drawMatchesKnn(img1, kp1, adj_img2, kp2, good_with_list, None, flags=2)
    #cv2.imshow("img1", match_img)

    #单应性寻找目标物体,剔除错误匹配点
    MIN_MATCH_COUNT = 20
    if len(good)>MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1, 1, 2) #reshape的作用是将得到的特征点按照索引转换成一个坐标点的列表
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0) #返回的M为 辅助图 到 基准图 的变换矩阵，mask是一个二维数组
        matchesMask = mask.ravel().tolist() #转化为一维数组
        '''在train中对query图像的标记
        h,w,d = img1.shape
        pts = np.float32([ [0, 0], [0, h-1], [w-1, h-1], [w-1, 0] ]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        adj_img2 = cv2.polylines(adj_img2, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
        '''
    else:
        print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
        matchesMask = None

    draw_params = dict(matchColor = (0, 255, 0), # 用绿色绘制匹配
                    singlePointColor = None,
                    matchesMask = matchesMask, # 只绘制内部点
                    flags = 2)
    in_match_img = cv2.drawMatches(img1, kp1, adj_img2, kp2, good, None, **draw_params) #对于drawMatches()，参数matches1to2和matchesMask是一维数组；
    #cv2.imshow('img3', in_match_img)

    #透射变换
    transform_img2 = cv2.warpPerspective(adj_img2, M, (adj_img2.shape[1], adj_img2.shape[0]))
    return transform_img2