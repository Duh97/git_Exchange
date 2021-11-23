import re

import numpy as np
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords


def get_eng_keyword(description):
    keyword = []
    keyword_df = pd.DataFrame()
    # 判斷大寫 例如: AA、BB
    capital = re.findall('[A-Z]{2,4}', str(description))
    # 判斷大寫+小寫 例如: Aa、Bb
    lower = re.findall('[A-Z]{1}[a-z]{1}', str(description))
    word_list = capital + lower
    # print(word_list)
    des_tokens = preprocessing(description)
    stop_words = stopwords.words('english')
    stopwords_list = ['By', 'In', 'It', 'If', 'On', 'An', 'No', 'As']
    stop_words.extend(stopwords_list)
    # 整理所有抓取下來的單字
    for word in word_list:
        keyword_dict = {}
        if word not in keyword and word not in stop_words:
            length = len(word)
            keyword.append(word)
            index = list(np.where(np.array(des_tokens) == word))
            keyword_dict = {'keyword': word, 'length': length, 'index': list(index)}
            keyword_df = keyword_df.append(keyword_dict, ignore_index=True)
    # print(keyword_df)
    return keyword_df


def get_keyword_description(description, keyword_df):
    keyword_dict = {}
    # 單字和描述的比對
    des_tokens = preprocessing(description)
    for idx, row in keyword_df.iterrows():
        keyword_length = int(row['length'])
        keyword = row['keyword']
        keyword_index = row['index']
        keyword_des = ''
        keyword_des_list = []
        for index in keyword_index:
            if (len(index) != 0):
                for key_idx in index:
                    keyword_des = ''
                    # 根據關鍵字的字數判斷要抓取前面幾個字詞
                    for i in range(keyword_length, 0, -1):
                        keyword_des += des_tokens[key_idx - i] + " "
                if keyword_des not in keyword_des_list:
                    keyword_des_list.append(keyword_des)
                    # print(len(keyword_des_list))
                    keyword_dict.update({keyword: keyword_des_list})
    return keyword_dict


def preprocessing(description):
    token_list = []
    description = word_tokenize(str(description))
    # 去除不必要的標點符號和空白
    description_tokens = re.sub(r'[^\w\s]', '', str(description))
    description_tokens = str(description_tokens).split(" ")
    # 把處理好的單字放入token_list中
    for token in description_tokens:
        # 若token不是空字串，則放入list中
        if (len(token) != 0):
            token_list.append(token)
    return token_list


# main
# patent_id = ['US20210162865A1','US20210167154A1','US20210183961A1','US20210200503A1',
#             'US20210173487A1']
patent_id = ['US20210167320A1']
for id in patent_id:
    file_path = "./" + id
    description = []
    description_file = open(file_path + "/description.txt", 'r', encoding='utf-8')
    for line in description_file:
        description.append(line)
    keyword_df = get_eng_keyword(description)
    keyword_dict = get_keyword_description(description, keyword_df)
    # 暫存編號和關鍵字對應檔
    file = open(str(id) + '/' + str(id) + '_english_keyword.txt', 'w', encoding="utf-8")
    for key, value in keyword_dict.items():
        file.write(str(key) + " : " + str(value) + "\n")
print("檔案儲存完成")