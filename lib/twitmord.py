# -*- coding: utf-8 -*-

import twython

def twit(msg):
  try:
    client = twython.Twython(app_key='TODO:insert app key', app_secret='TODO:insert app secret', oauth_token='TODO:insert token', oauth_token_secret='TODO:insert token secret')  
    client.updateStatus(status=msg)
  except:
    pass

def killmsg(victim):
  msg = u"Mörderspiel #%s: %s erlegte %s in Kreis %s: %s" % (victim.player.game.id, victim.killedby.killer.player.name, victim.player.name, victim.round.name, victim.killedby.reason)
  return msg[:140]

def twitkill(victim):
  msg = killmsg(victim)
  twit(msg[:140])

