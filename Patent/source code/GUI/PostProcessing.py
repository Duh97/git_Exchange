# coding=utf8

'''
version: August 30, 2021 11:00 AM
Last revision: October 01, 2021 04:05 PM

Author : Chao-Hsuan Ko
'''

import re

class PostProcessing():

    def __init__(self, getId):
        self.getId = ""
        self.main_processing(getId)

    def numberCheck(self, inputStr):
        NumRegex = re.compile(r'(\d{3}[a-z]?)')
        mo = NumRegex.search(inputStr)
        if (mo is None):
            checkIndex = 0
        else:
            checkIndex = 1
        return checkIndex

    def characterCheck(self, inputStr):
        CharRegex = re.compile(r'([a-zA-Z]{2,4})')
        mo = CharRegex.search(inputStr)
        if (mo is None):
            checkIndex = 0
        else:
            checkIndex = 1
        return checkIndex

    def main_processing(self, patent_id):
        readfilePath = 'output/' + patent_id;
        readfileName_content = "description.txt"
        readfileName_keywords = patent_id +'_keyword'
        outputfilePath = readfilePath
        outputfile = readfileName_keywords + "_postprocessing"
        readfileName_keywords += '.txt'
        outputfile += '.txt'

        f_content = open(readfilePath + '/' + readfileName_content, 'r', encoding="utf-8")
        f_keywords = open(readfilePath + '/' + readfileName_keywords, 'r', encoding="utf-8")
        # read file
        content = f_content.read()
        # replace
        content = content.replace("[", "")
        content = content.replace("]", "")
        content = content.replace("'", "")

        # output post_processing file
        fo = open(outputfilePath + '/' + outputfile, "w", encoding='utf-8')  # 'a' --> overlapping

        # result parameters
        id_list = []
        keyword_list = []
        # read each lines (keyword)
        tmp = []
        for line in f_keywords:
            tmp = line.split(':')
            if 2 <= len(tmp[0].strip()) <= 4:
                numberTag = self.numberCheck(tmp[0].strip())
                if numberTag:
                    indexTag = 0
                    if ',' in tmp[1]:
                        keywordArray = tmp[1].split(',')
                        keywordArray_1 = keywordArray[0].strip().replace("[", "")
                        keywordArray_2 = keywordArray[1].strip().replace("]", "")
                        keywordArray_1 = keywordArray_1.replace("'", "")
                        keywordArray_2 = keywordArray_2.replace("'", "")
                        index1 = content.casefold().find(keywordArray_1.strip().casefold())
                        index2 = content.casefold().find(keywordArray_2.strip().casefold())
                        if index1 < index2:
                            indexTag = 1
                            if len(keywordArray_1) < len(keywordArray_2):
                                indexTag = 2
                        else:
                            indexTag = 2
                            if len(keywordArray_2) < len(keywordArray_1):
                                indexTag = 1
                    else:
                        indexTag = 1
                        keywordArray_1 = tmp[1]
                        keywordArray_2 = tmp[1]

                    if (indexTag == 1):
                        id_list.append(tmp[0])
                        keyword_list.append(keywordArray_1)
                    else:
                        #print(tmp[0], keywordArray_2)
                        id_list.append(tmp[0])
                        keyword_list.append(keywordArray_2)
                    # print(index1, index2)
                else:
                    charTag = self.characterCheck(tmp[0].strip())
                    if charTag:
                        word = tmp[1].strip()
                        word = word.strip().replace("['", "")
                        word = word.strip().replace("']", "")
                        id_list.append(tmp[0].strip())
                        keyword_list.append(word.strip())

        # output
        for i in range(len(id_list)):
            if (i!=len(id_list)-1):
                fo.writelines(id_list[i].strip() + "," + keyword_list[i] + "\n")
            else:
                fo.writelines(id_list[i].strip() + "," + keyword_list[i])


        f_content.close()
        f_keywords.close()
        fo.close()
