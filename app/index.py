#-*- coding: utf-8 -*-
import datetime
import sys
import os
import re
import cgi
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

class Ticket(db.Model):
    id = db.IntegerProperty(long, required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    messages = db.ListProperty(db.Key)
    author = db.UserProperty()

class Message(db.Model):
    field1 = db.StringProperty(required=True)
    field3 = db.StringProperty(required=True)
    field4 = db.ListProperty(unicode)
    field5 = db.StringProperty()
    field6 = db.StringProperty(multiline=True, required=True)
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
            url_linktext = 'ログアウト'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'ログイン'

        params = {
            'tickets': tickets,
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, params))

class View(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        params = {
            'user': user
        }
        regexp = re.compile('.*view/(\d+)')
        matches = regexp.match(self.request.uri)
        if not matches:
            raise Exception('no matche.')
        id = matches.group(1)
        if not id:
            raise Exception
        q = Ticket.all().filter('id =', int(id))
        tickets = q.fetch(1)
        if len(tickets) == 0:
            raise Exception('no tickets.')
        ticket = tickets[0]

#         print('content-type:text/plain\n\n')
#         print(self.request.uri)
#         raise Exception

        path = os.path.join(os.path.dirname(__file__), 'view.html')
        self.response.out.write(template.render(path, {
            'ticket': ticket
        }))
    
    def post(self):
        message_posted = {
            'field1': self.request.get('Message.field1'),
            'field3': self.request.get('Message.field3'),
            'field4': self.request.get_all('Message.field4'),
            'field5': self.request.get('Message.field5'),
            'field6': self.request.get('Message.field6'),
            'field7': self.request.get('Message.field7'),
            'field8': self.request.get('Message.field8'),
        }
        try:
            user = users.get_current_user()
#             ticket = Ticket(id=max_id+1)
#             if user:
#                 ticket.author = user
#             ticket.put()
#             message = Message(parent=ticket, **message_posted)
#             if user:
#                 message.author = user
#             message.put()
#             ticket.messages.append(message.key())
#             ticket.put()
#             self.redirect('/')
        except Exception, mes:
            path = os.path.join(os.path.dirname(__file__), 'view.html')
            self.response.out.write(template.render(path, {
                'errormessage': mes,
                'message': message_posted
            }))


class Register(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        params = {
            'user': user
        }

        path = os.path.join(os.path.dirname(__file__), 'register.html')
        self.response.out.write(template.render(path, params))
    
    def post(self):
        message_posted = {
            'field1': self.request.get('Message.field1'),
            'field3': self.request.get('Message.field3'),
            'field4': self.request.get_all('Message.field4'),
            'field5': self.request.get('Message.field5'),
            'field6': self.request.get('Message.field6'),
            'field7': self.request.get('Message.field7'),
            'field8': self.request.get('Message.field8'),
        }
        try:
            lastticket = Ticket.all().order('-id').fetch(1)
            if len(lastticket) == 0:
                next_id = 1
            else:
                next_id = lastticket[0].id + 1
            user = users.get_current_user()
            ticket = Ticket(id=next_id)
            if user:
                ticket.author = user
            ticket.put()
            message = Message(parent=ticket, **message_posted)
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
     ('/view/.*', View)],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

# vi: set ts=4 sw=4 sts=4 expandtab fenc=utf-8:
