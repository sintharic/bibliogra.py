# options
infile = "/Users/christian/OneDrive/PhD/Publications/Confinement effect/confinement.bib"
outfile = "/Users/christian/OneDrive/PhD/Publications/Confinement effect/confinement_clean.bib"

EXCLUDE_PROPS = ["abstract", "mendeley-groups", "month"]#, "keywords"]
JOUR_IN_KEY = True
RENEW_KEY = True
ABBREV_JOUR = True

# update Journal abbreviations if necessary
JAbbrev = {
  "The European Physical Journal E" : "Eur. Phys. J. E",
  "Eurphysics Letters" : "Europhys. Lett",
  "The Journal of Adhesion" : "J. Adhes.",
  "Rubber Chemistry and Technology" : "Rubber Chem. Technol.",
  "Journal of Physics D: Applied Physics" : "J. Phys. D: Appl. Phys.",
  "Macromolecular Chemistry and Physics" : "Macromol. Chem. Phys.",
  "International Journal of Engineering Science" : "Int. J. Eng. Sci.",
  "Physical Review B" : "Phys. Rev. B",
  "Physical review. B, Condensed matter" : "Phys. Rev. B",
  "Frontiers in Mechanical Engineering" : "Front. Mech. Eng.",
  "Nature Methods" : "Nat. Methods",
  "Proceedings of the Institution of Mechanical Engineers, Part C: Journal of Mechanical Engineering Science" : "Proc. Inst. Mech. Eng. C: J. Mech. Eng. Sci.",
  "Bioinspiration & Biomimetics" : "Bioinspir. Biomim.",
  "Mechanics of Time-Dependent Materials" : "Mech. Time-Depend. Mater.",
  "Mech. Time-Dependent Mater." : "Mech. Time-Depend. Mater.",
  "Phys. Rev. E - Stat. Nonlinear, Soft Matter Phys." : "Phys. Rev. E",
  "Mater. Sci. Eng. R Reports" : "Mater. Sci. Eng. R Rep.",
  "Science (80-. )." : "Science"
}
#TODO: develop simple webcrawler for abbreviaitons, e.g. via
#      https://www.resurchify.com/find/?query=nature+materials#search_results



import sys
from datetime import datetime
DATE = datetime.now().strftime("%Y-%m-%d")
from .logger import logger



def argsort(seq):
  # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
  return sorted(range(len(seq)), key=seq.__getitem__)

def split(s: str, separators):
  if isinstance(separators, str): return s.split(separators)
  
  result = s.split(separators[0])
  for separator in separators[1:]:
    result = [substr.split(separator) for substr in result]
  return result



def initials(forenames):
  if type(forenames)==str: forenames = forenames.split(" ")
  #print(forenames)#DEBUG
  newfirst = ""

  # add initial of each forename
  for string in forenames:
    # firsts separated by "-"
    firsts = string.split("-")
    if len(firsts)>1:
      for first in firsts: 
        if first[0]=="{": # first letter is an Umlaut
          newfirst += first[0:first.find("}")+1] +".-"
        else:
          newfirst += first[0]+".-"
      continue

    # firsts are initials separated by "."
    firsts = string.split(".")
    if len(firsts)>1:
      for first in firsts:
        if len(first) == 0: 
          # print(string)#DEBUG
          continue
        if first[0]=="{": # first letter is an Umlaut
          opened = 1; closed = 0
          for char in first:
            newfirst += char
            if char=="{": opened += 1
            elif char=="}": closed += 1
            if opened==closed: break
          # newfirst += first[0:first.find("}")+1] +". "
        else:
          newfirst += first[0]+". "
      continue


    # single forename: len(firsts) == 1
    if string[0]=="{": # first letter is an Umlaut
      opened = 1; closed = 0
      for char in string:
        newfirst += char
        if char=="{": opened += 1
        elif char=="}": closed += 1
        if opened==closed: break
      # newfirst += string[0:string.find("}")+1] +". "
    else:
      newfirst += string[0]+". "

  return(newfirst[:-1]) # drop trailing " " or "-"



def Jinitials(journalname):
  words = journalname.split(" ")
  initials = ""
  for word in words:  # go through each word
    if word.lower() in ["","the","of","and","to","by",r"f{\"{u}}r","und"]: continue
    else: 
      if word=="-": return initials
      if not word[0].isalnum(): continue
      initials += word[0].upper()  # append the initial
      if (word[-1]==":") or (len(word)==1): return initials
  return initials



# drop leading and trailing spaces from a string
def drop_spaces(string):
  while string[0] in (" ", "\t"): string = string[1:]
  while string[-1]==" ": string = string[:-1]
  return(string)



# check if number of opened and closed curly brackets matches
def check_brackets(string):
  opened = string.count("{")
  closed = string.count("}")

  # everything fine
  if opened==closed: return(string)

  # fix broken string
  print("WARNING: bracket mismatch: " + string)#DEBUG
  if (opened > closed): string = string + "}"*(opened-closed)
  elif (opened < closed): string = "{"*(closed-opened) + string
  return(string)


