'''
version: August 31, 2021 11:00 AM
Last revision: October 01, 2021 05:08 PM

Author : ITING.TU / Chao-Hsuan Ko
'''

import re
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class Preprocessing_Number():
 returnDic = dict()

 def __init__(self, getId):
  self.getId = getId
  self.main_processing(getId)

 # 找到編號
 def find_no(self, description):
  # 找到文章中"數字"、"數字 "、"數字 英文字母"形式的所有字串
  search_no = re.findall('[0-9]+\s?[a-e]?', str(description))
  no_list = []
  for no in search_no:
   # 把抓下來的字串前後空白移除
   no = str(no).strip()
   # 如果編號沒有重複且不是空字串
   if no not in no_list and len(no) != 0:
    no_list.append(no)
  return no_list

 # 進行資料前處理
 def preprocessing(self, description):
  token_list = []
  temp_token = []
  # 先將所有單字進行分割
  description = word_tokenize(str(description))
  # 去除不必要的標點符號和空白pyinstaller -F --hidden-import=queue
  temp_token = re.sub(r'[^\w\s]', '', str(description))
  temp_token = str(temp_token).split(" ")
  # 把處理好的單字放入token_list中
  for token in temp_token:
   # 若token不是空字串，則放入list中
   if (len(token) != 0):
    token_list.append(token)
  return token_list

 # 找到編號中所有的單字組合
 def find_word(self, number_list, description):
  token = self.preprocessing(description)
  number_word_match_dict = {}
  # 設定停用字list
  stop_words = stopwords.words('english')
  stop_words.extend(['At', 'eg', 'within', 'to'])
  # 儲存月份縮寫
  month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  alpha = ['a', 'b', 'c', 'd', 'e']
  # 進行編號和關鍵字的比對
  for no in number_list:
   word_list = []
   # 若編號在token_list內且未進入字典中(字典部分有bug)
   if no in token:
    # 判斷是否為日期的flag
    not_add_flag = 0
    # 找到編號的位子
    index_list = np.where(np.array(token) == no)
    index_list = list(index_list)
    # 找編號前面的二到五個單字
    for index in index_list:
     for posotion in index:
      word = ""
      # 如果編號的前面第二個不是月份
      if token[posotion - 2] not in month:
       not_add_flag = 0
       # 總共抓取前面五個單字
       for i in range(0, 5):
        if (token[posotion - (i + 1)] not in stop_words):
         word = token[posotion - (i + 1)] + " " + word
        if (len(word) != 0):
         word_list.append(word.lower().rstrip())
       # 如果編號的後面第一個是單一個英文字母(代表此編號可能有補充)
       if token[posotion + 1] in alpha and len(str(token[posotion + 1])) == 1:
        for al in alpha:
         # 如果編號後的單字符合字母list的話，則把編號加入字母
         if (token[posotion + 1] == al):
          number = token[posotion] + " " + al
          # print(number)
        # 如果編號有在number_list中，則更新字典
        if (number in number_list):
         number_word_match_dict.update({number: word_list})
      else:
       not_add_flag = 1
     # 判斷此編號是否為年份
     if (not_add_flag == 0):
      number_word_match_dict.update({no: word_list})
  return number_word_match_dict

 # 進行關鍵字的頻率計算並找到最佳的兩個關鍵字
 def check_keyword(self, number_word_match_dict):
  keyword_dict = dict()
  # 計算頻率
  for key, value in number_word_match_dict.items():
   word_list = []
   frequrncy_dict = dict()  # 儲存對應單字出現在number_word_match_dict的次數
   # 把重複的字串刪除
   for word in value:
    if (word not in word_list):
     word_list.append(word)
   # 計算頻率
   for word in word_list:
    frequrncy = value.count(word)
    frequrncy_dict.update({word: frequrncy})
    # 將頻率由大到小排序
    frequrncy_dict = dict(sorted(frequrncy_dict.items(), key=lambda x: x[1], reverse=True))
   # 取frequrncy_dict中頻率最高的兩個關鍵字
   keyword = [word for word in frequrncy_dict.keys()][:2]
   if len(keyword)==1:
    newDic = []
    newDic.append(keyword[0])
    newDic.append(keyword[0])
    keyword = newDic
   elif len(keyword)==2:
    keyword_dict.update({key: keyword})
  return keyword_dict

 def main_processing(self, patent_id):
  file_path = 'output/' + str(patent_id)  # 資料夾的位置
  description = []
  # 打開資料夾，將data儲存到descrition中
  description_file = open(file_path + "/description.txt", 'r', encoding='utf-8')
  for line in description_file:
   description.append(line)

  # 找到文章中的編號，將結果回傳
  number_list = self.find_no(description)
  number_word_match_dict = self.find_word(number_list, description)
  self.returnDic = self.check_keyword(number_word_match_dict)

