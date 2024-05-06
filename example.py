pdf_folder = '/Users/christian/OneDrive - INM/References'
bib_file = pdf_folder+'/references.bib'

mandatory = {
  'article': ['journal', 'volume', 'pages', 'year']
}

import os
from pypdf import PdfReader
from bib.tools import pdf2doi, doi2bib
from bib.bib import BibRef
import webbrowser

pdfs = os.listdir(pdf_folder)
pdfs = [pdf_folder+os.sep+pdf for pdf in pdfs if pdf[-4:]=='.pdf']

unknown = []
dois = []
refs = []
for pdf in pdfs:
  # print(pdf)
  
  try: 
    doi = pdf2doi(pdf)
    dois.append(doi)
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
          ans = input(f'{obj.citekey}: field \'{prop}\' missing. Do you want to specify it manually? (y/n) ')
          if ans == 'y':
            webbrowser.open(obj.properties['url'])
            ans = input(f'enter value for \'{prop}\': ')
            if ans: obj.properties[prop] = ans
    refs.append(obj)

  except Exception as e:
    print(f'{type(e)}: {e}')
  print()

if len(unknown)>0:
  print(f'\ncould not extract doi from {len(unknown)}/{len(pdfs)} file(s):')
  for pdf in unknown:
    print(pdf)

with open(bib_file, 'w') as output:
  for ref in refs:
    output.write(ref.bibtex())