from d20pfsrd import SRDSearch
import praw
from praw.helpers import comment_stream
import ConfigParser

config = ConfigParser.RawConfigParser()  
config.read(".pfrpg_bot.cfg")
username = config.get('login','username')
password = config.get('login','password')

print "u+p: '" + username + "'+'" + password + "'"

r=praw.Reddit("pfrpgbot v1.0")
r.login(username, password)

subreddit = "killersquirel11test"

processed = []
while True:
   for c in comment_stream(r, subreddit):
      response=""
      if c.id not in processed:
         if c.author.name != "pfrpg_bot":
            for line in c.body.split('\n'):
               if line.lower().startswith("!srd"):
                  #try:
                  response+=SRDSearch(line) + "\n"
                  #except Exception, err:
                     #response+="Error: badly-formatted line:\n"+line
                     #print Exception, err
            if response:
               c.reply(response)
               processed.append(c.id)

