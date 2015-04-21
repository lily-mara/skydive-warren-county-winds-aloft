import os

import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.options import define, options

from aloft import winds_aloft

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html')


class WindsAloftHandler(tornado.web.RequestHandler):
	def get(self, airport_code):
		self.finish(winds_aloft(airport_code).dict())

handlers = [
	(r'/', IndexHandler),
	(r'/api/aloft/(\w+)', WindsAloftHandler),
]

settings = {
	'debug': True,
	'static_path': os.path.join(BASE_PATH, 'static'),
	'template_path': os.path.join(BASE_PATH, 'templates')
}

application = tornado.web.Application(handlers, **settings)

define(
	'port',
	help='The port that this instance of the server should listen on',
	default='8080',
	type=int,
)

if __name__ == '__main__':
	tornado.autoreload.start()

	application.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