def print_error(exception, location, reference):
  print(f"ERROR in {location}: {reference.citekey}")
  for key in reference.properties.keys():
    print(f"  {key} : {reference.properties[key]}")
  print(exception)


class BibRef():

  doctype = ""
  citekey = ""
  properties = {}


  def __init__(self, bibentry):
    bibstring = ""
    if isinstance(bibentry, list):
      for line in bibentry: bibstring += line 
    else: 
      bibstring = bibentry

    # doctype and citation key from first line
    idx = bibstring.find("\n")
    line0 = bibstring[0:idx].split("{")
    if len(line0) != 2: 
      logger.warn("ambiguous document type or citation key: %s!"%str(line0))
    self.doctype = line0[0][1:].lower()
    self.citekey = line0[1].split(",")[0]
    bibstring = bibstring[idx+1:]

    # properties in rest of bibstring
    keys = []
    values = []
    prop = ""
    value = ""
    while len(bibstring) > 1:
      idx = bibstring.find("\n")
      #print(len(bibstring), idx, "-"+bibstring+"-")#DEBUG
      line = drop_spaces(bibstring[0:idx])
      if line=="}": break

      linecontent = line.split("=",1)
      
      # property starts
      if len(linecontent) == 2:
        prop = drop_spaces(linecontent[0]).lower()
        value = ""
        line = drop_spaces(linecontent[1])
      # property ends
      if line[-1] in ('"','}',',') or line[-2:] in ('",','},'):
        value += line#[0:line.rfind("}")]
        keys.append(prop.replace(" ",""))
        valuecontent = value[value.find("{")+1 : value.rfind("}")]
        #if prop=="author": print("---",value)#DEBUG
        values.append( check_brackets(valuecontent) )
      # property continues from previous line
      else:
        value += line + " "

      bibstring = bibstring[idx+1:]

    # format online references without BibLaTex
    if self.doctype=="misc":
      try: idx_url = keys.index("url")
      except: idx_url = -1
      if idx_url>=0 and ("howpublished" not in keys) and ("booktitle" not in keys): 
        # print(self.citekey) #DEBUG
        keys.append("howpublished")
        values.append(values[idx_url])

        try: 
          idx_date = keys.index("urldate")
          date = values[idx_date]
        except: 
          date = DATE
          print("WARNING: Adding today's access date for "+values[idx_url])

        try: idx_note = keys.index("note")
        except: idx_note = -1
        if idx_note>=0:
          if "accessed" not in values[idx_note].lower():
            values[idx_note] = values[idx_note] + ", accessed: " + date
        else:
          keys.append("note")
          values.append("Accessed: " + date)
      # else: print("WARNING: no url in misc item "+self.citekey) #DEBUG
      
    
    self.properties = dict(zip(keys,values))



  def clean_authors(self):
    if not "author" in self.properties.keys():
      print("WARNING: no authors in %s"%self.citekey)#DEBUG
      return()
    
    authorstring = self.properties["author"]
    authors = authorstring.split(" and")
    newauthors = ""

    for author in authors:
      author = check_brackets(author)
      last = ""
      first = ""

      author = drop_spaces(author)
      if len(author)==0: 
        print("ERROR: empty author in %s!"%self.citekey)
        continue

      # last name, first name(s) format
      newfirst = ""
      trial = author.split(",")
      if len(trial)==2:
        last,firsts = trial
        last = drop_spaces(last)
        firsts = drop_spaces(firsts)
        firsts = [name.replace(" ","") for name in firsts.split(" ")]
        first = initials(firsts)

      # first name(s) last name format
      else:
        names = author.split(" ")
        last = names[-1]
        first = initials(names[:-1])

      # potentially fix Umlauts in last name
      if last=="Mueser": last = 'M{\\"{u}}ser'
      if last=="Mueller": last = 'M{\\"{u}}ller'

      # assemble last name and first names
      newauthors += check_brackets(last) + ", " + check_brackets(first) + " and "

    newauthors = newauthors[:-5]
    self.properties["author"] = newauthors
    #print(newauthors)#DEBUG



  def clean_journal(self):
    if not "journal" in self.properties.keys(): return()

    jour = self.properties["journal"]
    if jour in JAbbrev.keys(): self.properties["journal"] = JAbbrev[jour]


  def bibtex(self):
    # head
    string = "@" + self.doctype + "{" + self.citekey + ",\n"
    
    # author, title, year come first
    if "author" in self.properties.keys():
      string += "  author    = {" + check_brackets(self.properties["author"]) + "},\n"
    if "title" in self.properties.keys():
      string += "  title     = {" + check_brackets(self.properties["title"]) + "},\n"
    if "year" in self.properties.keys():
      string += "  year      = {" + check_brackets(self.properties["year"]) + "},\n"

    # then all other properties
    for key in self.properties.keys():
      if key not in ["author","title","year","file","doi"]:
        string += "  " + key.ljust(9) + " = {"
        string += check_brackets(self.properties[key]) + "},\n"

    # file and doi come last
    if "file" in self.properties.keys():
      string += "  file      = {" + check_brackets(self.properties["file"]) + "},\n"
    if "doi" in self.properties.keys():
      string += "  doi       = {" + check_brackets(self.properties["doi"]) + "},\n"
    
    string = string[:-2] + "\n}\n\n" # drop comma after final property

    return(string)

  def exclude_props(self, exclude):
    # then all other properties
    for key in self.properties.keys():
      if key in exclude: self.properties.pop(key)


  def renew_citekey(self):
    try:
      key = self.properties["author"].split(",")[0]
      for char in ["ä", "á", "à"]: key = key.replace(char, "a")
      for char in ["ë", "é", "è"]: key = key.replace(char, "e")
      for char in ["ï", "í", "ì"]: key = key.replace(char, "i")
      for char in ["ö", "ó", "ò"]: key = key.replace(char, "o")
      for char in ["ü", "ú", "ù"]: key = key.replace(char, "u")
      for char in ["ñ", r"{\~{n}}"]: key = key.replace(char, "n")
      for char in ["a", "e", "i", "o", "u"]:
        key = key.replace('\\"{%s}'%char, char)
        key = key.replace("\\'{%s}"%char, char)
        key = key.replace("\\´{%s}"%char, char)
        key = key.replace("\\`{%s}"%char, char)
        # key = key.replace("{\"{%s}}"%char, char)
        # key = key.replace('{\\"{%s}}'%char, char)
        # key = key.replace("{\\'{%s}}"%char, char)
        # key = key.replace("{\\´{%s}}"%char, char)
        # key = key.replace("{\\`{%s}}"%char, char)
      key = key.replace("ç","c")
      for char in ["{","}"," ","-"]: key = key.replace(char, "")
      if self.doctype in ("online"): 
        if "url" in self.properties.keys():
          website = self.properties["url"]
          website = website.split("//")[-1]
          website = website.split("www.")[-1]
          website = website.split(".")[0]
          key += "_" + website
        else: 
          key += "_Website"
      else: 
        key += str(self.properties["year"])
      self.citekey = key
    except BaseException as e:
      print_error(e, "renew_citekey()", self)


  def add_jour_to_key(self):
    if not self.citekey: 
      print("---", self.properties["author"], ":", self.properties["title"])
      self.renew_citekey()
    if not self.citekey[-1].isdigit(): self.citekey = self.citekey[:-1] # avoids format Persson2001a
    if self.doctype != "article": return
    ji = Jinitials(self.properties["journal"])
    if self.citekey[-len(ji):] != ji: self.citekey = self.citekey + ji



