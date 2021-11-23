from collections import OrderedDict
import numpy as np
import cv2
import pytesseract
from time import time


class TextOCR:
    """
    Do OCR on patent image
    """

    def __init__(self):
        self.__digits = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        self.__char_ascii = list(range(48, 58)) + \
            list(range(65, 91)) + list(range(97, 123))

    def text_detection(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary_img = cv2.adaptiveThreshold(gray_img, 255, 1, 1, 11, 2)
        contours, _ = cv2.findContours(
            binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidate = dict()

        for cnt in contours:
            if cv2.contourArea(cnt) > 50:
                [x, y, w, h] = cv2.boundingRect(cnt)
                # check if it is letter
                if (h > 15 and w > 10 and h < 60 and w < 60):
                    if candidate.get(y+h, None) == None:
                        candidate[y+h] = []
                        candidate[y+h].append([x, y, w, h])
                    else:
                        candidate[y+h].append([x, y, w, h])

        candidate = OrderedDict(sorted(candidate.items()))
        word_positions = []
        bias = []

        for key, val in candidate.items():
            if (key in bias):
                continue
            else:
                bias = list(range(key+1, key+4))

            temp = val
            for i in bias:
                if i in candidate.keys():
                    temp += candidate.get(i)

            stop = -1
            words = []
            num = 0
            if (len(temp) > 1):
                temp = sorted(temp, key=lambda elem: elem[0])
                for (x, y, w, h) in temp:
                    if stop == -1:
                        num = 1
                        stop = (x+w, y+h)
                        words.append((x, y, w, h))
                    else:
                        if (x - stop[0] < 20):
                            stop = (x + w, y + h)
                            words.append((x, y, w, h))
                            num += 1
                        else:
                            word_positions.append(words)
                            words = []
                            stop = -1
                if stop != -1:
                    word_positions.append(words)

        return word_positions

    def single_char_recognition(self, cahr_img, bordersize=5):
        start = time()
        fill_val = 255
        border_img = cv2.copyMakeBorder(
            cahr_img,
            top=bordersize,
            bottom=bordersize,
            left=bordersize,
            right=bordersize,
            borderType=cv2.BORDER_CONSTANT,
            value=[fill_val, fill_val, fill_val]
        )
        recognition = 'tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        text = pytesseract.image_to_string(
            border_img, config='--psm 10 -c ' + recognition)
        text = text.replace('\n', '')
        text = text.replace('\x0c', '')
        text = ''.join(
            [x if ord(x) in self.__char_ascii else '' for x in text]).strip()
        #print(f'Time[char recognition]: {time() - start} s')

        return text

    def word_recogition(self, word_img, bordersize=5):
        fill_val = 255
        border_img = cv2.copyMakeBorder(
            word_img,
            top=bordersize,
            bottom=bordersize,
            left=bordersize,
            right=bordersize,
            borderType=cv2.BORDER_CONSTANT,
            value=[fill_val, fill_val, fill_val]
        )
        recognition = 'tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        text = pytesseract.image_to_string(
            border_img, config='--psm 7')  # -c ' + recognition)
        # print(f'GG:{text}')
        text = text.replace('\n', '')
        text = text.replace('\x0c', '')
        text = ''.join(
            [x if ord(x) in self.__char_ascii else '' for x in text]).strip()

        return text

    def show_roi(self, roi, bordersize=5):
        fill_val = 255
        border_img = cv2.copyMakeBorder(
            roi,
            top=bordersize,
            bottom=bordersize,
            left=bordersize,
            right=bordersize,
            borderType=cv2.BORDER_CONSTANT,
            value=[fill_val, fill_val, fill_val]
        )
        cv2.imshow('demo', border_img)
        cv2.waitKey(7000)

    def text_recognition(self, img, word_positions):
        results = []

        for boxes in word_positions:
            ans = ''
            for idx, (x, y, w, h) in enumerate(boxes):
                roi = img[y:y+h, x:x+w, :]

                if (idx < 5):
                    ans += self.single_char_recognition(roi, 15)
                else:
                    ans += self.single_char_recognition(roi, 20)

                if (idx == 0) and (ans not in self.__digits):
                    break

            if (len(ans) > 1):
                results.append(ans)

        return results

    def text_recognition_by_word(self, img, word_positions):
        results = []

        for boxes in word_positions:
            x1, y1, _, _ = boxes[0]
            x2, y2, w, h = boxes[-1]
            x2 += w
            y2 += h
            roi = img[y1:y2, x1:x2, :]
            #self.show_roi(roi, 50)
            ans = self.word_recogition(roi, 50)
            if len(ans) != 0:
                if (ans[0] in self.__digits) or (len(ans) < 5):
                    results.append(ans)

        return results
