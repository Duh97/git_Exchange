## 20210818 IPD 智財 專利分析
專案起始時間: August 18, 2021

### version
2.0.0 新增 Image to PPT 


### GUI
整合 'crawler'與 'image processing' 個功能, 並建一視窗畫操作介面

##### 功能
1. 辨識圖片中數字
2. 把圖片中辨識出的數字對應文件結果 {Patent_ID}\_keyword\_postprocessing.txt
3. 將結果輸出至圖形中


##### 執行程序
1. 自動擷取 Google Patent 資料, 產生 claim.txt 與 description.txt
2. 辨識 數字-專有名詞
3. 辨識 英文-專有名詞
4. 後處理, 取出 '數字-專有名詞'最適當之結果 
5. 將整合 '數字-專有名詞' 與 '英文-專有名詞' 結果合併輸出 {Patent_ID}\_keyword\_postprocessing.txt


### crawler
宜庭 & 兆軒開發 
### image processing
啓睿 開發

---
### 套件安裝
1. poppler 
下載 [poppler](https://blog.alivate.com.au/poppler-windows/) <br> 
將解壓縮後的資料夾放在某個磁碟中(不限任何地方), 再把{該路徑}/bin 放到環境變數裡面 <br>
示範: [https://newbedev.com/how-to-install-poppler-on-windows](https://newbedev.com/how-to-install-poppler-on-windows)
2. tesseract-ocr-w64-setup-v5.0.0-alpha.20210811
下載 [Tesseract-OCR](https://digi.bib.uni-mannheim.de/tesseract/)<br>

### 修正辨識模型
1. [jTessBoxEditor](http://vietocr.sourceforge.net/training.html)
2. Character_revised : 修改OCR辨 model (包含說明檔)


---
### 執行檔編碼
###### 使用 py2exe

1. 進入 欲打包目錄料夾 cd {/location}
2. (新增)設定 setup.py
3. 執行以下指令 <br>
```
python setup.py py2exe
```

###### 錯誤查找
與打包後執行檔 {filename.exe} 相同資料夾位置中, 在執行過後會產生一個 {filename}.log 可以查詢程式執行時是否發生問題 ?

---

### 遇到之問題
1. Python 使用不同套件打包時狀況:
一般常使用 PyInstaller 或 py2exe 將Python打包成exe 檔, 但使用 PyInstaller 打包會造成檔案過大, 因此建議使用 py2exe 進行打包 

2. 使用 py2exe 打包後無法在 windows 32 位元環境下執行
解決: 需安裝 Python for 32 bits 再重新打包

3. 打包後缺乏 nltk 套件 <br>  
a. nltk_data/tokenizers/punkt/english.pickle <br>
b. nltk_data/corpora/stopwords
解決: 在 ```import nltk``` 下加上 ```nltk.download()```, 執行時會自動下載 nltk 套件至 
C:\Users\{user}\AppData\Roaming\nltk_data <br>
複製一份 nltk\_data 資夾至執行檔目錄內即可

4. 遭遇  File "tkinter\_\_init\_\_.pyc", line 2023, in \_\_init\_\_\_tkinter.TclError: 問題
解決: 安裝 tkinter

5. 若客戶端無法安裝 Python 等套件 <br>
解決: 使用 PortablePython 版本 [https://sourceforge.net/projects/portable-python/](https://sourceforge.net/projects/portable-python/) 下載到客戶端執行





##### 更新日期
November 23, 2021 <br>
08:20 AM