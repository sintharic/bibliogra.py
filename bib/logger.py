import os, sys
import logging
import json
logger = logging
JSON = 'logger.json'



datefmt = '%Y-%m-%d %H:%M:%S'
level = logging.INFO
logname = ''
msgfmt = '[%(levelname)s] %(message)s'



if os.path.isfile(JSON):
  params = json.load(open(JSON))
  if 'filename' in params.keys(): logname = params['filename']
  if 'format' in params.keys(): msgfmt = params['format']
  if 'datefmt' in params.keys(): datefmt = params['datefmt']
  if 'level' in params.keys(): 
    val = params['level']
    if val in ('debug','DEBUG'): level = logging.DEBUG
    elif val in ('info','INFO'): level = logging.INFO
    elif val in ('warning','WARNING'): level = logging.WARNING
    elif val in ('error','ERROR'): level = logging.ERROR
    elif val in ('critical','CRITICAL'): level = logging.CRITICAL
    else:
      try: 
        val = int(val)
        level = val
      except: 
        raise ValueError(f'invalid logging level in {JSON}: \'{val}\'')

if logname:
  logger.basicConfig(filename=logname, filemode='a', 
                     format='%(asctime)s '+msgfmt, 
                     datefmt=datefmt,
                     level=level)
else: 
  logger.basicConfig(stream=sys.stderr,
                     format=msgfmt, 
                     datefmt=datefmt,
                     level=level)