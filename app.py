# #!/usr/bin/env python
# from flask import Flask, render_template, Response
# import numpy as np
# import cv2
# import matplotlib.pyplot as plt
#
# app = Flask(__name__)
# #vc = cv2.VideoCapture(0)
#
# @app.route('/')
# def index():
#     """Video streaming home page."""
#     return render_template('index.html')


# def gen():
#     """Video streaming generator function."""
#     while True:
#         rval, frame = vc.read()
#         cv2.imwrite('t.jpg', frame)
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')
#
#
# @app.route('/video_feed')
# def video_feed():
#     """Video streaming route. Put this in the src attribute of an img tag."""
#     return Response(gen(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# def gen():
#     """Video streaming generator function."""
#     while True:
#         rval, frame = vc.read()
#         cv2.imwrite('t.jpg', frame)
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')
#
# @app.route('/video_feed')
# def video_feed():
#     """Video streaming route. Put this in the src attribute of an img tag."""
#     return Response(gen(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# img = cv2.imread("./standard_test_images/lena_gray_512.tif", 0)
# plt.hist(img.ravel(), 256, [0, 256])
# cv2.imshow("lena greyscale", img)
# plt.show()
# cv2.imshow("lena greyscale", img)
# cv2.waitKey()  # ważna funkcja!!!
# cv2.destroyAllWindows()  # zamknięcie wszystkich okien

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True, threaded=True)
#
# import os
# from flask import Flask, flash, request, redirect, url_for
# from werkzeug.utils import secure_filename
#
# UPLOAD_FOLDER = './uploads'
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'tif'])
#
# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#
#
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
#
# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # if user does not select file, browser also
#         # submit a empty part without filename
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('upload_file', filename=filename))
#     return '''
#     <!doctype html>
#     <title>Upload new File</title>
#     <h1>Upload new File</h1>
#     <form method=post enctype=multipart/form-data>
#       <p><input type=file name=file>
#          <input type=submit value=Upload>
#     </form>
#     '''

import os
from flask import Flask, render_template
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import cv2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/uploads'
imagePath = os.getcwd() + '/uploads'
app.config['IMAGES_PATH'] = os.getcwd() + '/assets'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
    else:
        file_url = None
    return render_template('index.html', form=form, file_url=file_url)


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/checker')
def checker_page():
    return render_template('checker.html')


def image_processing():
    img = cv2.imread(imagePath)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