class Library:
  _list = []

  def __init__(self, entries=None):
    if entries is None: return
    self._list = entries

  def __getitem__(self, key):
    return self._list[key]

  def __len__(self):
    return len(self._list)

  def add(self, ref):
    self._list.append(ref)

  def clean(self, renew_key=RENEW_KEY, jour_in_key=JOUR_IN_KEY, abbrev_jour=ABBREV_JOUR, exclude_props=EXCLUDE_PROPS):
    for ref in self._list:
      ref.clean_authors()
      if abbrev_jour: ref.clean_journal()
      if renew_key: ref.renew_citekey()
      if jour_in_key: ref.add_jour_to_key()
      if exclude_props: ref.exclude_props(exclude_props)

    # sort references alphabetically
    refkeys = [ref.citekey for ref in self._list]
    self._list = [self._list[idx] for idx in argsort(refkeys)]

    # check for identical keys
    duplicates = 0
    for idx in range(1,len(self._list)):
      if self._list[idx].citekey == self._list[idx-1-duplicates].citekey:
        #print(self._list[idx].citekey)#DEBUG
        duplicates += 1
        self._list[idx].citekey = self._list[idx].citekey + chr(ord("a")+duplicates-1)
      else:
        duplicates = 0

  def write(self, filename, mode="w"):
    with open(filename, mode) as output:
      for ref in self._list:
        output.write(ref.bibtex())




def read_bib(filename):

  bibstrings = []
  opened = 0; closed = 0 # count open/closed curly brackets
  isentry = False

  with open(filename,"r") as file:
    for line in file.readlines():

      # entry starts
      if line[0]=="@":
        bibstrings.append(line)
        opened += 1
        isentry = True
      elif isentry: 
        bibstrings[-1] += line
        opened += line.count("{")
        closed += line.count("}")

        # entry ends
        if opened == closed:
          opened = 0
          closed = 0
          isentry = False

  # convert strings to BibRef objects
  entries = []
  for entry in bibstrings:
    entries.append(BibRef(entry))
  
  return(Library(entries))



def main():
  if len(sys.argv) > 1:
    infile = sys.argv[1]
  if len(sys.argv) > 2:
    outfile = sys.argv[2]
  elif len(sys.argv) > 1:
    outfile = infile[:-4] + "_clean.bib"

  lib = read_bib(infile)
  lib.clean()
  lib.write(outfile)

if __name__ == '__main__':
  main()