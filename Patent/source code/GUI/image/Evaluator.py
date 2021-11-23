import numpy as np

from .generic import is_number


class Evaluator:
    """ Evaluate accuracy of OCR """

    def __init__(self):
        self.rotate_total = 0
        self.rotate_count = 0
        self.digit_accuracy = []
        self.eng_accuracy = []
        self.total_accuracy = []
        self.missing = dict()

    def evaluate(self, target, predict, img_name):
        missing_words = []
        digit_count = 0
        digit_amount = 0
        eng_count = 0
        eng_amount = 0

        for ans in target:
            if is_number(ans):
                digit_amount += 1
                if ans in predict:
                    digit_count += 1
                else:
                    missing_words.append(ans)
            else:
                eng_amount += 1
                if ans in predict:
                    eng_count += 1
                else:
                    missing_words.append(ans)

        self.digit_accuracy.append(digit_count / digit_amount)
        if eng_amount != 0:
            self.eng_accuracy.append(eng_count / eng_amount)

        self.total_accuracy.append((digit_count + eng_count) / len(target))
        if len(missing_words) != 0:
            self.missing[img_name] = missing_words

    def evaluate_rotate(self, target, predict):
        if predict:
            self.rotate_count += 1
            if target == 'y':
                self.rotate_total += 1

    def get_digit_acc(self):
        return np.mean(self.digit_accuracy)

    def get_eng_acc(self):
        return np.mean(self.eng_accuracy)

    def get_total_acc(self):
        return np.mean(self.total_accuracy)

    def display_missing_words(self):
        print('Missing Words')
        print('=============')
        for img_name, missing_words in self.missing.items():
            print(f'{img_name:<}: {missing_words}')

    def display_rotate_acc(self):
        print(f'Rotate number (target): {self.rotate_total}')
        print(f'Rotate number (predict): {self.rotate_count}')
