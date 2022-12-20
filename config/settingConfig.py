import os
from configparser import ConfigParser

def configWrite(path_config=''):
  if not path_config:
    return
  config = ConfigParser()
  
  config['Config'] = { 'lang': 'ja' }

  datas = ['construction', 'learning', 'output', 'parameter', 'setting']
  config['Datas'] = {}
  for data in datas:
    config['Datas'][data] = data + 'Data.csv'

# Setting Paths
  config['Paths'] = {
    'root':  path_config,
    'src':  os.path.join('${root}', 'src'),
    'sample':  os.path.join('${root}', 'sample'),
    'data':  os.path.join('${root}', 'data'),
    'config':  os.path.join('${root}', 'config'),
    'configfile':  os.path.join('${config}', 'config.ini'),
    'operation':  os.path.join('${config}', 'OPERATIONFILE'),
    'reference':  os.path.expanduser('~'),
  }

  for data in datas:
    config['Paths'][data] = os.path.join('${data}', '${Datas:' + data + '}')
  
  config['Operate'] = {
    'init': 'INIT',
    'start': 'START',
    'stop': 'STOP',
    'end': 'END',
    'close': 'CLOSE'
  }

  config['Setting'] = {
    'error': '1e-05',
    'epochs': '100',
    'batch': '100',
    'interval': '1'
  }

  with open(path_config, 'w') as file:
    config.write(file)


def configUpdate(config, data, path_config=''):
  path_config = path_config if path_config else config['Paths']['configfile']
  if not path_config:
    return
  config.read(path_config)
  
  for section, option in data.items():
    if not config[section]:
      config.add_section(section)
    for key, value in option.items():
      config.set(section, key, value)

  with open(path_config, 'w') as file:
    config.write(file)

if __name__ == '__main__':
  fpath = './config/config.ini'
  configWrite(fpath)