# -*- coding: utf-8 -*-

import os
import sys
workdir = os.path.dirname(__file__)
modpath = os.path.join(workdir,"lib")
sys.path.insert(0,modpath)
from flask import Flask, request as req, redirect, url_for, make_response, copy_current_request_context
from flaskext.genshi import Genshi
#from mod_python import util
from genshi.template import MarkupTemplate
from genshi.template import TemplateLoader
from genshi import Stream
from genshi.input import XML
from genshi.core import QName
import time
import pickle
import codecs
import os.path
import shutil
import utils as utils
import filelock
import moerderklassen
import logging
import time
import locale
from moerderklassen import GameError
from moerdergraph import moerdergraph
from moerdergraphall import moerdergraphall
from pprint import pformat
from functools import wraps
locale.setlocale(locale.LC_ALL, ('de_DE', 'UTF8'))
os.environ['TZ'] = 'Europe/Berlin'
time.tzset()

app = Flask(__name__)
genshi = Genshi(app)

utils.url_for = url_for

class G:
	@staticmethod
	def u8(s):
                if isinstance(s, unicode):
                	return s
		try:
			return s.decode('utf8')
		except UnicodeDecodeError:
			try:
				return s.decode('latin1')
			except UnicodeDecodeError:
				return None
	
G.workdir = workdir
G.modpath = modpath
G.staticdir = os.path.join(workdir, 'static')
G.cssdir = os.path.join(G.staticdir, 'css')
G.imagedir = os.path.join(G.staticdir, 'images')
G.templatedir = os.path.join(workdir, 'templates')
G.savegamedir = os.path.join(workdir, 'savegames')
logging.basicConfig(filename=os.path.join(G.savegamedir, 'moerderspiel.log'), level=logging.DEBUG)

def route(part, altpart=None, *arg, **kwarg):
	def func_wrapper(f):
		x = altpart 		# hack to avoid "usage of variable before assignment" error...
		if x is None:
			x = part + '/' + '/'.join([ "<%s>" % n for n in f.func_code.co_varnames[0:f.func_code.co_argcount]])
		if x.find('<') >= 0:
			if kwarg.has_key('methods'):
				kwarg['methods'].append('POST')
			else:
				kwarg['methods'] = ['GET', 'POST']
		@app.route(x, *arg, **kwarg)
		@app.route(part, *arg, **kwarg)
		@wraps(f)
		def handler(*args, **kwargs):
			if len(kwargs) == 0:
				if len(req.args.items()) > 0:
					a = dict([ (k,v) for k,v in req.args.items() ])
				else:
					a = dict([ (k,v) for k,v in req.form.items() ])
			else:
				a = kwargs 
			return f(**a)
		return handler
	return func_wrapper

def _savegame(game, checkifexists=False):
	G.fname = os.path.join(G.savegamedir, '%s.pkl' % game.id)
	if checkifexists and os.path.isfile(G.fname):
		#raise AssertionError
		pass
	output = open('%s.tmp' % G.fname, 'wb')
	pickle.dump(game, output)
	output.close()
	os.rename('%s.tmp' % G.fname, G.fname)
	if hasattr(G, 'lockfile'):
		G.lockfile.release()
		del G.lockfile
	return game.id
	
def _loadgame(gameid, lock=True):
	G.fname = os.path.join(G.savegamedir, '%s.pkl' % gameid)
	G.lockfile = filelock.FileLock('%s.lock' )
	while G.lockfile.acquire():
		pass
	input = open(G.fname, 'rd')
	ret = pickle.load(input)
	input.close()
	if not lock:
		G.lockfile.release()
		del G.lockfile
	ret.workdir = G.workdir
	ret.templatedir = G.templatedir
	ret.savegamedir = G.savegamedir
	os.environ['TZ'] = ret.config.timezone
	time.tzset()
	return ret
	
def _response(content, content_type="text/html"):
	response = make_response(content)
	response.content_type = content_type
	return response

def _template(filename):
	loader = TemplateLoader([G.templatedir])
	tmpl = loader.load(filename)
	return tmpl

def _stream(filename, **args):
	return _template(filename).generate(utils = utils, **args)

def _mainstream(filename, **args):
	if not args.has_key('errormsg'):
		args['errormsg'] = ''
	return _stream('mainframe.html', baseurl = url_for('.index'), url_for = url_for, content = _stream(filename, **args), **args )

