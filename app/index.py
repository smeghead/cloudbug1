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
    subject = db.StringProperty(required=True)
    status = db.StringProperty(required=True)
    categories = db.ListProperty(unicode)
    priority = db.StringProperty()
    detail = db.StringProperty(multiline=True, required=True)
    reproduction_procedure = db.StringProperty(multiline=True)
    comment = db.StringProperty(multiline=True)
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
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'ログアウト'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'ログイン'

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
        message = Message.get(ticket.messages[len(ticket.messages) - 1])

        path = os.path.join(os.path.dirname(__file__), 'view.html')
        self.response.out.write(template.render(path, {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'ticket': ticket,
            'message': message
        }))
    
    def post(self):
        message_posted = {
            'subject': self.request.get('Message.subject'),
            'status': self.request.get('Message.status'),
            'categories': self.request.get_all('Message.categories'),
            'priority': self.request.get('Message.priority'),
            'detail': self.request.get('Message.detail'),
            'reproduction_procedure': self.request.get('Message.reproduction_procedure'),
            'comment': self.request.get('Message.comment'),
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
            'subject': self.request.get('Message.subject'),
            'status': self.request.get('Message.status'),
            'categories': self.request.get_all('Message.categories'),
            'priority': self.request.get('Message.priority'),
            'detail': self.request.get('Message.detail'),
            'reproduction_procedure': self.request.get('Message.reproduction_procedure'),
            'comment': self.request.get('Message.comment'),
        }
        try:
            lastticket = Ticket.all().order('-id').fetch(1)
            if len(lastticket) == 0:
                next_id = 1
            else:
                next_id = lastticket[0].id + 1
            user = users.get_current_user()
            ticket = Ticket(id=next_id, key_name='ticket')
            if user:
                ticket.author = user
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
                'message': message_posted,
                'user': user,
                'url': url,
                'url_linktext': url_linktext,
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
