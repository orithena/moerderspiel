# -*- coding: utf-8 -*-

import datetime
import smtplib
import mimetypes
import os
import os.path

from genshi.template import NewTextTemplate
from genshi.template import TemplateLoader
from genshi import Stream
from genshi.input import XML
from genshi.core import QName

from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def now(format='%d.%m.%Y %H:%M'):
	return datetime.datetime.now().strftime(format)

def future(format='%d.%m.%Y %H:%M', **kwargs):
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

def latexEsc(str):
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
	for c in str:
		if c in keys:
			out.append(translations[c])
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

def sendemail(templatedir, filename, subject, sender, receiver, game, player, pdfpath):
	try:
		outer = MIMEMultipart()
		outer['Subject'] = subject
		outer['From'] = sender
		outer['To'] = receiver
		outer.preamble = ''
		ctype, encoding = mimetypes.guess_type(pdfpath)
		if ctype is None or encoding is not None:
			ctype = 'application/octet-stream'
		maintype, subtype = ctype.split('/', 1)
		fp = open(pdfpath, 'rb')
		text = MIMEText( str(mailstream(templatedir, filename, game=game, player=player)), 'plain', 'utf-8')
		outer.attach(text)
		attach = MIMEBase(maintype, subtype)
		attach.set_payload(fp.read())
		fp.close()
		encoders.encode_base64(attach)
		attach.add_header('Content-Disposition', 'attachment', filename='auftrag.pdf')
		outer.attach(attach)
		s = smtplib.SMTP('localhost')
		s.sendmail(sender, [receiver], outer.as_string())
		s.quit()
	except:
		pass

html_escape_table = {
	'"': "&quot;",
	"'": "&apos;",
	}
			
def htmlescape(text):
	if text is not str:
		text = u8(text).__str__()
	return "".join(html_escape_table.get(c,c) for c in text)

