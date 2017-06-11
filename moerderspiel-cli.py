# -*- coding: utf-8 -*-

import os, glob
import sys
workdir = '.'
modpath = os.path.join(workdir,"lib")
sys.path.insert(0,modpath)
import pickle
import codecs
import os.path
import shutil
import moerderklassen
import filelock
import logging
import datetime
from moerdergraph import moerdergraph
from pprint import pformat

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
logging.basicConfig(filename=os.path.join(G.savegamedir, 'moerderspiel-%s.log'%datetime.date.today()), level=logging.DEBUG)

def _savegame(game, checkifexists=False):
	G.fname = G.savegamedir + '/' + game.id + '.pkl'
	if checkifexists and os.path.isfile(G.fname):
		#raise AssertionError
		pass
	output = open(G.fname + '.tmp', 'wb')
	pickle.dump(game, output)
	output.close()
	os.rename(G.fname + '.tmp', G.fname)
	G.lockfile.release()
	del G.lockfile
	return game.id
	
def _loadgame(gameid, lock=True):
	G.fname = G.savegamedir + '/' + gameid + '.pkl'
	G.lockfile = filelock.FileLock(G.fname + '.lock')
	while G.lockfile.acquire():
		pass
	input = open(G.savegamedir + '/' + gameid + '.pkl', 'rd')
	ret = pickle.load(input)
	input.close()
	if not lock:
		G.lockfile.release()
		del G.lockfile
	return ret

def ldgame(gameid):
        G.fname = G.savegamedir + '/' + gameid + '.pkl'
	input = open(G.savegamedir + '/' + gameid + '.pkl', 'rd')
	ret = pickle.load(input)
	input.close()
	return ret

def resetrounds(game):
        for ro in game.rounds:
                for participant in game.rounds[ro].participants:
                        participant.killedby = None
                game.rounds[ro].participants = []                        