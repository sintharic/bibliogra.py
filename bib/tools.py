import sys
import urllib.request
import bibtexparser
from pypdf import PdfReader
from urllib.error import HTTPError
from .logger import logger
sys.path.append('.')

BASE_URL = 'http://dx.doi.org/'
DOI_KEYS = ['/doi', '/prism:doi', '/WPS-ARTICLEDOI']
DOI_CONTAINING_KEYS = ['/Subject', '/Keywords']
DOI_KWDS = ['doi.org/', 'DOI:', 'doi:', 'DOI']

def doi_from_str(string):
    logger.debug('doi_from_str():')
    doi = ''
    for kwd in DOI_KWDS:
        idx = string.find(kwd)
        if idx >= 0:
            split = string[(idx+len(kwd)):].split()
            doi = split[0]
            # there might be whitespace between the two parts of the DOI
            if len(doi) < 8: 
                doi += split[1]
                doi = doi[:7] + '/' + doi[8:]
            elif len(doi) < 12: 
                doi += split[1]
            while doi[0] in (' ', '\t', '\n'): doi = doi[1:]
            break

    return doi

def doi2bib(doi):
    # source: https://scipython.com/blog/doi-to-bibtex/
    logger.debug(f'doi2bib({doi}):')
    
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
            raise Exception(f'Website {url} not found.') from e
        else: 
            raise Exception(f'DOI {doi} not found.') from e

def pdf2doi(filename):
    logger.debug(f'pdf2doi({filename}):')
    doi = ''
    try: 
        pdf_file = PdfReader(filename)

        # try to extract DOI from metadata
        logger.debug('  trying to extract from metadata...')
        metadata = pdf_file.metadata
        meta_keys = metadata.keys()
        for key in DOI_KEYS:
            if key in meta_keys: doi = metadata[key]
        if not doi:
            for key in DOI_CONTAINING_KEYS:
                if key in meta_keys:
                    value = metadata[key]
                    doi = doi_from_str(value)

        # try to extract DOI from first page
        logger.debug('  trying to extract from first page...')
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
        print(f'Usage:\n{sys.argv[0]} <doi>')
        sys.exit(1)

    print(doi2bib(doi))

if __name__ == '__main__':
    main()