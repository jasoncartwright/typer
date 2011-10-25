from google.appengine.ext import db
from google.appengine.ext.blobstore import blobstore
  
class CharacterSet(db.Model):
    name = db.StringProperty(required=True)
    description = db.TextProperty()
    button_text = db.StringProperty()
    image_size = db.IntegerProperty(required=True,default=250)

class Character(db.Model):
    character_set = db.ReferenceProperty(CharacterSet,required=True)
    character = db.StringProperty(required=True)
    image_blob = blobstore.BlobReferenceProperty()
    image_url = db.StringProperty(required=True)
    
