# -*- coding: utf-8 -*-

import os
import sys
workdir = os.path.dirname(__file__)
modpath = os.path.join(workdir,"lib")
sys.path.insert(0,modpath)
from mod_python import util
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
locale.setlocale(locale.LC_ALL, ('de_DE', 'UTF8'))
os.environ['TZ'] = 'Europe/Berlin'
time.tzset()

class G:
	@staticmethod
	def u8(s):
		try:
			return s.decode('utf8')
		except UnicodeDecodeError:
			try:
				return s.decode('latin1')
			except UnicodeDecodeError:
				return None
	
G.workdir = workdir
G.modpath = modpath
G.cssdir = os.path.join(workdir, 'css')
G.templatedir = os.path.join(workdir, 'templates')
G.savegamedir = os.path.join(workdir, 'savegames')
logging.basicConfig(filename=os.path.join(G.savegamedir, 'moerderspiel.log'), level=logging.DEBUG)

#mod_python convention: functions starting with an underscore are _not_ published on the webserver
def _savegame(game, checkifexists=False):
	G.fname = os.path.join(G.savegamedir, '%s.pkl' % game.id)
	if checkifexists and os.path.isfile(G.fname):
		#raise AssertionError
		pass
	output = open('%s.tmp' % G.fname, 'wb')
	pickle.dump(game, output)
	output.close()
	os.rename('%s.tmp' % G.fname, G.fname)
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
	
def _template(filename):
	loader = TemplateLoader([G.templatedir])
	tmpl = loader.load(filename)
	return tmpl

def _stream(filename, **args):
	return _template(filename).generate(utils = utils, **args)

def _mainstream(req, filename, **args):
	req.content_type = 'text/html;charset=utf-8'
	if not args.has_key('errormsg'):
		args['errormsg'] = ''
	return _stream('mainframe.html', baseurl = _url(req, ''), content = _stream(filename, **args), **args )

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

