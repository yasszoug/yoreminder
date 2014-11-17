import webapp2, urllib, jinja2, os
from google.appengine.api import taskqueue
from google.appengine.api import urlfetch

from apikeys import *  # contains api key for YOIN15MIN,YOIN30MIN,YOINANHOUR 

SINGLE_YO_API = "http://api.justyo.co/yo/"

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class ScheduleHandler(webapp2.RequestHandler):
    
    def get(self):
        username = self.request.get("username")
        link = self.request.get("link")
        path = self.request.path
        if path in APIDATA and username:
            apitoken,delay = APIDATA[path]
            taskqueue.add( url="/yo", 
                           params={"username":username.upper(), 
                                   "api_token":apitoken, 
                                   "link":link}, 
                           method="POST", 
                           countdown=delay)
         
class YoHandler(webapp2.RequestHandler):
    
    def post(self):
        params = {field:self.request.get(field) for field in self.request.arguments()}
        if "username" in params and "api_token" in params:
            form_data = urllib.urlencode(params)
            urlfetch.fetch(url=SINGLE_YO_API,
                                    payload=form_data,
                                    method=urlfetch.POST,
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})

class HomePageHandler(webapp2.RequestHandler):
    
    def get(self):
        template = jinja_environment.get_template("index.html")
        self.response.write(template.render({}))

app = webapp2.WSGIApplication([ (callback,ScheduleHandler ) for callback in APIDATA ] +
                              [ ("/", HomePageHandler), ("/yo", YoHandler) ], debug=True)

