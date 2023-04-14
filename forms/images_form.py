from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import SubmitField, FileField

from test_app import app

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, 'Image only!'),
                                  FileRequired('File was empty!')])
    submit = SubmitField('Upload')