def _ajaxstream(req, filename, selectors, **args):
	"""Creates a genshi.Stream object containing XML response data suitable for
	the JS AJAX functions in ajax.js. 
	
	It requires the mod_python request object, the filename of the proper 
	template, the XPath selector string (or list of strings) of all elements
	that need to be updated (currently, these elements need to have an 
	id attribute!), and any named variables the template may need.
	If one of the named variables is called "errormsg", <div id="errormessage">
	is automatically selected.
	
	Call example:
		stream = _ajaxstream(req, "index.html", 
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
	s = list(_mainstream(req, filename, **args))
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
	req.content_type = 'text/xml'
	return Stream(_insert(frame, u'insert', *main))
	
def index(req):
	util.redirect(req, _url(req, 'start'))

def start(req):
	stream = _mainstream(req, 'index.html')
	return stream.render('xhtml')
	
def newgameform(req):
	stream = _mainstream(req, 'newgameform.html')
	return stream.render('xhtml')
	
def view(req, id, msg = ""):
	stream = None
	game = None
	try:
		game = _loadgame(id, False)
	except:
		stream = _mainstream(req, 'error.html', errormsg = "Sorry, diese Spiel-ID existiert nicht.", returnurl="start")
	else:
		stream = _mainstream(req, 'view.html', game = game, errormsg = msg)
	return stream.render('xhtml')

def error(req, msg = "", returnurl = "index"):
	#game = _loadgame(id, False)
	stream = _mainstream(req, 'error.html', errormsg = msg, returnurl = returnurl)
	return stream.render('xhtml')

def gamegraph(req, id, roundid, mastercode=''):
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
	fname = os.path.join(G.savegamedir, '%s_%s%s.png' % (game.id, round.name, '-admin' if adminview else ''))
	tries = 0
	while tries < 10:
		try:
			moerdergraph(round, fname, adminview)
			tries = 10
		except:
			time.sleep(0.01)
			tries += 1
	req.content_type = 'image/png'
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
	
def gamegraphall(req, id, roundid='', mastercode=''):
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
	fname = os.path.join(G.savegamedir, '%s_%s%s%s.png' % (game.id, roundid, 'full', '-admin' if adminview else ''))
	tries = 0
	while tries < 10:
		try:
			if len(roundid) < 1:
				moerdergraphall(game, fname, adminview)
			else:
				moerdergraphall(game, fname, adminview, rounds=game.rounds[roundid])
			tries = 10
		except:
			time.sleep(0.01)
			tries += 1
	req.content_type = 'image/png'
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
	return ret

def addplayer(req, gameid, spielername, zusatzinfo, email='', ajax=0):
	err = ''
	game = _loadgame(gameid)
	try:
		game.addPlayer(G.u8(spielername), G.u8(zusatzinfo), G.u8(email) )
		gameid = _savegame(game)
	except GameError as e:
		err = e.__str__()
	else:
		err = "Neuer Mitspieler: %s" % G.u8(spielername)
	if ajax == '1':
		selectors = [ "//*[@id='listplayers']", "//*[@id='gameinfo']" ]
		stream = _ajaxstream(req, 'view.html', selectors, game = game, errormsg = err)
		return stream.render("xhtml")
	else:
		util.redirect(req, _url(req, 'view', gameid, err))
		return ""

def creategame(req, action, rundenname, kreiszahl, enddate, rundenid=''):
	game = moerderklassen.Game(
		G.u8(rundenname), 
		int(kreiszahl), 
		enddate, 
		_url(req, 'view',  rundenid), 
		rundenid
	)
	G.fname = os.path.join(G.savegamedir, '%s.pkl' % game.id)
	if not os.path.exists(G.fname):
		G.lockfile = filelock.FileLock(G.fname + '.lock')
		try:
			gameid = _savegame(game, True)
		except Exception as e:
			return error(req, e.__str__())
	stream = _mainstream(req, 'creategame.html', gameid = gameid, url = _url(req, 'view', id=game.id), mastercode = game.mastercode)
	return stream.render('xhtml')

def startgame(req, gameid, mastercode):
	game = _loadgame(gameid)
	try:
		game.start(mastercode)
	except GameError as e:
		return error(req, e.__str__(), _url(req, "view", gameid))
	gameid = _savegame(game)
	try:
		_pdfgen(req, game)
	except Exception as e:
		pass
	stream = _mainstream(req, 'startgame.html', game = game, adminurl = _url(req, 'admin', game.id), viewurl = req.construct_url("/" + gameid))
	return stream.render('xhtml')

def endgame(req, gameid, mastercode):
	game=_loadgame(gameid)
	try:
		game.stop(mastercode)
	except GameError as e:
		return error(req, e.__str__(), _url(req, "view", gameid))
	gameid = _savegame(game)
	stream = _mainstream(req, 'view.html', game = game, errormsg = u'Spiel beendet')
	return stream.render('xhtml')

def _pdfgen(req, game):
	return game.pdfgen()

def _pdfblankgen(req, count, game):
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

def css(req, css):
	filepath = os.path.join(G.cssdir, "%s.css" % css )
	if filepath.find("..") < 0 and os.path.isfile(filepath):
		ret = ""
		req.content_type = 'text/css'
		cssfile = None
		try:
			cssfile = file(filepath, 'r')
			ret = cssfile.read()
		except:
			pass
		finally:
			if cssfile:
				cssfile.close()
		return ret
	else:
		req.content_type = 'text/css'
		return ""

def pdfget(req, id, mastercode, count=0):
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
		req.content_type = 'application/pdf'
		pdf = file(filename, 'r')
		ret = pdf.read()
		pdf.close()
		if not count == 0:
			os.unlink(filename)
		return ret
	else:
		return error(req, u"Das war nicht der richtige Mastercode!")

def htmlget(req, id, mastercode):
	game = _loadgame(id)
	if mastercode == game.mastercode:
		req.content_type = 'text/xml;charset=utf-8'
		stream = _stream('auftrag.html', game = game)
		return stream.render('xhtml')
	else:
		return error(req, u"Das war nicht der richtige Mastercode!")

def admin(req, id=None, mastercode=None, action=None, round=None, killer=None, victim=None, datum=None, reason=None, ajax=0, spielername=None, zusatzinfo=None, email=''):
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
				stream = _ajaxstream(req, 'admin.html', selectors, game = game, errormsg = err)
			else:
				stream = _mainstream(req, 'admin.html', game = game, errormsg = err)
		else:
			err = u'Das war nicht der Game Master Code zu diesem Spiel!'
		if stream is None:
			if ajax == '1':
				stream = _ajaxstream(req, 'view.html', selectors, game = game, errormsg = err)
			else:
				stream = _mainstream(req, 'view.html', game = game, errormsg = err)
	else: #if id is None
		stream = _mainstream(req, 'index.html', errormsg = "")
	return stream.render('xhtml')

def killplayer(req, gameid, victimid, killerpublicid, datum, reason, ajax=0):
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
		stream = _ajaxstream(req, 'view.html', selectors, game = game, errormsg = errormsg)
		return stream.render('xhtml')
	else:
		stream = _mainstream(req, 'view.html', game = game, errormsg = errormsg)
		return stream.render('xhtml')

def _url(req, action, id=None, errormsg=""):
	if id is not None and action == 'view':
		# I can do this because .htaccess has this line: 
		# RewriteRule ^([a-z0-9]+)$ /moerderspiel/view?id=$1 [R=302]
		return req.construct_url("/%s" % id)
	else:
		url = req.construct_url("/moerderspiel/%s" % action)
		if id != None:
			url += '?id=' + id
		if len(errormsg) > 1 and id == None:
			url +=  '?msg=' + errormsg
		elif len(errormsg) > 1:
			url +=  '&msg=' + errormsg
		return url

def hello(req):
	return req.construct_url("/view/")

def redir(req, gameid):
	util.redirect(req, _url(req, 'view', gameid))

