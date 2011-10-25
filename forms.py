from google.appengine.ext.db import djangoforms
from models import CharacterSet

class CharacterSetForm(djangoforms.ModelForm):
    class Meta:
        model = CharacterSet