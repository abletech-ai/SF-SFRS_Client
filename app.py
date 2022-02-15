import io
import time
from datetime import datetime
import numpy as np
from flask import Flask, render_template, request, jsonify, Response
import warnings
import cv2
import json
import requests
import base64
import os
from PIL import Image
from face_detection.FaceDetection import FaceDetector

# setting up face detector
detector = FaceDetector('ssd')

warnings.filterwarnings('ignore')
DATA_FOLDER = os.path.join("static", "data")

# global counter variable for image capture and class id
CAPTURE_IMAGE = False
CLASS_ID = None


def delete_current_captured_saved_image():
    folder_path = 'static/sv_im/'

    # using listdir() method to list the files of the folder
    test = os.listdir(folder_path)
    # taking a loop to remove all the images
    # using ".png" extension to remove only png images
    for images in test:
        if images.endswith(".png"):
            os.remove(os.path.join(folder_path, images))


def web_streaming():
    global CAPTURE_IMAGE, CLASS_ID

    vid = cv2.VideoCapture(0)
    vid.set(cv2.CAP_PROP_FPS, 30)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if os.path.exists("templates/profiles.json"):
        os.remove("templates/profiles.json")

    delete_current_captured_saved_image()

    while True:
        # Capture the video
        ret, frame = vid.read()

        if frame is None:
            print("Error, Check if camera is connected!")
            break

        frame = cv2.flip(frame, 1)
        output = detector.check_and_detect(frame)

        # flip the image
        if CAPTURE_IMAGE:
            if (output['detectable']) and (output['faceonly'].all() is not None):
                request_data = {'id': CLASS_ID,
                                'face': output['faceonly'], 'box': output['box']}
                cv2.imwrite('static/sv_im/box.png', output['box'])
                resized_cropped_face = cv2.resize(request_data['face'], (400, 400))
                cv2.imwrite('static/sv_im/cropped-frame.png', resized_cropped_face)
                cv2.imwrite('static/sv_im/cropped.png', request_data['face'])

            else:
                print('Face Not Found or Lightening Issues...')

        CAPTURE_IMAGE = False

        frame = output['frame']

        # Display the resulting frame on page
        ret, jpeg = cv2.imencode('.jpg', frame)
        img = jpeg.tobytes()

        if os.path.exists('static/sv_im/cropped.png') and os.path.exists('static/sv_im/db_image.png'):
            img_st_mtime = os.stat('static/sv_im/cropped.png').st_mtime

            img_str_time = datetime.fromtimestamp(img_st_mtime).strftime("%H:%M:%S")
            current_time = datetime.now().strftime("%H:%M:%S")

            FMT = '%H:%M:%S'
            tdelta = datetime.strptime(current_time, FMT) - datetime.strptime(img_str_time, FMT)

            if int(str(tdelta).split(':')[1]) > 0 or int(str(tdelta).split(':')[-1]) > 5:
                print('resetting...')
                delete_current_captured_saved_image()

                if os.path.exists("templates/profiles.json"):
                    os.remove("templates/profiles.json")

                print('reset done.')

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = '0'
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/', methods=['POST', 'GET'])
def index():
    dummy_image = os.path.join(DATA_FOLDER, "dummy.png")
    return render_template("index.html", dummy_image=dummy_image)


@app.route('/live_streaming', methods=['POST', 'GET'])
def live_streaming():
    return Response(web_streaming(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/requests', methods=['POST', 'GET'])
def tasks():
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            print('Running tasks')

            global CAPTURE_IMAGE, CLASS_ID

            CAPTURE_IMAGE = True
            CLASS_ID = request.form['uid'].strip().rstrip()
            if len(CLASS_ID) == 0:
                CLASS_ID = None

            if os.path.exists('static/sv_im/cropped.png') and os.path.exists('static/sv_im/box.png'):
                img_st_mtime = os.stat('static/sv_im/box.png').st_mtime

                img_str_time = datetime.fromtimestamp(img_st_mtime).strftime("%H:%M:%S")
                current_time = datetime.now().strftime("%H:%M:%S")

                FMT = '%H:%M:%S'
                tdelta = datetime.strptime(current_time, FMT) - datetime.strptime(img_str_time, FMT)

                if int(str(tdelta).split(':')[1]) > 0 or int(str(tdelta).split(':')[-1]) > 10:
                    delete_current_captured_saved_image()

            # send the data to the server
            api = 'http://192.168.100.220:5000/fr'
            image_file = 'static/sv_im/cropped.png'

            time.sleep(0.5)

            if os.path.exists(image_file):
                with open(image_file, "rb") as f:
                    im_bytes = f.read()

                im_b64 = base64.b64encode(im_bytes).decode("utf8")

                headers = {'Content-type': 'application/json',
                           'Accept': 'text/plain'}

                payload = json.dumps({"id": CLASS_ID, "face": im_b64})

                response = requests.post(api, data=payload, headers=headers)
                response = response.json()
                if response['verified']:
                    db_img_bytes = base64.b64decode(response['db_image'].encode('utf-8'))
                    db_img = Image.open(io.BytesIO(db_img_bytes))
                    db_bgr_img_array = np.asarray(db_img)

                    db_rgb_img_array = cv2.cvtColor(db_bgr_img_array, cv2.COLOR_BGR2RGB)

                    db_rgb_img_array = cv2.resize(db_rgb_img_array, (400, 400))

                    cv2.imwrite('static/sv_im/db_image.png', db_rgb_img_array)

                    images_dict = {'db_img': 'static/sv_im/db_image.png',
                                   'cr_img': 'static/sv_im/cropped-frame.png',
                                   'id': response['id'].split("_")[0],
                                   'name': response['id'].split("_")[1]}

                    with open('templates/profiles.json', 'w') as outfile:
                        # Writing from json file
                        outfile.write(json.dumps(images_dict))

                    print('Welcome Mr. ' + response['id'].split('_')[1])

                    try:
                        requests.get('http://192.168.100.197/gpio/1')
                    except:
                        print('Lock Not Connected')

                    # delete_current_captured_saved_image()

                CAPTURE_IMAGE = False
                CLASS_ID = None
            else:
                print('Current Image Not Found')

    elif request.method == 'GET':
        return render_template('index.html')

    return render_template('index.html')


@app.route('/get_similarity_json', methods=['POST', 'GET'])
def get_similarity_json():
    try:
        # Opening JSON file
        with open('templates/profiles.json', 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)

        return jsonify(json_object)
    except:
        abort(404)


@app.route('/form', methods=['POST', 'GET'])
def form():
    return jsonify({'status': 'Done'})


if __name__ == '__main__':
    app.run(debug=True)
