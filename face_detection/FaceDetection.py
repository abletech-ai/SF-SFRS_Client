import numpy as np
import cv2
import os

DEPLOY_PROTOTXT_PATH = os.path.join('face_detection', 'deploy.prototxt.txt')
SSD_FACE_DETECTOR_MODEL_PATH = os.path.join('face_detection', 'res10_300x300_ssd_iter_140000.caffemodel')


class FaceDetector:
    def __init__(self, face_detector_type):
        if face_detector_type.__eq__('ssd'):
            self.detector_type = face_detector_type

            self.face_detector_model = cv2.dnn.readNetFromCaffe(DEPLOY_PROTOTXT_PATH, SSD_FACE_DETECTOR_MODEL_PATH)

    def check_and_detect(self, frame):
        """
        This function takes an image (array) and returns the following in a dictionary:
        1. original image (array) with frame drawn on it
        2. blur : True or False
        3. Box : image(array) which has detected face only.
        4. Detectable: Only true if no blur found and only one face is present.
        5. faceonly: array containing the face only
        """

        face_found = False
        detectable = False
        blurr = False
        text = 'Scan Here'
        t_color = (230, 91, 118)
        r_color = (224, 225, 225)
        img = frame.copy()
        box = img[101:101 + 300, 179:179 + 300]

        # blurr detection
        box_g = cv2.cvtColor(box, cv2.COLOR_BGR2BGRA)
        var_lap = cv2.Laplacian(box_g, cv2.CV_64F).var()

        # face detection
        (h, w) = box.shape[:2]

        blob = cv2.dnn.blobFromImage(box, 1.0, (300, 300))
        self.face_detector_model.setInput(blob)
        detections = self.face_detector_model.forward()
        big_boxes = []
        confidences = []
        # loop over the detections
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > 0.9:
                # compute the (x, y)-coordinates of the bounding box for the
                # object
                boxex = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = boxex.astype("int")

                x = int(startX - (endX / 2))
                y = int(startY - (endY / 2))

                # append boxes in lists defined above for nms
                big_boxes.append([int(startX), int(startY), int(endX), int(endY)])
                confidences.append(float(confidence))

        # perform nms
        idxs = cv2.dnn.NMSBoxes(big_boxes, confidences, 0.99, 0.1)

        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for i in idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (big_boxes[i][0], big_boxes[i][1])
                (w, h) = (big_boxes[i][2], big_boxes[i][3])
                # draw a bounding box rectangle and label on the image
                try:
                    face_crop = box[(y-10):(h+10), (x-10):(w+10)]
                except:
                    face_crop = box[y:h, x:w]

                #cv2.rectangle(box, (x, y), (w, h), (255, 255, 255), 2)

        # drawing sna box
        shapes = np.zeros_like(img, np.uint8)

        # Draw shapes
        cv2.rectangle(shapes, (180, 100), (450, 400), (254, 255, 255), cv2.FILLED)

        # Generate output by blending image with shapes image, using the shapes
        # images also as mask to limit the blending to those parts
        alpha = 0.88
        mask = shapes.astype(bool)
        frame[mask] = cv2.addWeighted(frame, alpha, shapes, 1 - alpha, 0)[mask]
        # scan box
        cv2.rectangle(frame, (180, 100), (450, 400), (254, 255, 255), 2)
        # text box
        cv2.rectangle(frame, (180, 60), (450, 95), r_color, cv2.FILLED)
        frame[mask] = cv2.addWeighted(frame, alpha, shapes, 1 - alpha, 0)[mask]
        cv2.putText(frame, text, (220, 90), 2, 1, t_color, 2)

        ### blurr checking

        if var_lap < 90:
            blurr = True
            text = 'Poor Lighting'
            r_color = (0, 0, 255)
            cv2.rectangle(frame, (180, 60), (450, 95), r_color, cv2.FILLED)
            cv2.putText(frame, text, (220, 90), 2, 1, t_color, 2)

        ### detecting faces and multi faces

        elif len(idxs) == 1:
            text = 'Face Found'
            r_color = (0, 255, 0)
            cv2.rectangle(frame, (180, 60), (450, 95), r_color, cv2.FILLED)
            cv2.putText(frame, text, (220, 90), 2, 1, t_color, 2)
            face_found = True

        elif len(idxs) > 1:
            text = 'Multi Faces'
            r_color = (0, 0, 255)
            cv2.rectangle(frame, (180, 60), (450, 95), r_color, cv2.FILLED)
            cv2.putText(frame, text, (220, 90), 2, 1, t_color, 2)

        if (not blurr) and (face_found):
            detectable = True

        output = {'frame': frame, 'box': box, 'blurr': blurr, 'detectable': detectable}

        if detectable:
            output['faceonly'] = face_crop

        return output
