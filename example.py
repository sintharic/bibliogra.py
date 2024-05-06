refpath = '/Users/christian/OneDrive - INM/References'
bibfile = refpath+'/references.bib'

mandatory = {
  'article': ['journal', 'volume', 'pages', 'year']
}

import os
from pypdf import PdfReader
# import bibtexparser
from bib.tools import pdf2doi, doi2bib
from bib.bib import BibRef
import webbrowser

pdfs = os.listdir(refpath)
pdfs = [refpath+os.sep+pdf for pdf in pdfs if pdf[-4:]=='.pdf']

unknown = []
refs = []
for pdf in pdfs:
  # print(pdf)
  
  try: 
    doi = pdf2doi(pdf)
    print(doi)
  except: 
    unknown.append(pdf)
    continue

  continue#DEBUG

  try:
    bib = doi2bib(doi)
    obj = BibRef(bib)
    obj.properties['file'] = pdf
    
    # ensure that the bib entry contains the mandatory fields
    if obj.doctype in mandatory.keys():
      for prop in mandatory[obj.doctype]:
        if prop not in obj.properties.keys():
          ans = input(f'field \'{prop}\' missing. Do you want to specify it manually? (y/n) ')
          if ans == 'y':
            webbrowser.open(obj.properties['url'])
            ans = input(f'enter value for \'{prop}\': ')
            if ans: obj.properties[prop] = ans
    refs.append(obj)

  except Exception as e:
    print(f'{type(e)}: {e}')
  print()

print(f'\ncould not extract doi from {len(unknown)} file(s):')
for pdf in unknown:
  print(pdf)

with open(bibfile, 'w') as output:
  for ref in refs:
    output.write(ref.bibtex())