def _insert(outer, tagname, *inner):
	suppresstag = False
	for kind, data, pos in outer:
		if kind == 'START' and data[0].localname == tagname:
			suppresstag = True
		elif kind == 'END' and data.localname == tagname:
			suppresstag = False
			for i in inner:
				for k, d, p in i:
					yield k, d, p
		elif not suppresstag:
			yield kind, data, pos

def _ajaxstream(filename, selectors, **args):
	"""Creates a genshi.Stream object containing XML response data suitable for
	the JS AJAX functions in ajax.js. 
	
	It requires the mod_python request object, the filename of the proper 
	template, the XPath selector string (or list of strings) of all elements
	that need to be updated (currently, these elements need to have an 
	id attribute!), and any named variables the template may need.
	If one of the named variables is called "errormsg", <div id="errormessage">
	is automatically selected.
	
	Call example:
		stream = _ajaxstream("index.html", 
			'//*[@id="content"]', 
			errormsg="Fehlertext", 
			headline="Welcome")
		output = stream.render("xhtml")
	
	An output data example would be:
		<div xmlns="http://www.w3.org/1999/xhtml">
			<div id="errormessage">
				Fehlertext
			</div>
			<div id="content">
				<h2>Welcome</h2>
			</div>
		</div>
	"""
	main = list()
	s = list(_mainstream(filename, **args))
	try:
		if args.has_key('errormsg'):
			main.append(Stream(s).select("//*[@id='errormessage']"))
	except:
		pass
	if selectors is None:
		selectors = list()
	if isinstance(selectors, str):
		try:
			main.append(Stream(s).select(selectors))
		except Exception as e:
			logging.debug(e)
	elif isinstance(selectors, list):
		for sel in selectors:
			try:
				main.append(Stream(s).select(sel))
			except Exception as e:
				logging.debug(e)
	else:
		logging.debug("_ajaxstream(): selectors is not list nor str")
	frame = XML('<div xmlns="http://www.w3.org/1999/xhtml"><insert/></div>')
	return Stream(_insert(frame, u'insert', *main))

	
	
@app.route('/')
def index():
	return redirect(url_for('start'))

@app.route('/start')
def start():
	stream = _mainstream('index.html')
	return stream.render('xhtml')

@app.route('/newgameform')
def newgameform():
	stream = _mainstream('newgameform.html')
	return stream.render('xhtml')

@app.route('/<id>')
@route('/view', '/view/<id>')
def view(id, msg = ""):
	stream = None
	game = None
	try:
		game = _loadgame(id, False)
	except:
		stream = _mainstream('error.html', errormsg = "Sorry, Spiel-ID %s  existiert nicht." % id, returnurl="start")
	else:
		stream = _mainstream('view.html', game = game, errormsg = msg)
	return stream.render('xhtml')

@route('/wall', '/wall/<id>')
def wall(id, msg = "", ajax=0):
	stream = None
	games = []
	try:
		for gameid in id.split(':'):
			games.append(_loadgame(gameid, False))
	except:
		stream = _mainstream('error.html', errormsg = "Sorry, Spiel-ID %s  existiert nicht." % id, returnurl="start")
	else:
		if ajax == '1':
			selectors = [ "//*[@id='listplayers']" ]
			stream = _ajaxstream('wall.html', selectors, games = games, errormsg = None)
			return _response(stream.render("xhtml"), 'text/xml')
		else:
			stream = _mainstream('wall.html', games = games, errormsg = msg)
	
	return stream.render('xhtml')

@route('/error')
def error(msg = "", returnurl = "index"):
	#game = _loadgame(id, False)
	stream = _mainstream('error.html', errormsg = msg, returnurl = returnurl)
	return stream.render('xhtml')

@route('/gamegraph', '/gamegraph/<id>/<roundid>/<mastercode>')
def gamegraph(id, roundid, mastercode=''):
	game = None
	tries = 0
	while tries < 10:
		try:
			game = _loadgame(id, False)
			tries = 10
		except:
			time.sleep(0.01)
			tries += 1
	round = game.rounds[roundid]
	adminview = (mastercode == game.mastercode or game.status == 'OVER')
	fname = os.path.join(G.savegamedir, '%s_%s%s.svg' % (game.id, round.name, '-admin' if adminview else ''))
	tries = 0
	while tries < 10:
		try:
			moerdergraph(round, fname, adminview)
			tries = 10
		except:
			time.sleep(0.01)
			tries += 1
	req.content_type = 'image/svg+xml'
	ret = None
	tries = 0
	while tries < 10:
		img = file(fname, 'r')
		try:
			ret = img.read()
			tries = 10
		except:
			time.sleep(0.01)
			tries += 1
		finally:
			img.close()
	return ret
	
