# source: https://scipython.com/blog/doi-to-bibtex/

import sys
import urllib.request
import bibtexparser
from urllib.error import HTTPError

BASE_URL = 'http://dx.doi.org/'

def doi2bib(doi):
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

def main():
    try:
        doi = sys.argv[1]
    except IndexError:
        print('Usage:\n{} <doi>'.format(sys.argv[0]))
        sys.exit(1)

    print(doi2bib(doi))

if __name__ == '__main__':
    main()