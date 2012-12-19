#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
import yapgvb as graph
import textwrap
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
	G = graph.Digraph("Moerder")

	nodes = {}
	prev_node = first_node = node = None
	participants = round.participants[:]
	if not alledges:
		participants.sort(key = lambda p: p.player.name + p.player.info)
	for participant in participants:
		name = participant.player.name
		if len(participant.player.info) > 0:
			name += "\\n" + participant.player.info
		node = G.add_node(participant.player.public_id)
		node.label = name.encode('utf-8')
		node.fontsize = nodefontsize
		node.margin = 0.03
		if prev_node:
			if alledges:
				edge = G.add_edge(prev_node, node)
		else:
			first_node = node
		nodes[participant.player.public_id] = node
		prev_node = node
		node.fontname = 'arial'
		if participant.killed() and participant.killedby.killer is None:
			node.color = 'gray'
			node.fontcolor = 'gray'
		if participant.killed() and not participant.killedby.killer is None:
			node.color = 'red'
			node.fontcolor = 'red'
	if alledges:
		edge = G.add_edge(node, first_node)

	for participant in round.participants:
		if participant.killed():
			# add black edges for the initial killer
			edge = G.add_edge(nodes[participant.getInitialKiller().player.public_id], nodes[participant.player.public_id])
			edge.color = 'black'
			edge.weight = 1.0
			# add red edges for the kill
			if not participant.killedby.killer is None:
				edge = G.add_edge(nodes[participant.killedby.killer.player.public_id], nodes[participant.player.public_id])
			else:
				node = G.add_node('vorzeitig ausgestiegen')
				node.fontsize = nodefontsize
				node.fontname = 'arial'
				node.color = 'gray'
				node.fontcolor = 'gray'
				edge = G.add_edge(node, nodes[participant.player.public_id])
			edge.color = 'red'
			edge.fontcolor = 'red'
			edge.weight = 1.0
			label = participant.killedby.date + ":\\n"
			label += "\\n".join(textwrap.wrap(participant.killedby.reason, 28))
			#l = len(label)
			#maxlen = 25
			#i = 0
			## set label for kill edge
			#while l > maxlen:
			#	i = label.find(' ', i+maxlen)
			#	if i >= 0:
			#		label = label[:i] + "\\n" + label[i+1:]
			#		l = l - i
			#	else:
			#		break
			edge.label = label.encode('utf-8')
			edge.fontsize = edgefontsize
			edge.fontname = 'arial'
	G.layout(graph.engines.dot)
	G.render(filename)
