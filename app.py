import os

import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.options import define, options, parse_command_line
from metar.Metar import Metar
import requests

from aloft import winds_aloft

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
BASE_ADDR = 'http://weather.noaa.gov/pub/data/observations/metar/stations/{}.TXT'


def add_ground_wind(airport_code, aloft_wind):
	"""
	Add the wind information at the ground for the given station code.
	"""
	raw = requests.get(BASE_ADDR.format(airport_code.upper()))
	if raw.status_code == 404:
		raw = requests.get(BASE_ADDR.format('K' + airport_code.upper()))

	if raw.status_code == 404:
		raise ValueError('The given station code is invalid.')

	ground_wind = {'altitude': 0, 'direction': 0, 'speed': 0}

	for line in raw.text.split('\n'):
		if airport_code.upper() in line:
			line = line.strip()
			observation = Metar(line)
			ground_wind['direction'] = observation.wind_dir.value()
			ground_wind['speed'] = observation.wind_speed.value(units='KT')

	return [ground_wind] + aloft_wind


class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html')


class WindsAloftHandler(tornado.web.RequestHandler):
	def get(self, airport_code):
		aloft_info = winds_aloft(airport_code).dict()
		aloft_info['winds'] = add_ground_wind(airport_code, aloft_info['winds'])

		self.finish(aloft_info)

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
	parse_command_line()
	tornado.autoreload.start()

	application.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
