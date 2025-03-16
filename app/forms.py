from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField #added file field
from wtforms.validators import InputRequired
from flask_wtf.file import FileAllowed, FileRequired #required import


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

#new class for image files only
class UploadForm(FlaskForm):
    file = FileField('Image File', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png','.jpeg', '.gif'], 'Only images are allowed!')
    ])