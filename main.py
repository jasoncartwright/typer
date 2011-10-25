import os
from random import choice

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.images import get_serving_url

from models import CharacterSet, Character

import logging


def get_template_path(filename):
    return os.path.join(os.path.dirname(__file__), "templates", '%s.html' % filename)


def get_character_sets():
    character_sets_query = CharacterSet.all()
    return character_sets_query.fetch(1000)


def get_characters(char_set):
    character_sets_query = Character.all()
    character_sets_query.filter("character_set = ", char_set)
    return character_sets_query.fetch(1000)


class IndexHandler(webapp.RequestHandler):
    
    def get(self):
        
        template_vars = {
            "character_sets":get_character_sets(),
        }
        
        self.response.out.write(template.render(get_template_path("index"), template_vars))


class CharSetHandler(webapp.RequestHandler):

    def get(self,charset_key):
        
        text = self.request.get("text")
        charset = CharacterSet.get(charset_key)
        images = []
        
        if text:
            for character in text:
                
                logging.info(character)
            
                the_character = character.upper()

                character_images_query = Character.all()
                character_images_query.filter("character = ", the_character)
                characters = character_images_query.fetch(1000)
        
                if characters:
                    images.append(choice(characters).image_url)
                
        
        template_vars = {
            "charset":charset,
            "text":text,
            "images":images,
        }

        self.response.out.write(template.render(get_template_path("charset"), template_vars))



class AdminIndexHandler(webapp.RequestHandler):

    def get(self):
        
        template_vars = {
            "character_sets":get_character_sets(),
        }
        
        self.response.out.write(template.render(get_template_path("admin"), template_vars))

    def post(self):
        
        new_charset = CharacterSet(
            name = self.request.get("name")
        )
        new_charset.save()
        
        self.redirect("/admin/%s/" % new_charset.key())


class AdminCharSetHandler(webapp.RequestHandler):

    def get(self,charset_key):
        
        charset = CharacterSet.get(charset_key)
        characters = get_characters(charset)

        template_vars = {
            "charset":charset,
            "characters":characters,
        }

        self.response.out.write(template.render(get_template_path("admin_charset"), template_vars))


class AdminCharUploadHandler(webapp.RequestHandler):
    
    def get(self,charset_key):
        
        charset = CharacterSet.get(charset_key)
        characters = CharacterSet.get(charset_key)
        
        template_vars = {
            "characters":characters,
            "upload_url":blobstore.create_upload_url('/admin/%s/upload/do/' % charset_key)
        }

        self.response.out.write(template.render(get_template_path("admin_upload"), template_vars))
        

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    
    def post(self,charset_key):
        
        character_set = CharacterSet.get(charset_key)
        
        logging.info(character_set)
        
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        
        new_character = Character(
            character = self.request.get("character").upper(),
            character_set = character_set,
            image_blob = blob_info.key(),
            image_url = get_serving_url(blob_info.key()),
        )
        new_character.save()
        
        self.redirect("/admin/%s/" % charset_key)
        

def main():
    application = webapp.WSGIApplication(
        [
            ('/', IndexHandler),
            ('/admin/', AdminIndexHandler),
            ('/admin/([^/]+)/', AdminCharSetHandler),
            ('/admin/([^/]+)/upload/', AdminCharUploadHandler),
            ('/admin/([^/]+)/upload/do/', UploadHandler),
            ('/([^/]+)/', CharSetHandler),
        ],
    debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
