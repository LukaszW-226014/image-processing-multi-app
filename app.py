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


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/checker', methods=['GET', 'POST'])
def checker_page():
    cancer = 0
    cleaning()
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        cancer = image_processing(filename)
    else:
        file_url = None
    return render_template('checker.html', form=form, file_url=file_url, cancer=cancer)


def image_processing(file):
    img = cv2.imread(imagePath + str(file), cv2.IMREAD_GRAYSCALE)
    rows, cols = img.shape

    fig = plt.hist(img.ravel(), 256, [0, 256])
    # plt.show()
    plt.savefig(histogramPath + "histogram1")
    cancer = random.randrange(10.0, 100.0, 1)
    non_cancer = 100.0 - cancer
    cv2.imwrite(histogramPath + "before.jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    denoised = cv2.GaussianBlur(img, (5, 5), 0)
    filter_withoutDenoised = cv2.Laplacian(img, cv2.CV_64F)
    filter = cv2.Laplacian(denoised, cv2.CV_64F)
    filter_canny = cv2.Canny(denoised, 100, 200)
    sobelx64 = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5)
    sobely64 = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5)

    #laplacian = np.uint8(np.absolute(filter))
    #sobelx = np.uint8(np.absolute(sobelx64))
    #sobely = np.uint8(np.absolute(sobely64))

    ret, thresh2 = cv2.threshold(denoised, 127, 255, cv2.THRESH_BINARY_INV)

    denoisedTresh = cv2.GaussianBlur(thresh2, (5, 5), 0)

    img_tmp, contours, hierarchy = cv2.findContours(thresh2, 1, 2)

    # cnt = contours[0]
    # #M = cv2.moments(cnt)
    # print(cnt)
    # print(thresh2)
    #
    # (x, y), radius = cv2.minEnclosingCircle(cnt)
    # center = (int(x), int(y))
    # radius = int(radius)
    # print("Center: " + str(center) + " Radius: " + str(radius))
    # cv2.circle(thresh2, center, radius, (0, 255, 0), 20)

    filter_withoutDenoised2 = cv2.Laplacian(thresh2, cv2.CV_64F)
    filter2 = cv2.Laplacian(denoisedTresh, cv2.CV_64F)
    filter_canny2 = cv2.Canny(denoisedTresh, 100, 200)
    sobelx642 = cv2.Sobel(thresh2, cv2.CV_64F, 1, 0, ksize=5)
    sobely642 = cv2.Sobel(thresh2, cv2.CV_64F, 0, 1, ksize=5)


    flood_fill = thresh2.copy()
    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    h, w = thresh2.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # Floodfill from point (0, 0)
    cv2.floodFill(flood_fill, mask, (0, 0), 255);

    # Invert floodfilled image
    flood_fill_inv = cv2.bitwise_not(flood_fill)

    # Combine the two images to get the foreground.
    filled_out = thresh2 | flood_fill_inv



    cv2.imwrite(histogramPath + "floodFill.jpg", flood_fill, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "floodFill_invert.jpg", flood_fill_inv, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "Out.jpg", filled_out, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    cv2.imwrite(histogramPath + "Started.jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "denoised.jpg", denoised, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "denoisedThresh.jpg", denoisedTresh, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "detectedEdges(withoutDenoised).jpg", filter_withoutDenoised, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "detectedEdges.jpg", filter, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "detectedEdges(Canny).jpg", filter_canny, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "sobelX.jpg", sobelx64, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "sobelY.jpg", sobely64, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "Tresh.jpg", thresh2, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    cv2.imwrite(histogramPath + "detectedEdges(withoutDenoised)2.jpg", filter_withoutDenoised2, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "detectedEdges2.jpg", filter2, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "detectedEdges(Canny)2.jpg", filter_canny2, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "sobelX2.jpg", sobelx642, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    cv2.imwrite(histogramPath + "sobelY2.jpg", sobely642, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    #cv2.imwrite(histogramPath + "Circle.jpg", img_circle, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    #cv2.imwrite(histogramPath + "CircleTMP.jpg", contours, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    #cv2.imshow('Orginal', img)
    #cv2.imshow('Laplacian', filter)

    #cv2.waitKey()
    #cv2.destroyAllWindows()

    return cancer


def cleaning():
    histograms = glob.glob(histogramPath + '*')
    for h in histograms:
        os.remove(h)

    uploads = glob.glob(imagePath + '*')
    for u in uploads:
        os.remove(u)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
