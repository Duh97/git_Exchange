import numpy as np
import cv2
from imutils.object_detection import non_max_suppression
import pytesseract


class DLModelOCR:
    def __init__(self, model_path):
        self.__model_path = model_path

    def get_proposal_bbox(self, prob_score, geo, min_confidence=0.5):
        # Returns a bounding box and probability score if it is more than minimum confidence
        (numR, numC) = prob_score.shape[2:4]
        boxes = []
        confidence_val = []

        # loop over rows
        for y in range(0, numR):
            scoresData = prob_score[0, 0, y]
            x0 = geo[0, 0, y]
            x1 = geo[0, 1, y]
            x2 = geo[0, 2, y]
            x3 = geo[0, 3, y]
            anglesData = geo[0, 4, y]

            # loop over the number of columns
            for i in range(0, numC):
                if scoresData[i] < min_confidence:
                    continue

                (offX, offY) = (i * 4.0, y * 4.0)

                # extracting the rotation angle for the prediction and computing the sine and cosine
                angle = anglesData[i]
                cos = np.cos(angle)
                sin = np.sin(angle)

                # using the geo volume to get the dimensions of the bounding box
                h = x0[i] + x2[i]
                w = x1[i] + x3[i]

                # compute start and end for the text pred bbox
                endX = int(offX + (cos * x1[i]) + (sin * x2[i]))
                endY = int(offY - (sin * x1[i]) + (cos * x2[i]))
                startX = int(endX - w)
                startY = int(endY - h)

                boxes.append((startX, startY, endX, endY))
                confidence_val.append(scoresData[i])

        # return bounding boxes and associated confidence_val
        return (boxes, confidence_val)

    def text_detection(self, img):

        (img_h, img_w) = img.shape[:2]
        (new_w, new_h) = (320, 320)

        self.rW = img_w / float(new_w)
        self.rH = img_h / float(new_h)

        # resize the original image to new dimensions
        resize_img = cv2.resize(img, (new_w, new_h))
        (H, W) = resize_img.shape[:2]

        # construct a blob from the image to forward pass it to EAST model
        blob = cv2.dnn.blobFromImage(resize_img, 1.0, (W, H),
                                     (123.68, 116.78, 103.94),
                                     swapRB=True, crop=False)

        net = cv2.dnn.readNet(self.__model_path)

        layerNames = [
            "feature_fusion/Conv_7/Sigmoid",
            "feature_fusion/concat_3"
        ]

        # Forward pass the blob from the image to get the desired output layers
        net.setInput(blob)
        (scores, geometry) = net.forward(layerNames)

        (boxes, confidence_val) = self.get_proposal_bbox(scores, geometry)
        boxes = non_max_suppression(np.array(boxes), probs=confidence_val)

        return boxes

    def draw_text(self, img, results):
        display_image = img.copy()

        for ((start_X, start_Y, end_X, end_Y), text) in results:
            text = "".join([x if ord(x) < 128 else "" for x in text]).strip()
            cv2.rectangle(display_image, (start_X, start_Y), (end_X, end_Y),
                          (0, 0, 255), 2)
            cv2.putText(display_image, text, (start_X, start_Y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return display_image

    def text_recognition(self, img, boxes):
        results = []
        origin_img = img.copy()

        for (startX, startY, endX, endY) in boxes:
            # scale the coordinates based on the respective ratios in order to reflect bounding box on the original image
            startX = int(startX * self.rW)
            startY = int(startY * self.rH)
            endX = int(endX * self.rW)
            endY = int(endY * self.rH)

            # extract the region of interest
            r = origin_img[startY:endY, startX:endX]

            configuration = ("-l eng --oem 1 --psm 8")
            text = pytesseract.image_to_string(r, config=configuration)
            results.append(((startX, startY, endX, endY), text))

        result_img = self.draw_text(img, results)

        return result_img
