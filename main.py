#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import tornado
import tornado.web
import os
from pymongo import MongoClient
from commandprocessor import CommandProcessor, generate_name
from objects.robot import Robot

ws = '[NL]'


class App():
    class BaseHandler(tornado.web.RequestHandler):
        def get_current_user(self):
            login = self.get_secure_cookie("login", None).decode('utf-8')
            password = self.get_secure_cookie("password", None).decode('utf-8')
            if login and password \
                and App.db().users.find({
                    'login': login,
                    'password': password}).count() == 1:
                return login
            else:
                return None

    class MainHandler(BaseHandler):
        @tornado.web.authenticated
        def get(self):
            self.render("index.view.html", title='Base')

    class LoginHandler(BaseHandler):
        def get(self):
            self.render("login.view.html", title='Login')

        def post(self):
            login = self.get_argument("login")
            password = self.get_argument("password")
            if App.db().users.find({"login": login}).count() == 0:
                App.db().users.insert({'login': login, 'password': password})
                self.set_secure_cookie("login", login)
                self.set_secure_cookie("password", password)
                self.redirect("/")
            elif App.db().users.find({'login': login,
                                      'password': password}).count() == 1:
                self.set_secure_cookie("login", login)
                self.set_secure_cookie("password", password)
                self.redirect("/")
            else:
                self.redirect("/login")

    class Terminalhandler(BaseHandler):
        @tornado.web.authenticated
        def get(self):
            self.content_type = 'application/json'
            robot = Robot(App.db().robots.find_one(
                {'owner': self.get_current_user()}
            ))
            App.db().robots.update({'name': robot.name, 'owner': robot.owner},
                                   {'$set': {'messages': []}})
            self.write({'messages': robot.messages})

        @tornado.web.authenticated
        def post(self):
            data = tornado.escape.json_decode(self.request.body)
            answers = App.cp().process_command(data['text'],
                                               self.get_current_user())
            self.content_type = 'application/json'
            self.write({'userdata': data['text'], 'data': answers})

    def __init__(self):
        routes = [
            (r"/", self.MainHandler),
            (r"/login", self.LoginHandler),
            (r"/handler", self.Terminalhandler),
            (r'/css/^(.*)', tornado.web.StaticFileHandler,
                {'path': '/css'},),
            (r'/templates/^(.*)', tornado.web.StaticFileHandler,
                {'path': '/templates'},),
            (r'/js/^(.*)', tornado.web.StaticFileHandler,
                {'path': '/js'},),
        ]

        self.application = tornado.web.Application(
            routes,
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            cookie_secret="4qwetd646343dsgxdfhsjm434",
            login_url="/login"
        )
        #Database settings
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['game_database']
        if not self.db.users:
            self.db.users.remove()
            self.db.users.insert({"login": "admin", "password": "password"})
        self.db.robots.remove()
        for user in self.db.users.find():
            if not self.db.robots.find_one({'owner': user['login']}):
                self.db.robots.insert({
                    "name": generate_name(),
                    "inventory": [],
                    "x": 0,
                    "y": 0,
                    "owner": user['login'],
                    "actions": [],
                    "instructions": {'wander': '''go random
go random
go random
go random
go 2 2
go 4 4
jmp 0'''},
                    "messages": [],
                    "instructions_stage": 0,
                })
        self.cp = CommandProcessor(db=self.db)

    app = None

    @staticmethod
    def db():
        return App.instance().db

    @staticmethod
    def cp():
        return App.instance().cp

    @staticmethod
    def instance():
        if App.app is None:
            App.app = App()
        return App.app

if __name__ == "__main__":
    app = App()
    app.application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
