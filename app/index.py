#-*- coding: utf-8 -*-
import datetime
import sys
import os
import cgi
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

class Ticket(db.Model):
    id = db.IntegerProperty(long)
    date = db.DateTimeProperty(auto_now_add=True)
    messages = db.ListProperty(db.Key)
    author = db.UserProperty()

class Message(db.Model):
    author = db.UserProperty(required=True)
    field1 = db.StringProperty(required=True)
    field2 = db.StringProperty(required=True)
    field3 = db.StringProperty(required=True)
    field4 = db.ListProperty(unicode)
    field5 = db.StringProperty()
    field6 = db.StringProperty(multiline=True)
    field7 = db.StringProperty(multiline=True)
    field8 = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    author = db.UserProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        tickets_query = Ticket.all().order('-date')
        tickets_query
        tickets = []
        for ticket in tickets_query:
            if len(ticket.messages) > 0:
                message = Message.get(ticket.messages[len(ticket.messages) - 1])
            tickets.append({
                'ticket': ticket,
                'message': message
            })

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        params = {
            'tickets': tickets,
            'url': url,
            'url_linktext': url_linktext,
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, params))

class Guestbook(webapp.RequestHandler):
    def post(self):
        greeting = Greeting()

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/')

class Register(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        path = {
            'script_name': os.environ['SCRIPT_NAME']
        }
        params = {
            'path': path,
            'url': url,
            'url_linktext': url_linktext,
        }

        path = os.path.join(os.path.dirname(__file__), 'register.html')
        self.response.out.write(template.render(path, params))
    
    def post(self):
        message_posted = {
            'field1': self.request.get('Message.field1'),
            'field2': self.request.get('Message.field2'),
            'field3': self.request.get('Message.field3'),
            'field4': self.request.get_all('Message.field4'),
            'field5': self.request.get('Message.field5'),
            'field6': self.request.get('Message.field6'),
            'field7': self.request.get('Message.field7'),
            'field8': self.request.get('Message.field8'),
        }
        try:
            user = users.get_current_user()
            ticket = Ticket()
            if user:
                ticket.author = user
            ticket.put()
            message = Message(parent=ticket, **message_posted)
#             message.field1 = message_posted.field1
#             message.field2 = message_posted.field2
#             message.field3 = message_posted.field3
#             message.field4 = message_posted.field4
#             #message.field4 = map(lambda x: unicode(x, 'utf-8'), fields)
#             message.field5 = message_posted.field5
#             message.field6 = message_posted.field6
#             message.field7 = message_posted.field7
#             message.field8 = message_posted.field8
            if user:
                message.author = user
            message.put()
            ticket.messages.append(message.key())
            ticket.put()
            self.redirect('/')
        except Exception, mes:
            path = os.path.join(os.path.dirname(__file__), 'register.html')
            self.response.out.write(template.render(path, {
                'errormessage': mes,
                'message': message_posted
            }))


application = webapp.WSGIApplication(
    [('/', MainPage),
     ('/register', Register),
     ('/sign', Guestbook)],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

# vi: set ts=4 sw=4 sts=4 expandtab fenc=utf-8:
