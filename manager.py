pdf_folder = '/Users/christian/OneDrive - INM/References'
bib_file = '/Users/christian/OneDrive - INM/References/references.bib'

mandatory = {
  'article': ['journal', 'volume', 'pages', 'year']
}

import os, subprocess, platform
from shutil import copy2
from pypdf import PdfReader
from bib.tools import pdf2doi, doi2bib
from bib.bib import BibRef, Library, read_bib
import webbrowser

def open_file(filepath):
  # from https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os
  if platform.system() == 'Darwin':       # macOS
      subprocess.call(('open', filepath))
  elif platform.system() == 'Windows':    # Windows
      os.startfile(filepath)
  else:                                   # linux variants
      subprocess.call(('xdg-open', filepath))


def pdfs2dois(pdf_list):
  doi_list = []
  unknown = []
  for pdf in pdf_list:
    # print('pdf:', pdf)
    try: 
      doi = pdf2doi(pdf)
      doi_list.append(doi)
      # print('doi:', doi)
    except: 
      doi = ''
      ans = input(f'{pdf}: Could not extract DOI. Do you want to specify it manually? (y/n) ')
      if ans == 'y':
        open_file(pdf)
        doi = input(f'enter DOI: ')
      if doi:
        doi_list.append(doi)
      else:
        unknown.append(pdf)
        doi_list.append('')

  return doi_list, unknown


def generate_lib(pdf_list, doi_list):
  ref_list = []
  for pdf,doi in zip(pdf_list, doi_list):
    if not doi: continue
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
      ref_list.append(obj)

    except Exception as e:
      print(f'{e.__class__}: {e}')
    print()

  return Library(ref_list)


pdfs = os.listdir(pdf_folder)
pdfs = [pdf_folder+os.sep+pdf for pdf in pdfs if pdf[-4:]=='.pdf']
lib = read_bib(bib_file)
synced = [os.path.split(ref.properties['file'])[-1] for ref in lib if 'file' in ref.properties.keys()]
unsynced_pdfs = [pdf for pdf in pdfs if os.path.split(pdf)[-1] not in synced]
unsynced_bibs = [ref for ref in lib if ('file' not in ref.properties.keys()) or (ref.properties['file'] not in pdfs)]

print(f'found {len(unsynced_bibs)} bibrefs without corresponding pdf.')
print(f'found {len(unsynced_pdfs)} pdfs without corresponding bib entry.')
print(unsynced_pdfs)

new_dois, unknown = pdfs2dois(unsynced_pdfs)
if len(unknown)>0:
  print(f'\ncould not extract doi from {len(unknown)}/{len(unsynced_pdfs)} file(s):')
  for pdf in unknown:
    print(pdf)


new_refs = generate_lib(unsynced_pdfs, new_dois)


copy2(bib_file, bib_file[:-4]+'.bak')
new_refs.write(bib_file, 'a')

# with open(bib_file, 'w') as output:
#   for ref in new_refs:
#     output.write(ref.bibtex())