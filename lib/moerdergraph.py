#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
import yapgvb as graph
import textwrap
import math
import utils
from moerderklassen import *

def u8(s):
	try:
		return s.decode('utf8')
	except UnicodeDecodeErrors:
		try:
			return s.decode('latin1')
		except UnicodeDecodeError:
			return None

def moerdergraph(round, filename, alledges=False, nodefontsize=8.0, edgefontsize=8.0):
	# G is the main Graph object
	G = graph.Digraph("Moerder")
	# a dict for indexing all nodes
	nodes = {}
	# we need to keep some of the nodes in mind
	prev_node = first_node = node = None
	# make a copy of the participant list so we don't jumble up the original list
	participants = round.participants[:]
	if not alledges:
		# if not admin/gameover view: sort nodes prior to adding them to the graph
		participants.sort(key = lambda p: p.player.name + p.player.info)
	# for each participant, add a node to the graph bearing his name
	for participant in participants:
		name = participant.player.name
		if len(participant.player.info) > 0:
			name += "\\n" + participant.player.info
		node = G.add_node(participant.player.public_id)
		node.label = name.encode('utf-8')
		node.fontsize = nodefontsize
		node.margin = 0.03
		if not prev_node:
			first_node = node
		# put all the nodes into a dict so we could find them fast by the player's id (needed later)
		nodes[participant.player.public_id] = node
		
		prev_node = node
		node.fontname = 'arial'
		# kicked participants are gray
		if participant.killed() and participant.killedby.killer is None:
			node.color = 'gray'
			node.fontcolor = 'gray'
		# dead participants are red
		if participant.killed() and not participant.killedby.killer is None:
			node.color = 'red'
			node.fontcolor = 'red'

	for participant in round.participants:
		if alledges or participant.killed():
			# add black edges for the initial kill assignment
			edge = G.add_edge(nodes[participant.getInitialKiller().player.public_id], nodes[participant.player.public_id])
			edge.color = 'black'
			edge.weight = 1.0
		if participant.killed():
			# add red edges for the kill
			if not participant.killedby.killer is None:
				# normal case
				edge = G.add_edge(nodes[participant.killedby.killer.player.public_id], nodes[participant.player.public_id])
			else:
				# special case of a game master kill
				node = G.add_node('vorzeitig ausgestiegen')
				node.fontsize = nodefontsize
				node.fontname = 'arial'
				node.color = 'gray'
				node.fontcolor = 'gray'
				edge = G.add_edge(node, nodes[participant.player.public_id])
			edge.color = 'red'
			edge.fontcolor = 'red'
			edge.weight = 1.0
			# set edge label to kill description
			label = utils.dateformat(participant.killedby.date) + ":\\n"
			maxlinelen = max(24, math.trunc(math.ceil(math.sqrt(6 * len(participant.killedby.reason)))))
			label += "\\n".join(textwrap.wrap(participant.killedby.reason, maxlinelen))
			edge.label = label.encode('utf-8')
			edge.fontsize = edgefontsize
			edge.fontname = 'arial'
	# do the layout math and save to file
	G.layout(graph.engines.dot)
	G.render(filename)
