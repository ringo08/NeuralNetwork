import os
from configparser import ConfigParser

def write(fpath=''):
  config = ConfigParser()

  datas = ['construction', 'learning', 'output', 'param', 'setting']
  config['Datas'] = {}
  for data in datas:
    config['Datas'][data] = data + 'Data.csv'

  config['Paths'] = {}
  config['Paths']['root'] = '.'
  config['Paths']['src'] = os.path.join('${root}', 'src')
  config['Paths']['sample'] = os.path.join('${root}', 'sample')
  config['Paths']['data'] = os.path.join('${root}', 'data')
  
  for data in datas:
    config['Paths'][data] = os.path.join('${data}', '${Datas:' + data + '}')

  with open(fpath, 'w') as file:
    config.write(file)


def update(config, data, fpath=''):
  config.read(fpath)
  
  for section, option in data.items():
    if not config[section]:
      config.add_section(section)
    for key, value in option.items():
      config.set(section, key, value)

  with open(fpath, 'w') as file:
    config.write(file)

if __name__ == '__main__':
  fpath = './config/config.ini'
  write(fpath)