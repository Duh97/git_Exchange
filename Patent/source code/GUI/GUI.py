'''
version: September 08, 2021 09:12 AM
Last revision: October 19, 2021 03:20 PM

Author : Chao-Hsuan Ko
'''

import tkinter as tk
from tkinter import END, W, E

from crawler.Crawler import Crawler
from crawler.Preprocessing import Preprocessing
from PostProcessing import PostProcessing
from image.Image_Main import Image_Main
from crawler.Image_to_PPT import Image_to_PPT

window = tk.Tk()
window.title('Patent')
window.geometry('370x390')  # width / high
window.resizable(False, False)

'''
US20210011510A1
US20120158633A1
'''
'''
四位數
US10909441
'''
'''
數字+英文
US10909441
'''
'''
有底線
US20210167154A1
'''
'''
有括號
US10909441
'''
'''
英文字
US20210167154A1
'''


crawler = Crawler()


def button_Processing():
    idList = []
    if (len(text_1.get()) != 0):
        txt_output.configure(state='normal')
        txt_output.update()
        stateCode = crawler.get_pattentID(text_1.get())
        idList.append(text_1.get())
    else:
        idList = (txt_input.get(1.0, tk.END + "-1c").replace(" ", "")).split('\n')      # Save input ids as list
        crawler.get_pattentID(idList[0])
        stateCode = crawler.get_pattentID(idList[0])

    if stateCode == 200:
        for pattenId in idList:
            txt_output.configure(state='normal')
            txt_output.insert(END, pattenId + '處理中'+ '\n')
            txt_output.update()
            label_4['text'] = str(pattenId)
            label_2['text'] = '處理中'
            label_4.update()
            label_2.update()
            crawler.get_pattentID(pattenId)
            Preprocessing(pattenId)
            PostProcessing(pattenId)
            label_2['text'] = '數字辨識中'
            label_2.update()
            Image_Main(pattenId)
            label_2['text'] = '正在產生PPT'
            label_2.update()
            Image_to_PPT(pattenId)
            txt_output.insert(END, pattenId + '處理完成' + '\n')
            txt_output.update()
            label_2['text'] = '處理完成'
            label_2.update()
        label_4['text'] = ''
        label_2['text'] = '全部執行完成'
        label_4.update()
        label_2.update()
        txt_output.insert(END, '全部執行完成' + '\n')
        txt_output.update()
        txt_output.configure(state='disabled')
    elif stateCode == 404:
        txt_output.configure(state='normal')
        txt_output.insert(END, '來源資料錯誤' + '\n')
        txt_output.update()
        txt_output.configure(state='disabled')
    else:
        txt_output.configure(state='normal')
        txt_output.insert(END, '不明錯誤' + '\n')
        txt_output.update()
        txt_output.configure(state='disabled')

# Radiobutton
radioValue = tk.IntVar()
radioValue.set(1)
def radioChange():
    # disabled, normal, or readonly
    if radioValue.get() == 1:
        text_1.config(state='normal')
        txt_input.configure(state='disabled')
    elif radioValue.get() == 2:
        text_1.config(state='readonly')
        txt_input.configure(state='normal')

# Listen
def text_changed_callback(event):
    button_1.configure(state='normal')



# Input Id (Layout)
a1 = tk.Radiobutton(window, text="輸入單篇專利編號", variable=radioValue, value=1, command=radioChange).grid(column=0, row=0, sticky=W)
a2 = tk.Radiobutton(window, text="輸入多篇專利編號", variable=radioValue, value=2, command=radioChange).grid(column=0, row=1, sticky=W)
# Patent Id input
text_1 = tk.Entry(window, width=15)
text_1.grid(column=1, row=0, padx=0, pady=10, sticky=W)
text_1.bind("<Key>", text_changed_callback)
# Display Label
label_3 = tk.Label(window, text='輸入專利清單列表', fg='#263238', font=('Arial', 12))
label_3.grid(column=0, row=2, padx=10, pady=10, sticky=W)
# Patent Id input (Scrollbar)
fram1 = tk.LabelFrame(window, height=5, width=30)
txt_input = tk.Text(fram1, height=5, width=30)
txt_input.configure(state='disabled')
txt_input.bind("<Key>", text_changed_callback)
sl1 = tk.Scrollbar(fram1)
sl1['command'] = txt_input.yview
sl1.grid(column=0, row=3, sticky=E)
txt_input.grid(column=0, row=3, sticky=E)
fram1.grid(column=0, row=3, sticky=E, padx=5, pady=0)
# Text Widget
label_3 = tk.Label(window, text='結果顯示', fg='#263238', font=('Arial', 12))
label_3.grid(column=0, row=4, padx=10, pady=10, sticky=W)
# Display Textbox (Result) (Scrollbar)
fram2 = tk.LabelFrame(window, height=5, width=30)
txt_output = tk.Text(fram2, height=5, width=30)
sl2 = tk.Scrollbar(fram2)
sl2['command'] = txt_output.yview
sl2.grid(column=0, row=5, sticky=E)
txt_output.grid(row=5, column=0, sticky=E)
fram2.grid(column=0, row=5, sticky=E, padx=5, pady=0)
txt_output.configure(state='disabled')
# State Display (Label)
label_2 = tk.Label(window, text='', fg='#263238', font=('Arial', 12))
label_2.grid(column=1, row=7, padx=0, pady=0)
label_4 = tk.Label(window, text='', fg='#263238', font=('Arial', 10))
label_4.grid(column=1, row=6, padx=0, pady=3)

# Search Button
#button_1 = tk.Button(window, text='Search', command=getInputId)
button_1 = tk.Button(window, text='Search', command=button_Processing)
button_1.grid(column=0, row=6, padx=10, pady=20, sticky=W)
button_1.configure(state='disabled')



window.mainloop()


