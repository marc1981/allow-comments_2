import cgi
import urllib
import os

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	autoescape=True)


class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainPage(Handler):
	def get(self):
		self.render("base_form.html")

class Stage1(Handler):
	def get(self):
		self.render('stage_1.html')

class Stage2(Handler):
	def get(self):
		self.render('stage_2.html')

class Stage3(Handler):
	def get(self):
		self.render('stage_3.html')


DEFAULT_PAGE_NAME = 'color_selection'

def page_key(page_name=DEFAULT_PAGE_NAME):
    return ndb.Key('ColorChoice', page_name)


class Greeting(ndb.Model):
    author = ndb.StringProperty()
    color = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class Stage4(Handler):
    def get(self):
        page_name = self.request.get('page_name',
                                          DEFAULT_PAGE_NAME)
        greetings_query = Greeting.query(
            ancestor=page_key(page_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        template_values = {    
            'greetings': greetings,
            'page_name': urllib.quote_plus(page_name),
        }

        template = jinja_env.get_template('stage_4.html')
        self.response.write(template.render(template_values))


class Formpage(webapp2.RequestHandler):
    def post(self):
        page_name = self.request.get('page_name',
                                          DEFAULT_PAGE_NAME)
        greeting = Greeting(parent=page_key(page_name))  
        greeting.author = self.request.get('author')
        greeting.color = self.request.get('color')
        greeting.put()
        query_params = {'page_name': page_name}
        
        if greeting.color != '':
        	self.redirect('/stage_4?' + urllib.urlencode(query_params) + '#begin_form')
        else:
        	self.redirect('/stage_4?#form_start')

class Stage5(Handler):
	def get(self):
		self.render('stage_5.html')

app = webapp2.WSGIApplication([('/', MainPage),
								('/stage_1', Stage1),
								('/stage_2', Stage2),
								('/stage_3', Stage3),
								('/stage_4', Stage4),
								('/select', Formpage),
								('/stage_5', Stage5),
								],
								debug=True)