import requests
from bs4 import BeautifulSoup
import re

def find_all(substr, string):
  return [m.start() for m in re.finditer(substr, string)]

def html_content(url, decode=True):
  response = requests.get(url)
  if response.status_code != 200:
    print('ERROR: Failed to fetch the website.')
    return ''
  
  if decode: return(response.content.decode())
  else: return(response.content)

def bs_parse(url):
  return BeautifulSoup(html_content(url, decode=False), 'html.parser')
