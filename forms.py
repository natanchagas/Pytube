from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired

class GetVideoForm(FlaskForm):
    video = StringField('URL:', validators=[DataRequired()])
    submit = SubmitField('Convert')