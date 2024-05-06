import sys
import urllib.request
import bibtexparser
from pypdf import PdfReader
from urllib.error import HTTPError

BASE_URL = 'http://dx.doi.org/'
DOI_KEYS = ['/doi', '/prism:doi', '/WPS-ARTICLEDOI']
DOI_KWDS = ['doi.org/', 'DOI:', 'doi:']

def doi_from_str(string):
    doi = ''
    for kwd in DOI_KWDS:
        idx = string.find(kwd)
        if idx >= 0:
            doi = string[(idx+len(kwd)):].split()[0]
            while doi[0] in (' ', '\t', '\n'): doi = doi[1:]
            break

    return doi

def doi2bib(doi):
    # source: https://scipython.com/blog/doi-to-bibtex/
    
    url = BASE_URL + doi
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/x-bibtex')
    try:
        with urllib.request.urlopen(req) as f:
            bibtex = f.read().decode()
            # The round-trip through bibtexparser adds line endings.
            bibtex = bibtexparser.loads(bibtex)
            bibtex = bibtexparser.dumps(bibtex)
        return bibtex

    except HTTPError as e:
        if e.code == 404: 
            raise ValueError('DOI not found.')
        else: 
            raise e

def pdf2doi(filename):
    doi = ''
    try: 
        pdf_file = PdfReader(filename)

        # try to extract DOI from metadata
        metadata = pdf_file.metadata
        meta_keys = metadata.keys()
        for key in DOI_KEYS:
            if key in meta_keys: doi = metadata[key]
        if not doi:
            if '/Subject' in meta_keys:
                subject = metadata['/Subject']
                doi = doi_from_str(subject)

        # try to extract DOI from first page
        if not doi:
            page = pdf_file.pages[0].extract_text()
            doi = doi_from_str(page)

        # try to extract DOI from last page
        # if not doi:
        #     page = pdf_file.pages[-1].extract_text()
        #     doi = doi_from_str(page)

        if not doi: 
            # print(metadata)#DEBUG
            # print(page)#DEBUG
            raise
        return(doi)

    except Exception as e:
        raise AttributeError(f'{filename}: error reading DOI from PDF.') from e

def main():
    try:
        doi = sys.argv[1]
    except IndexError:
        print('Usage:\n{} <doi>'.format(sys.argv[0]))
        sys.exit(1)

    print(doi2bib(doi))

if __name__ == '__main__':
    main()