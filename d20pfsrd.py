from bs4 import BeautifulSoup
import urllib, unicodedata, re, os, errno

MAXRESULTS=1
BASEURL="http://www.d20pfsrd.com"

SPELL_PARAMETERS = ["School","Spell Level","Casting Time","Components","Range","Effect","Target","Duration","Saving Throw","Spell Resistance"]
SPELL_URL        = BASEURL+"/magic/all-spells"

ITEM_PARAMETERS  = ["Price","Slot","CL","Weight","Aura"]
ITEM_URL         = BASEURL+"/magic-items"


def sanitize(string):
   string = unicodedata.normalize('NFKD', string).encode('ascii','ignore')
   return string

def mkdir_p(path):
   if os.path.isdir(path):
      return
   try:
      os.makedirs(path)
   except OSError as exc: # Python >2.5
      if exc.errno == errno.EEXIST and os.path.isdir(path):
         pass
      else: raise

def getSoup(url):
   localUrl = url.replace(BASEURL,".") + ".html"
   mkdir_p(os.path.dirname(localUrl))
   if not os.path.exists(localUrl):
      urllib.urlretrieve (url, localUrl)
   return BeautifulSoup(open(localUrl,'r'))

def getGeneric(url, parameters):
   soup = getSoup(url)
   param_dict={}
   for param in parameters:
      param_dict[param]=""
   content = soup.find_all("div",{"id":"sites-canvas-main-content"})[0].get_text()
   for line in re.split('\n|;',content):
      for param in parameters:
         if param in line:
            param_dict[param]=sanitize(line.replace(param,""))
   name=sanitize(soup.find_all("span",{"id":"sites-page-title"})[0].contents[0])
   description=sanitize(re.split(r'\s*description\s*',content,flags=re.I)[1])
   
   ret = "**[{name}]({url})**  \n".format(name=name,url=url)
   for param in parameters:
      ret += " - **{param}** {value}".format(param=param,value=param_dict[param])
   ret += "\n\n"
   ret += description
   return ret

def genericSearch(url, name, parameters, line):
   response="""Retrieving list of {name} matching "{line}"\n\n---\n\n""".format(line=line, name=name)
   links = getSoup(url).find_all("li")
   idx=0
   otherOptions=[]
   for link in links:
      if line in link.get_text().lower():
         if idx == MAXRESULTS:
            response += "Maximum number of results reached. Try using more specific keywords\n\n"
         elif idx > MAXRESULTS:
            otherOptions.append(link.get_text())
         else:
            link_url = BASEURL+str(link.find("a").get('href'))
            response += getGeneric(link_url, parameters)
         idx += 1
   if otherOptions:
      response += "Other possible options include " + ", ".join(otherOptions) + "\n\n"
   return response

def SRDSearch(line):
   line = line.split(" ",1)[1]
   (searchType,line) = line.split(" ",1)
   searchType=searchType.lower()
   line=line.strip().lower()

   if searchType in ["spell","spells"]:
      return genericSearch(SPELL_URL, "spells", SPELL_PARAMETERS, line)
   elif searchType in ["item","items","magic"]:
      return genericSearch(ITEM_URL, "items", ITEM_PARAMETERS, line)
   else:
      return "Error, !srd should be followed by one of the following:\n\t Spell,\n"