@route('/gamegraphall', '/gamegraphall/<id>/<roundid>/<mastercode>')
def gamegraphall(id, roundid='', mastercode=''):
	game = None
	tries = 0
	while tries < 10:
		try:
			game = _loadgame(id, False)
			tries = 10
		except:
			time.sleep(0.01)
			tries += 1
	adminview = (mastercode == game.mastercode or game.status == 'OVER')
	fname = os.path.join(G.savegamedir, '%s_%s%s%s.svg' % (game.id, roundid, 'full', '-admin' if adminview else ''))
	tries = 0
	while tries < 10:
		try:
			if len(roundid) < 1:
				moerdergraphall(game, fname, adminview)
			else:
				moerdergraphall(game, fname, adminview, rounds=game.rounds[roundid])
			tries = 10
		except:
			raise
			time.sleep(0.01)
			tries += 1
	ret = None
	tries = 0
	while tries < 10:
		img = None
		try:
			img = file(fname, 'r')
			ret = img.read()
			tries = 10
		except:
			time.sleep(0.01)
			tries += 1
		finally:
			if img is not None:
				img.close()
	return _response(ret, 'image/svg+xml')

@route('/addplayer')
def addplayer(gameid, spielername, zusatzinfo, email='', email2='', subgame='', ajax=0):
	err = ''
	if email != email2:
		stream = _mainstream('error.html', errormsg = "Die beiden Mailadressen sind nicht gleich!", returnurl = 'view/%s' % gameid)
		return stream.render('xhtml')
	game = _loadgame(gameid)
	try:
		if isinstance(game, moerderklassen.MultiGame):
			game.addPlayer(G.u8(spielername), G.u8(zusatzinfo), G.u8(email), G.u8(subgame) )
		else:
			game.addPlayer(G.u8(spielername), G.u8(zusatzinfo), G.u8(email) )
		gameid = _savegame(game)
	except GameError as e:
		err = e.__str__()
	else:
		err = "Neuer Mitspieler: %s" % G.u8(spielername)
	if ajax == '1':
		selectors = [ "//*[@id='listplayers']", "//*[@id='gameinfo']" ]
		stream = _ajaxstream('view.html', selectors, game = game, errormsg = err)
		return _response(stream.render("xhtml"), 'text/xml')
	else:
		return redirect(_url(req, 'view', gameid, err))

@route('/creategame')
def creategame(action, rundenname, kreiszahl, enddate, rundenid='', desc=None):
	game = moerderklassen.Game(
		G.u8(rundenname), 
		int(kreiszahl), 
		enddate, 
		_url(req, 'view',  rundenid), 
		rundenid,
		G.u8(desc)
	)
	game.url = _url(req, 'view', game.id)
	G.fname = os.path.join(G.savegamedir, '%s.pkl' % game.id)
	if not os.path.exists(G.fname):
		G.lockfile = filelock.FileLock(G.fname + '.lock')
		try:
			gameid = _savegame(game, True)
		except Exception as e:
			return error(req, e.__str__())
	stream = _mainstream('creategame.html', gameid = game.id, url = _url(req, 'view', id=game.id), mastercode = game.mastercode)
	return stream.render('xhtml')

@route('/startgame', '/startgame/<gameid>/<mastercode>')
def startgame(gameid, mastercode):
	game = _loadgame(gameid)
	try:
		game.start(mastercode)
	except GameError as e:
		return error(req, e.__str__(), _url(req, "view", gameid))
	gameid = _savegame(game)
	try:
		_pdfgen(game)
	except Exception as e:
		pass
	return redirect(_url(req, 'view', gameid))
	#stream = _mainstream('startgame.html', game = game, adminurl = _url(req, 'admin', game.id), viewurl = _url(req, 'view', id=game.id))
	#return stream.render('xhtml')

@route('/endgame', '/endgame/<gameid>/<mastercode>')
def endgame(gameid, mastercode):
	game=_loadgame(gameid)
	try:
		game.stop(mastercode)
	except GameError as e:
		return error(req, e.__str__(), _url(req, "view", gameid))
	gameid = _savegame(game)
	stream = _mainstream('view.html', game = game, errormsg = u'Spiel beendet')
	return stream.render('xhtml')

def _pdfgen(game):
	return game.pdfgen()

