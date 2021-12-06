'''
version: August 31, 2021 11:00 AM
Last revision: October 14, 2021 02:35 PM

Author : ITING.TU / Chao-Hsuan Ko
'''

import os.path
from pathlib import Path

import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from pdf2image import convert_from_path


class Crawler():
    stateCode = ''

    def __init__(self):
        self.description = ""
        self.claim = list()
        self.information = dict()

    # 抓取頁面中描述的部分
    def get_description(self, soup):
        description_resource = soup.findAll("div", class_="description-line") or soup.findAll("div",
                                                                                              class_="description-paragraph")
        description_content = [content.getText() for content in description_resource]
        self.description = description_content
        return 0

    # 抓取頁面中cliam的部分
    def get_claim(self, soup):
       #抓取 main claim
        mian_claim_resouce = soup.select("div.claim > div")
        #抓取 dependent claim
        dependent_claim_resource = soup.select("div.claim-dependent")
        main_claim = []
        dependent_claim = []
        main_claim_no = []
        #資料前處理
        for text in mian_claim_resouce:
            if text.has_attr('num'):
                if text['num'].isdigit():
                    main_claim_no.append(int(text['num']))
                    main_claim.append(text.getText().replace("\n",""))
        for text in dependent_claim_resource:
            dependent_claim.append(text.getText())
        start = 0
        end = 0
        #找出主claim下的附屬claim有哪一些
        output_claim = []
        for i in range(0, len(main_claim_no)):
            dept_claim_list = []
            #後一項的main claim編號 扣掉 前一項main claim編號 
            if (i != (len(main_claim_no)-1)):
                dept_amount = main_claim_no[i+1] - main_claim_no[i]
            else:
                dept_amount = abs(len(dependent_claim) - main_claim_no[i])
            if(dept_amount != 0):
                end += dept_amount - 1
            if end>len(dependent_claim):
                end = len(dependent_claim)
            for j in range(start, end):
                dept_claim = dependent_claim[j].replace("\n","")
                dept_claim_list.append(dept_claim)
            output_claim.append(main_claim[i])
            output_claim.append(dept_claim_list)
            start = end
        #資料存檔
        self.claim = output_claim
        return 0

    #抓取專利的相關資訊
    def get_information(self, id, soup):
        #抓取專利編號、標題、發明者、發表公司、filed date、摘要
        inventor_resouce = soup.findAll("dd",itemprop="inventor")
        assigneecurrent_resouce = soup.findAll("dd", itemprop = "assigneeCurrent")
        title_resource = soup.findAll("span", itemprop="title")
        filed_resource = soup.findAll("time", itemprop="filingDate")
        abstract_resource = soup.findAll("div", class_="abstract")
        company = []
        title = ""
        #進行資料前處理
        inventor = [text.getText() for text in inventor_resouce]
        for res in assigneecurrent_resouce:
            company_text = res.getText()
            company_text = company_text.replace('\n','')
            company.append(company_text.replace(' ',''))
        for text in title_resource:
            title_text = text.getText()
            title_text = title_text.replace('\n','').strip()
            title = title_text
        abstract = ""
        abstract_list = abstract_resource[0].getText().split(",")
        for abs in abstract_list:
            abstract += abs +'\n'
        filed_date = [text.getText() for text in filed_resource]
        #將相關資訊存入dict中
        self.information.update({"Patnet No:": id,
                            "Title : ":title,
                            "Inventor:": inventor,
                            "Company: ":company,
                            "Filed Date : ":filed_date,
                            "Abstract : ":abstract})
        # print(self.information)
        return 0

    # 儲存圖片(沒有用到seleium)
    def get_image(self, patent_id, soup):
        img_count = 0  # 計算圖片的數量
        # 是否存在images的資料夾，若沒有則建立
        if not os.path.exists('output/' + patent_id + "/images"):
            os.mkdir('output/' + patent_id + "/images")
            os.mkdir('output/' + patent_id + "/images_temp")
        # 找到所需要的image
        img_resouse = soup.findAll('meta', {'itemprop': "full"})
        for img in img_resouse:
            image_path = 'output/' + patent_id + "/images/" + str(img_count) + '.jpg'
            if not os.path.isfile(image_path):
                with open('output/' + patent_id + "/images/" + str(img_count) + ".jpg", 'wb') as file:
                    file.write(requests.get(img['content']).content)
                with open('output/' + patent_id + "/images_temp/" + str(img_count) + ".jpg", 'wb') as temp_file:
                    temp_file.write(requests.get(img['content']).content)
            else:
                print(img, 'exist')
            img_count += 1
        return 0

    def download_pdf(self, patent_id, soup):
        # 找到pdf的URL
        pdf_resouce = soup.findAll("meta", attrs = {"name":"citation_pdf_url"})
        #儲存PDF
        pdf_path = 'output/' + patent_id + "/" + patent_id +".pdf"
        for pdf in pdf_resouce:
            with open(pdf_path, "wb") as file:
                file.write(requests.get(pdf['content']).content)
        pdf_img = convert_from_path(pdf_path, first_page=1, last_page=1)
        pdf_img[0].save('output/' + patent_id +'/pdf.jpg',"JPEG")
        return 0

    # 儲存description檔案、claim檔案
    def save_file(self, patent_id):
        # 儲存description檔案
        if self.description:
            description_path = Path('output/' + patent_id + '/description.txt')
            description_path.touch(exist_ok=True)
            description_file = open(description_path, 'w', encoding='utf-8')
            description_file.write(str(self.description))
        # 儲存claims檔案
        if self.claim:
            #claim_file = open('output/' + patent_id + "/claim.txt", 'w', encoding='utf-8')
            claim_path = Path('output/' + patent_id + '/claim.txt')
            claim_path.touch(exist_ok=True)
            claim_file = open(claim_path, 'w', encoding='utf-8')
            for claim in self.claim:
                claim_file.write(str(claim)+"\n")
        # 儲存information檔案
        if self.information:
            #information_file = open('output/' + patent_id + "/information.txt", 'w', encoding='utf-8')
            information_path = Path('output/' + patent_id + '/information.txt')
            information_path.touch(exist_ok=True)
            information_file = open(information_path, 'w', encoding='utf-8')
            for key, value in self.information.items():
                information_file.write(str(key) + str(value) + "\n")
        # print("檔案儲存完成")
        return 0

    def main_processing(self, patent_id):
        url = "https://patents.google.com/patent/"
        # 搜尋每一個頁面的所有資料
        for id in tqdm(patent_id):
            respones = requests.get(url + str(id))
            stateCode = respones.status_code
            if stateCode == 200:
                # 若有真實資料 則建立資料夾
                if not os.path.exists('output/' + id):
                    os.mkdir('output/' + id)
                    #patent.stateCode = 200
                    # 抓取頁面的資訊
                    soup = BeautifulSoup(respones.text, "html.parser")
                    patent.get_description(soup)
                    patent.get_claim(soup)
                    patent.get_information(id, soup)
                    patent.get_image(id, soup)
                    patent.download_pdf(id, soup)
                    patent.save_file(id)
                else:
                    #shutil.rmtree('output/' + id)
                    #os.mkdir('output/' + id)
                    #patent.stateCode = 200
                    # 抓取頁面的資訊
                    soup = BeautifulSoup(respones.text, "html.parser")
                    patent.get_description(soup)
                    patent.get_claim(soup)
                    patent.get_information(id, soup)
                    #patent.get_image(id, soup)
                    patent.download_pdf(id, soup)
                    patent.save_file(id)
        return stateCode


    # 接收 GUI 傳入之 Patten Id
    def get_pattentID(self, getId):
        patent_id = []
        patent_id.append(getId)
        stateCode = patent.main_processing(patent_id)
        return stateCode


patent = Crawler()
