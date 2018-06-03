import os
import glob
import random
from flask import Flask, render_template
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
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
    img = cv2.imread(imagePath + str(file))
    fig = plt.hist(img.ravel(), 256, [0, 256])
    # plt.show()
    plt.savefig(histogramPath + "histogram1")
    cancer = random.randrange(10.0, 100.0, 1)
    non_cancer = 100.0 - cancer
    return cancer


def cleaning():
    files = glob.glob(histogramPath + '*')
    for f in files:
        os.remove(f)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