def _pdfblankgen(count, game):
	tmptexdir = "/tmp/moerder_" + game.id
	if not os.path.isdir(tmptexdir):
		os.mkdir(tmptexdir)
	shutil.copyfile(os.path.join(G.templatedir, "moerder.tex"), os.path.join(tmptexdir, "moerder.tex"))
	listfile = codecs.open(os.path.join(tmptexdir, "list.tex"), "w", "utf-8")
	for p in range(0, count):
		for roundid in sorted(game.rounds):
			round = game.rounds[roundid]
			roundname = round.name if len(game.rounds) > 1 else ''
			#listfile.write("\Auftrag{Gamename}{Gameid}{Victim}{Killer}{Signaturecode}{Spielende}{URL}\n")
			listfile.write(u"\\Auftrag{%s}{%s}{%s\\\\%s}{%s\\\\%s}{%s}{%s}{%s}{%s}\n" % 
				(
					utils.latexEsc(game.name), 
					utils.latexEsc(game.id), 
					'\underline{\hskip4.5cm}', 
					'\underline{\hskip4.5cm}', 
					'\underline{\hskip2.5cm}', 
					'\underline{\hskip2.5cm}', 
					'\underline{\hskip2cm}', 
					utils.latexEsc(game.enddate.strftime("%d.%m.%Y %H:%M")), 
					utils.latexEsc(_url(req, 'view',  game.id)), 
					utils.latexEsc(roundname)
				) 
			)
	listfile.close()
	cwd = os.getcwd()
	os.chdir(tmptexdir)
	os.system("xelatex moerder.tex")
	os.chdir(cwd)
	shutil.copyfile(tmptexdir + "/moerder.pdf", os.path.join(G.savegamedir, "%s.pdf" % game.id))

@route('/css', '/css/<css>')
def css(css):
	print _url(req, 'view',  rundenid)
	filepath = os.path.join(G.cssdir, "%s.css" % css )
	if filepath.find("..") < 0 and os.path.isfile(filepath):
		ret = ""
		cssfile = None
		try:
			cssfile = file(filepath, 'r')
			ret = cssfile.read()
		except:
			pass
		finally:
			if cssfile:
				cssfile.close()
		return _response(ret, "text/css")
	else:
		return _response('', "text/css")

@route('/images', '/images/<path:image>')
def images(image):
	filepath = os.path.join(G.imagedir, image )
	if filepath.find("..") < 0 and os.path.isfile(filepath):
		ret = ""
		imagefile = None
		mime='png'
		try:
			imagefile = file(filepath, 'r')
			ret = imagefile.read()
			mime = image.split('.')[-1]
		except:
			pass
		finally:
			if imagefile:
				imagefile.close()
		return _response(ret, "image/%s" % mime)
	else:
		return _response('', "text/html"), 404

@route('/pdfdownload', '/pdfdownload/<id>/<mastercode>/<publicid>')		
def pdfdownload(id, mastercode, publicid):
	game = _loadgame(id)
	filename = os.path.join(G.savegamedir, "%s_%s.pdf" % (game.id, publicid))
	if mastercode == game.mastercode:
		if not os.path.isfile(filename):
			return error(req, u"Da gibt es kein passendes PDF")
		else:
			pdf = file(filename, 'r')
			ret = pdf.read()
			pdf.close()
			return _response(ret, 'application/pdf')
	else:
		return error(req, u"Das war nicht der richtige Mastercode")

@route('/pdfget', '/pdfget/<id>/<mastercode>/<int:count>')
def pdfget(id, mastercode, count=0):
	game = _loadgame(id)
	filename = os.path.join(G.savegamedir, "%s.pdf" % game.id)
	if mastercode == game.mastercode:
		if not os.path.isfile(filename):
			if count == 0:
				filename = game.pdfgen()
			else:
				try:
					_pdfblankgen(req, int(count), game)
				except:
					return error(req, u"Das war keine Zahl...")
		pdf = file(filename, 'r')
		ret = pdf.read()
		pdf.close()
		if not count == 0:
			os.unlink(filename)
		return _response(ret, 'application/pdf')
	else:
		return error(req, u"Das war nicht der richtige Mastercode!")

@route('/htmlget', '/htmlget/<id>/<mastercode>')
def htmlget(id, mastercode):
	game = _loadgame(id)
	if mastercode == game.mastercode:
		#TODO req.content_type = 'text/xml;charset=utf-8'
		stream = _stream('auftrag.html', game = game)
		return stream.render('xhtml')
	else:
		return error(req, u"Das war nicht der richtige Mastercode!")

