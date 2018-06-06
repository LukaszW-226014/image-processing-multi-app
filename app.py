import os
import glob
import random
from flask import Flask, render_template
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/uploads'
imagePath = os.getcwd() + '/uploads/'
histogramPath = os.getcwd() + '/static/histograms/'
app.config['IMAGES_PATH'] = os.getcwd() + '/assets'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload')

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/checker', methods=['GET', 'POST'])
def checker_page():
    cancer = 0
    random_value = ""
    cleaning()
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        random_value, cancer = image_processing(filename)
    else:
        file_url = None
    return render_template('checker.html', form=form, file_url=file_url, cancer=cancer, random_value=random_value)


def image_processing(file):
    # Step 1 read convert to grayscale image
    img = cv2.imread(imagePath + str(file), cv2.IMREAD_GRAYSCALE)

    # Generate random value to refresh showing on page image
    random_value = str(random.randrange(10, 100, 1))

    # TODO counting real probability
    cancer = random.randrange(10.0, 100.0, 1)

    # Step 2: Gaussian filter
    denoised = cv2.GaussianBlur(img, (5, 5), 0)

    #Step 3: Thresholding
    ret, thresh2 = cv2.threshold(denoised, 127, 255, cv2.THRESH_BINARY_INV)

    denoisedTresh = cv2.GaussianBlur(thresh2, (5, 5), 0)

    flood_fill = denoisedTresh.copy()

    h, w = denoisedTresh.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # Step 5: Floodfill from point (0, 0)
    cv2.floodFill(flood_fill, mask, (0, 0), 255)

    # Invert floodfilled image
    flood_fill_inv = cv2.bitwise_not(flood_fill)

    # Combine the two images to get the foreground.
    filled_out = denoisedTresh | flood_fill_inv

    # Step 6: Detect edges - Laplacian
    filter2 = cv2.Laplacian(filled_out, cv2.CV_64F)

    #cv2.imwrite(histogramPath + "floodFill" + str(random_value) + ".jpg", flood_fill, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    cv2.imwrite(histogramPath + "0Started" + str(random_value) + ".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "1denoised" + str(random_value) + ".jpg", denoised, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "2Tresh" + str(random_value) + ".jpg", thresh2, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "3denoisedThresh" + str(random_value) + ".jpg", denoisedTresh, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "4Mask" + str(random_value) + ".jpg", mask, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "5invOut" + str(random_value) + ".jpg", flood_fill_inv, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "6Out" + str(random_value) + ".jpg", filled_out, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "7detectedEdges" + str(random_value) + ".jpg", filter2, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    return random_value, cancer


def cleaning():
    histograms = glob.glob(histogramPath + '*')
    for h in histograms:
        os.remove(h)

    uploads = glob.glob(imagePath + '*')
    for u in uploads:
        os.remove(u)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
