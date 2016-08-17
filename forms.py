from flask_wtf import Form
from wtforms import (TextAreaField, StringField)
from flask_pagedown.fields import PageDownField
from wtforms.validators import (Length, Required, URL)


class PostForm(Form):
    headline = StringField('Ueberschrift',
                           [Required(), Length(min=0, max=140)])
    content = PageDownField('Text',
                            [Required(), Length(min=0, max=3000)])
    author = StringField('Autor',
                         [Required(), Length(min=0, max=50)])
    main_image = StringField('Anzeigebild') 

class RegisterAndLogin(Form):
    username = StringField('Benutzername', [Required()])
    password = StringField('Passwort', [Required()])
