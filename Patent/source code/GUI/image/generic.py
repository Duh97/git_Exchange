import numpy as np
import os
import cv2
from time import time
from collections import OrderedDict


def preprocessing(img):
    """
    Tilt correction => Binarization => Clear background
    """
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary_img = cv2.adaptiveThreshold(gray_img, 255, 1, 1, 11, 2)
    text_img = get_text_img(binary_img, img)
    return text_img


def preprocessing2(img):
    """
    Tilt correction => Binarization => Canny => Clear background
    """
    origin = img.copy()
    gray = cv2.cvtColor(origin, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edge_img = cv2.Canny(gray, 75, 200)

    return edge_img


def find_boxes(img):
    start = time()
    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    img_h, img_w = img.shape
    candidate = []
    vertical = 0
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        if h >= w and h > 20 and w > 5 and w < 60 and h < 60:
            candidate.append((x, y, w, h))
        elif w > h and h > 20 and w > 5 and w < 60 and h < 60:
            vertical += 1

    ratio = vertical / len(contours)
    candidate = sorted(candidate, key=lambda x: (x[1], x[0]))
    white_img = np.full((img_h, img_w, 1), 255, np.uint8)

    bboxes = []
    for (x, y, w, h) in candidate:
        if (white_img[y:y+h, x:x+w, 0].all()):
            bboxes.append((x, y, w, h))
            white_img[y:y+h, x:x+w, 0] = np.full((h, w), 0, np.uint8)
        else:
            continue

    # print(f'Time [find boxes]: {time() - start} s')

    return bboxes, ratio


def group_char_to_word(bboxes):
    candidate = dict()

    for (x, y, w, h) in bboxes:
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
                        words = [(x, y, w, h)]
                        stop = -1
            if stop != -1:
                word_positions.append(words)

    return word_positions


def get_text_img_by_bbox(bboxes, origin_img):
    white_img = np.full(origin_img.shape, 255, np.uint8)
    for x, y, w, h in bboxes:
        white_img[y:y+h, x:x+w, :] = origin_img[y:y+h, x:x+w, :]

    return white_img


def get_text_img(binary_img, origin_img, w_range=(5, 50), h_range=(15, 55)):
    white_map = np.full(origin_img.shape, 255, np.uint8)
    # Find contours for all elements
    contours, _ = cv2.findContours(
        binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    w_min, w_max = w_range
    h_min, h_max = h_range

    all_w = []
    all_h = []
    rects = []
    # Calculate mean of width and height of all candidate bbox
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)

        if (w < w_max) and (h < h_max):
            rects.append((x, y, w, h))
            all_w.append(w)
            all_h.append(h)

    w_mean = np.mean(all_w)
    h_mean = np.mean(all_h)
    w_min = min(w_mean, w_min)
    h_min = min(h_mean, h_min)

    for x, y, w, h in rects:
        if (w > w_min and h > h_min):
            white_map[y:y+h, x:x+w, :] = origin_img[y:y+h, x:x+w, :]

    return white_map


def get_rotate_angle(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.bitwise_not(gray_img)
    thresh = cv2.threshold(gray_img, 0, 255,
                           cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))

    return (cv2.minAreaRect(coords)[-1])


def img_correction(img):
    # angle = get_rotate_angle(img)
    # print('angle:', angle)
    # if (angle < 87 or angle > 93):
    #     return img

    angle = 90
    (h, w) = img.shape[:2]
    (center_x, center_y) = (w // 2, h // 2)

    # get rotate matrix: sin cos
    rotate_mat = cv2.getRotationMatrix2D((center_x, center_y), -angle, 1.0)
    cos = np.abs(rotate_mat[0, 0])
    sin = np.abs(rotate_mat[0, 1])

    # calculate new w, h
    new_w = int((h * sin) + (w * cos))
    new_h = h

    # adjust rotate matrix
    rotate_mat[0, 2] += (new_w / 2) - center_x
    rotate_mat[1, 2] += (new_h / 2) - center_y

    return cv2.warpAffine(img, rotate_mat, (new_w, new_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def save_img(img, root_path, img_name):
    """
    Save image (numpy format, opencv format)
    """
    if not os.path.isdir(root_path):
        try:
            os.mkdir(root_path)
        except FileExistsError:
            print('"{}" already exist.'.format(root_path))
    full_path = os.path.join(root_path, img_name)
    cv2.imwrite(full_path, img)


def is_number(num_str):
    try:
        _ = int(num_str)
        return True
    except ValueError:
        return False


def find_blank_area(img, x, y, w, h):
    img_h, img_w, _ = img.shape
    is_find = False

    tmp_x = -1
    tmp_y = -1
    raw = y
    col = x
    while (raw < img_h - h - 3):
        while (col < img_w - w - 3):
            # print(raw, col)
            area = img[raw:raw+h, col:col+w, :]
            if np.any(area == 0):
                indices = np.where(np.all(area == 0, axis=-1))
                # print(indices)
                tmp_x = max(indices[0]) + col
                tmp = max(indices[1]) + raw
                if (tmp > tmp_y):
                    tmp_y = tmp

                if (tmp_x + w + 3 > img_w):
                    break
                else:
                    col = tmp_x + 1
            else:
                new_x = col
                new_y = raw
                is_find = True
                break

        if (is_find):
            break
        elif (tmp_y + h + 3 >= img_h):
            break
        else:
            col = x
            raw = tmp_y + 1

    if (is_find):
        return (new_x, new_y)
    else:
        return (x, y)


def get_txt_map(file_name):
    txt_map = dict()
    if os.path.isfile(file_name):
        with open(file_name, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            key, content = line.split(',')
            txt_map[key] = content
    else:
        print('{} does not exits!'.format(file_name))

    return txt_map


def text_maping(map_path, words):
    """
    Get text by mapping key
    Get width, height of area of all text
    """
    area_w = 0
    area_h = 0
    text_list = []
    txt_map = get_txt_map(map_path)

    # Get draw area of all text
    for key in words:
        if key in txt_map.keys():
            val = txt_map.get(key)
            content = key + ' ' + val
            text_list.append(content)
            (txt_w, txt_h), _ = cv2.getTextSize(
                content, cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, 1)
            if (txt_w > area_w):
                area_w = txt_w + 10
            area_h += txt_h

    text_list = sorted(text_list)
    return (text_list, area_w, area_h)


def draw_text(img, text_area):
    text_list, area_w, area_h = text_area
    if (len(text_list) != 0):
        # Get blank area in picture
        white_x, white_y = find_blank_area(
            img, 10, 10, area_w, area_h)

        for content in text_list:
            (txt_w, txt_h), baseline = cv2.getTextSize(
                content, cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, 1)
            cv2.putText(img, content, (white_x + 10, white_y + txt_h),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 0, 0), 1, cv2.LINE_AA)
            white_y += (txt_h + baseline)
