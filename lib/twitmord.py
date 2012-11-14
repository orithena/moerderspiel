# -*- coding: utf-8 -*-

import twython

def twit(msg):
  try:
    client = twython.Twython(app_key='gsjHX798H87zdMYidAq99Q', app_secret='yRl0Udu9WcC1ZPc579fWiyM4Do8zeCdkGe7GPGnw', oauth_token='934156986-pwgjpVK7upWsBo0bygthT8AXHzsdZL2asTSJtOUk', oauth_token_secret='VGFnTV6aagbRvWTr7EXKtDp9i8WERmHLqFVwByM24iE')  
    client.updateStatus(status=msg)
  except:
    pass

def killmsg(victim):
  if victim.player.game.id == 'kif405':
    msg = u"Mörderspiel #%s: %s erlegte %s in Kreis %s: %s" % (victim.player.game.id, victim.killedby.killer.player.name, victim.player.name, victim.round.name, victim.killedby.reason)
    return msg[:140]

def twitkill(victim):
  if victim.player.game.id == 'kif405':
    msg = killmsg(victim)
    twit(msg[:140])