@route('/admin')
def admin(id=None, mastercode=None, action=None, round=None, killer=None, victim=None, datum=None, reason=None, ajax=0, spielername=None, zusatzinfo=None, email=''):
	stream = None
	if id is not None:
		err = ''
		selectors = [ "//*[@id='listplayers']", "//*[@id='gameinfo']" ]
		game = _loadgame(id)
		if mastercode == game.mastercode:
			if victim == 'ERROR':
				err = u'Du solltest schon ein Opfer aus der Liste auswählen!'
				selectors = "//*[@id='makeakill']"
			elif action == 'removeplayer':
				playername = game.findPlayerByPublicID(victim).name
				try:
					game.removePlayer(victim)
				except GameError as e:
					err = u'Fehler: %s' % e.__str__()
				else:
					err = u'%s wurde aus dem Spiel entfernt.' % playername
			elif action == 'addplayer':
				try:
					game.addPlayer(G.u8(spielername), G.u8(zusatzinfo), G.u8(email))
				except GameError as e:
					err = e.__str__()
				else:
					err = "Neuer Mitspieler: %s" % G.u8(spielername)
			elif action == 'killplayer':
				participant = game.rounds[round].getParticipant(victim)
				if len(killer) < 1:
					killer = None
				try:
					game.kill(killer, participant.id, datum, G.u8(reason))
				except GameError as e:
					err = u'Fehler: %s' % e.__str__()
				else:
					err = u'Eingetragen: %s wurde erlegt.' % participant.player.name
					selectors.append( "//*[@id='makeakill']" )
			elif action == 'kickplayer':
				playername = game.findPlayerByPublicID(victim).name
				try:
					game.kickPlayer(victim, mastercode)
				except GameError as e:
					err = u'Fehler: %s' % e.__str__()
				else:
					err = u'%s wurde aus dem Spiel entfernt.' % playername
			elif action == 'revertkill':
				try:
					game.revertkill(victim)
				except GameError as e:
					err = e.__str__()
				else:
					err = u'Mord an %s wurde zurückgenommen' % game.findParticipant(victim).player.name
			elif action == 'editkill':
				err = u'Not implemented yet. Muss momentan noch durch "undo" und neu eintragen durchgeführt werden.'
			else:
				err = u'No valid action'
			id = _savegame(game)
			if ajax == '1':
				logging.debug(selectors)
				stream = _ajaxstream('admin.html', selectors, game = game, errormsg = err)
			else:
				stream = _mainstream('admin.html', game = game, errormsg = err)
		else:
			err = u'Das war nicht der Game Master Code zu diesem Spiel!'
		if stream is None:
			if ajax == '1':
				stream = _ajaxstream('view.html', selectors, game = game, errormsg = err)
			else:
				stream = _mainstream('view.html', game = game, errormsg = err)
	else: #if id is None
		stream = _mainstream('index.html', errormsg = "")
	if ajax == '1':
		return _response(stream.render('xhtml'), 'text/xml')
	else:
		return stream.render('xhtml')

@route('/killplayer')
def killplayer(gameid, victimid, killerpublicid, datum, reason, ajax=0):
	errormsg = ''
	game = _loadgame(gameid)
	try:
		game.kill(killerpublicid, victimid, datum, G.u8(reason))
		errormsg = u'Spieler wurde erlegt'
	except GameError as e:
		errormsg = e.__str__()
	gameid = _savegame(game)
	selectors = "//*[@id='inner-content']"
	if ajax == '1':
		stream = _ajaxstream('view.html', selectors, game = game, errormsg = errormsg)
		return _response(stream.render('xhtml'), 'text/xml')
	else:
		stream = _mainstream('view.html', game = game, errormsg = errormsg)
		return stream.render('xhtml')

def _url(req, action, id=None, errormsg=""):
	if id is not None and action == 'view':
		# I can do this because .htaccess has this line: 
		# RewriteRule ^([a-z0-9]+)$ /moerderspiel/view?id=$1 [R=302]
		return "%s%s" % (req.host_url, id)
	else:
		url = "%s%s" % (url_for('.index'), action)
		if id != None:
			url += '?id=' + id
		if len(errormsg) > 1 and id == None:
			url +=  '?msg=' + errormsg
		elif len(errormsg) > 1:
			url +=  '&msg=' + errormsg
		return url

@route('/redir', '/redir/<gameid>')
def redir(gameid):
	redirect(_url(req, 'view', gameid))

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
