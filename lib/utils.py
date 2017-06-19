# -*- coding: utf-8 -*-

from __future__ import print_function
import sys

import datetime
import smtplib
import mimetypes
import os
import os.path
import math
import colorsys
import random

from genshi.template import NewTextTemplate
from genshi.template import TemplateLoader
from genshi import Stream
from genshi.input import XML
from genshi.core import QName

import qrcode
import cStringIO
import base64

from email import encoders
import email.utils
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def errprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

def now(format='%d.%m.%Y %H:%M'):
	return datetime.datetime.now().strftime(format)
	
def dateformat(dt, format='%a %d.%m. %H:%M'):
	try:
		return dt.strftime(format)
	except:
		return dt

def future_date(format='%d.%m.%Y %H:%M', **kwargs):
	return (datetime.datetime.now() + datetime.timedelta(**kwargs)).strftime(format)

def u8(s):
	try:
		return s.decode('utf8')
	except UnicodeDecodeError:
		try:
			return s.decode('latin1')
		except UnicodeDecodeError:
			return None
	except UnicodeEncodeError:
		return None


class Bunch(object):
	def __init__(self, **kwds):
		self.__dict__.update(kwds)
	def __eq__(self, other):
		return self.__dict__ == other.__dict__
	def put(self, **kwds):
		self.__dict__.update(kwds)
tmp = Bunch()

def latexEsc(s):
	translations = dict((
		(u'\\', u'\\textbackslash{}'),
		(u'{', u'\\{'),
		(u'}', u'\\}'),
		(u'$', u'\\$'),
		(u'&', u'\\&'),
		(u'#', u'\\#'),
		(u'^', u'\\textasciicircum{}'),
		(u'_', u'\\_'),
		(u'~', u'\\textasciitilde{}'),
		(u'%', u'\\%'),
		(u'<', u'\\textless{}'),
		(u'>', u'\\textgreater{}'),
	))
	keys = translations.keys()
	out = list()
	for c in s:
		if c in keys:
			out.append(translations[c])
		else:
			out.append(c)
	if len(out) < 1:
		out.append('~')
	return ''.join(out)
	
def dotescape(s):
	out = list()
	for c in s:
		if c in ['"', "'", '$', '%', '/', '*']:
			out.append("\\%s" % c)
		else:
			out.append(c)
	if len(out) < 1:
		out.append('~')
	return ''.join(out)

def texttemplate(templatedir, filename):
	loader = TemplateLoader([templatedir])
	tmpl = loader.load(filename, cls=NewTextTemplate)
	return tmpl

def mailstream(templatedir, filename, **args):
	return texttemplate(templatedir, filename).generate(**args)

def sendemail(templatedir, templatefile, subject, sender, receiver, game, player=None, pdfpath=None):
	try:
		outer = MIMEMultipart()
		outer['Subject'] = subject
		outer['From'] = sender
		outer['To'] = receiver
		outer['Date'] = email.utils.formatdate()
		outer['Message-Id'] = email.utils.make_msgid('hades')
		outer.preamble = ''
		text = MIMEText( str(mailstream(templatedir, templatefile, game=game, player=player)), 'plain', 'utf-8')
		outer.attach(text)
		
		if pdfpath is not None:
			ctype, encoding = mimetypes.guess_type(pdfpath)
			if ctype is None or encoding is not None:
				ctype = 'application/octet-stream'
			maintype, subtype = ctype.split('/', 1)
			fp = open(pdfpath, 'rb')
			attach = MIMEBase(maintype, subtype)
			attach.set_payload(fp.read())
			fp.close()
			encoders.encode_base64(attach)
			attach.add_header('Content-Disposition', 'attachment', filename='auftrag.pdf')
			outer.attach(attach)
		
		s = smtplib.SMTP('localhost')
		s.sendmail(sender, [receiver], outer.as_string())
		s.quit()
	except Exception as e:
		errprint("ERROR: Cannot send mail to receiver %s" % receiver)
		errprint(e)
		pass

def colorgen(starthue, format='#RGBA'):
	PHI = 1.0 / ((1.0 + math.sqrt(5)) / 2.0)
	s = 1.0
	v = 1.0
	c = 0
	while(True):
		r,g,b = colorsys.hsv_to_rgb(starthue, s, v)
		starthue = (starthue + PHI) % 1.0
		c += 1
		if c % 3 == 0:
			v = (v + PHI) % 1.0
		if format == '#RGBA':
			yield '#%02x%02x%02xA0' % ( r*255, g*255, b*255 )
		elif format == '#RGB':
			yield '#%02x%02x%02x' % ( r*255, g*255, b*255 )
		elif format == 'rgba()':
			yield 'rgba(%d, %d, %d, 0.627)' % ( r*255, g*255, b*255 )
		
html_escape_table = {
	'"': "&quot;",
	"'": "&apos;",
	}
			
def htmlescape(text):
	if text is not str:
		text = u8(text).__str__()
	return "".join(html_escape_table.get(c,c) for c in text)

quote_escape_table = {
	'"': '\\"',
	"'": "\\'",
	}
			
def escape_quotes(text):
	if text is not str:
		text = u8(text).__str__()
	return "".join(quote_escape_table.get(c,c) for c in text)


def qrdata(text, **kwargs):
	qr = qrcode.QRCode(**kwargs)
	qr.add_data(text)
	qr.make() # Generate the QRCode itself
	
	# im contains a PIL.Image.Image object
	im = qr.make_image()
	
	jpeg_image_buffer = cStringIO.StringIO()
	im.save(jpeg_image_buffer)
	return base64.b64encode(jpeg_image_buffer.getvalue())

namelist = [
 'Gavin Gasser',
 'Natashia Norton',
 'Natalia Nam',
 'Arnetta Abboud',
 'Lael Luong',
 'Rachell Ralston',
 'Steffanie Steedley',
 'Napoleon Neumeister',
 'Sarina Schumann',
 'Tamesha Tafoya',
 'Rudy Reiman',
 'Jackeline Jarrells',
 'Sina Shofner',
 'Delma Demaio',
 'Chun Carini',
 'Layne Lipsky',
 'Marlon Mccardle',
 'Hyun Hansford',
 'Bobette Broadwater',
 'Richard Rikard',
 'Lera Lamberton',
 'Tresa Truett',
 'Soila Skelly',
 'Irena Ishibashi',
 'Jone Jasso',
 'Janey Judah',
 'Ricki Repka',
 'Lawanna Lorenzo',
 'Barrie Boyd',
 'Connie Crone',
 'Leanora Lamy',
 'Cliff Caldwell',
 'Rubye Redeker',
 'Micaela Manfredi',
 'Pamala Popek',
 'Vannessa Vandeventer',
 'Abdul Aker',
 'Annemarie Andrea',
 'Taylor Tank',
 'Sunshine Steller',
 'Maryln Master',
 'Amy Almon',
 'Tonia Taormina',
 'Cathi Caplan',
 'Scarlett Sandberg',
 'Aura Ashbrook',
 'Darlena Dorfman',
 'Ivory Ikard',
 'Leilani Landreth',
 'Myrl Mchugh']

infolist = [
 'Hyderabad',
 'Durban',
 'Hamburg',
 'Bonn',
 'Berlin',
 'Luxemburg',
 'Shenzhen',
 'Waldkirchen',
 'Mir doch egal',
 'Johannesburg',
 'Amsterdam',
 'Venedig'
]

def random_playerdata(num=10):
	return [ (u8(name), u8(random.sample(infolist, 1)[0])) for name in random.sample(namelist, num) ]