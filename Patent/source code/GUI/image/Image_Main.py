'''
version: September 23, 2021 15:05 PM
Last revision: October 21, 2021 05:30 PM

Author : Ray.Jiang / Chao-Hsuan Ko


https://www.jianshu.com/p/93ab58dea50f

'''

#import csv
from os import listdir
from os.path import isfile, join
from pathlib import Path
#from time import time
from .generic import *
from .TextOCR import TextOCR
from .DLModelOCR import DLModelOCR
from .Evaluator import Evaluator

class Image_Main():

    def __init__(self, getId):
        self.getId = ""
        #self.main(False, getId)
        self.demo(getId)

    def get_allPicture(self, pictureFolder):
        picture_list = []
        files = listdir(pictureFolder)
        if (os.path.exists(pictureFolder)):
            for fileName in files:
                fullpath = join(pictureFolder, fileName)
                if isfile(fullpath):
                    picture_list.append(fileName)

        return picture_list

    def demo(self, getId):
        ROOT_PATH = './output/'
        PICTURE_PATH = ROOT_PATH + str(getId) + '/images/'
        # MAP_PATH = 'output/' + getId + '/' + getId + '_keyword_postprocessing.txt'
        # SAVE_PATH = './output/'+ getId + '/results/'
        # SAVE_NAME = '{}'
        # DETECTION_MODEL_PATH = '../frozen_east_text_detection.pb'
        img_list = self.get_allPicture(PICTURE_PATH)
#        ground_truth = []
        #img_list = []
        LABEL_PATH = './image/ground_truth.csv'

        # Open csv file of ground truth
        # with open(LABEL_PATH, 'r') as csv_file:
        #     rows = csv.reader(csv_file, delimiter=',')
        #     for img_path, ans, rotate in rows:
        #         if (img_path == 'fileName'):
        #             continue
        #         img_list.append(img_path)
        #         ground_truth.append((ans, rotate))

        ocr = TextOCR()
        #eva = Evaluator()

        # create '{id}_idtext_Mapping.txt'
        mapping_path = Path(ROOT_PATH + getId + '/' + getId + '_idtext_Mapping.txt')
        mapping_path.touch(exist_ok=True)
        fo = open(mapping_path, 'w', encoding='utf-8')

        start1 = time()
        for idx, img_path in enumerate(img_list):
            img_name = img_path.split('/')[-1]
            print(f'Image count: {idx + 1}, name: {img_name}')
            start = time()
            full_path = os.path.join(ROOT_PATH, img_path)
            origin_img = cv2.imread(PICTURE_PATH+img_path)
            edge_img = preprocessing2(origin_img)
            bboxes, vertical_ratio = find_boxes(edge_img)
            is_roate = (vertical_ratio > 0.5)

            if (is_roate):
                print(vertical_ratio)
                origin_img = img_correction(PICTURE_PATH)
                edge_img = preprocessing2(PICTURE_PATH)
                bboxes, _ = find_boxes(edge_img)

            word_bboxes = group_char_to_word(bboxes)
            # Text recognition
            words = ocr.text_recognition_by_word(origin_img, word_bboxes)
            # Remove redundant words
            wordset = set(words)
            # Sort word list
            words = list(wordset)
            words = sorted(words)
            print(words)
            # output text_list
            fo.writelines(img_name + "@@" + str(words[0:]) + "\n")

            # ans_str, rotate = ground_truth[idx]
            # eva.evaluate_rotate(rotate, is_roate)
            # eva.evaluate(ans_str.split('|'), words, img_path)
            print(f'Execution time: {time() - start} s')

        print(f'Total execution time: {time() - start1} s')
        # Evaluation
        # print(f'OCR Accuracy: {eva.get_total_acc():.2f}')
        # print(f'OCR Accuracy (digit): {eva.get_digit_acc():.2f}')
        # print(f'OCR Accuracy (eng): {eva.get_eng_acc():.2f}')
        # eva.display_rotate_acc()
        # print()
        # eva.display_missing_words()


    def main(self, use_dl, getId):
        root_path = 'output/'
        PICTURE_PATH = root_path + getId + '/images/'
        MAP_PATH = 'output/' + getId + '/' + getId +'_keyword_postprocessing.txt'
#        SAVE_PATH = './output/'+ getId + '/results/'
#        SAVE_NAME = '{}'
        DETECTION_MODEL_PATH = '../frozen_east_text_detection.pb'
        img_list = self.get_allPicture(PICTURE_PATH)

        # create '{id}_idtext_Mapping.txt'
        mapping_path = Path(root_path + getId +'/' + getId + '_idtext_Mapping.txt')
        mapping_path.touch(exist_ok=True)
        fo = open(mapping_path, 'w', encoding='utf-8')

        for idx, img_name in enumerate(img_list):
            print('Image count:', idx + 1)
            start = time()
            # 0. Read image
            #full_path = os.path.join(root_path, img_name)
            full_path = os.path.join(PICTURE_PATH, img_name)
            origin_img = cv2.imread(full_path)
            # 1. Preprocessing (Tilt correction, binarization, clear background)
            origin_img = img_correction(origin_img)
            text_img = preprocessing(origin_img)

            if use_dl:
                dl_ocr = DLModelOCR(DETECTION_MODEL_PATH)
#                words_positions = dl_ocr.text_detection(text_img)
#                res_img = dl_ocr.text_recognition(origin_img, words_positions)
#                save_img(res_img, SAVE_PATH, SAVE_NAME.format(img_name))
            else:
                ocr = TextOCR()
                # 2. Text detection
                words_positions = ocr.text_detection(text_img)
                # 3. Text recognition
                words = ocr.text_recognition(text_img, words_positions)
                print(words)
                # 4. Text Mapping
                text_list, area_w, area_h = text_maping(MAP_PATH, words)
                # 5. Draw Text
#                draw_text(origin_img, (text_list, area_w, area_h))
                # 6. Save result image
#                save_img(origin_img, SAVE_PATH, SAVE_NAME.format(img_name))
                # 7. output text_list
                fo.writelines(img_name + "@@" + str(text_list[0:]) + "\n")

            print('Execution time:', time() - start, 's')

        fo.close()