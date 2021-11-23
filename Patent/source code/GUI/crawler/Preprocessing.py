'''
version: September 13, 2021 02:10 PM
Last revision: September 13, 2021 02:10 PM

Author : ITING.TU / Chao-Hsuan Ko
'''

from .Preprocessing_Number import Preprocessing_Number
from .Preprocessing_Character import Preprocessing_Character

class Preprocessing:
    getId = ''
    #keyword_dict = dict()
    returnDic_N = dict()
    returnDic_C = dict()

    def __init__(self, getId):
        self.getId = getId

        # check Number in PATENT
        PN = Preprocessing_Number(getId)
        returnDic_N = PN.returnDic
        #print('N',returnDic_N)
        # check English in PATENT
        PC = Preprocessing_Character(getId)
        returnDic_C = PC.returnDic
        #print('C',returnDic_C)

        # 暫存編號和關鍵字對應檔
        file = open('output/' + str(getId) + '/' + str(getId) + '_keyword.txt', 'w', encoding="utf-8")
        for key, value in returnDic_N.items():
            file.write(str(key) + " : " + str(value) + "\n")
        for key, value in returnDic_C.items():
            file.write(str(key) + " : " + str(value) + "\n")