# bibliogra.py
A Python package for DOI-based .bib and .pdf file management.

## Examples
`from bib.tools import doi2bib, pdf2doi`  
`print(doi2bib('https://doi.org/10.1103/PhysRevLett.131.156201'))`  
`print(pdf2doi('path/to/some.pdf'))`  

At this point, `pdf2doi` appears to work for about 95+% of all research articles that were downloaded directly from the publisher's website.
It *cannot* extract DOIs from arXiv articles or book pdfs.