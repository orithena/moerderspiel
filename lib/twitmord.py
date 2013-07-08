# -*- coding: utf-8 -*-

import twython

def twit(msg):
  try: # get tokens from https://dev.twitter.com/
    client = twython.Twython(app_key='TODO:insert app key', app_secret='TODO: insert app secret', oauth_token='TODO:insert oauth token', oauth_token_secret='TODO:insert oauth secret')  
    client.update_status(status=msg)
  except:
    pass #if there is an error while tweeting, it can't be solved by the user, so he does not need an error message

def killmsg(victim):
  if len(victim.player.game.rounds) > 1:
    msg = u"Mörderspiel #%s: %s erlegte %s in Kreis %s: %s" % (victim.player.game.id, victim.killedby.killer.player.name, victim.player.name, victim.round.name, victim.killedby.reason)
  else:
    msg = u"Mörderspiel #%s: %s erlegte %s: %s" % (victim.player.game.id, victim.killedby.killer.player.name, victim.player.name, victim.killedby.reason)
  return msg[:140]

def twitkill(victim):
  try:
    msg = killmsg(victim)
    twit(msg[:140])
  except:
    pass #if killmsg produces an error, it does not know how to produce a message for this situation

