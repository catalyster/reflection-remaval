import tkinter as tk
from remove import remove_high_area
import matlab
import matlab.engine

# 第1步，实例化object，建立窗口window
window = tk.Tk()
# 第2步，给窗口的可视化起名字
window.title('反光去除')
# 第3步，设定窗口的大小(长 * 宽)
window.geometry('500x300')  # 这里的乘是小x
 
# 第4步，加载 welcome image
canvas = tk.Canvas(window, width=500, height=114)
image_file = tk.PhotoImage(file='C:/Users/catalyst/Desktop/graduationDesign/code/test/pic.gif')
image = canvas.create_image(250, 0, anchor='n', image=image_file)
canvas.pack(side='top')
 


def muti():
    def muti_start():
        reference_pic_path = var_reference.get()    #基准图路径
        auxiliary_pic_path = var_auxiliary.get()    #辅助图路径
        '''
        if(remove_high_area(reference_pic_path, auxiliary_pic_path)):
            tkinter.messagebox.showinfo(title='消息', message='成功！')
        else:
            tkinter.messagebox.showinfo(title='消息', message='失败！')
        '''
        remove_high_area(reference_pic_path, auxiliary_pic_path)
        window_muti.destroy()

     # 定义在窗口上的窗口
    window_muti = tk.Toplevel(window)
    window_muti.geometry('500x300')
    window_muti.title('高光去除')
 
    tk.Label(window_muti, text='多图像高光去除',font=('Arial', 16, "bold")).place(x=170, y=50)
    # 第5步
    tk.Label(window_muti, text='基准图:', font=('Arial', 14)).place(x=10, y=100)
    tk.Label(window_muti, text='辅助图:', font=('Arial', 14)).place(x=10, y=150)
    
    # 第6步，用户输入框entry
    # 基准图
    var_reference = tk.StringVar()
    var_reference.set('输入基准图路径')
    entry_reference = tk.Entry(window_muti, textvariable=var_reference, font=('Arial', 14), width = 27)
    entry_reference.place(x=100,y=100)
    # 辅助图
    var_auxiliary = tk.StringVar()
    var_auxiliary.set('输入辅助图路径')
    entry_auxiliary = tk.Entry(window_muti, textvariable=var_auxiliary, font=('Arial', 14), width = 27)
    entry_auxiliary.place(x=100,y=150)
 
    # 下面的 muti_start
    btn_comfirm_single = tk.Button(window_muti, text='开始', command=muti_start)
    btn_comfirm_single.place(x=220, y=220)

# 第7步，按钮
btn_login = tk.Button(window, text='高光去除', command=muti)
btn_login.place(x=225, y=160)



def single():
    def single_start():
        image_path = var_image.get()    #基准图路径
        engine = matlab.engine.start_matlab() # Start MATLAB process
        engine.deghosts(image_path,nargout=0) #调用matlab函数
        window_single.destroy()
 
    # 定义在窗口上的窗口
    window_single = tk.Toplevel(window)
    window_single.geometry('500x300')
    window_single.title('重影去除')
 
    tk.Label(window_single, text='单图像重影去除',font=('Arial', 16, "bold")).place(x=170, y=50)
    # 第5步
    tk.Label(window_single, text='图像:', font=('Arial', 14)).place(x=10, y=100)
    
    # 第6步，用户输入框entry
    var_image = tk.StringVar()
    var_image.set('输入图像路径')
    entry_image = tk.Entry(window_single, textvariable=var_image, font=('Arial', 14), width = 27)
    entry_image.place(x=100,y=100)
 
    # 下面的 single_start
    btn_comfirm_single = tk.Button(window_single, text='开始', command=single_start)
    btn_comfirm_single.place(x=220, y=200)
    

# 第7步，按钮
btn_login = tk.Button(window, text='重影去除', command=single)
btn_login.place(x=225, y=240)

# 第10步，主窗口循环显示
window.mainloop()