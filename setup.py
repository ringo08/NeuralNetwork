import sys, os
from cx_Freeze import setup, Executable

base = None

if sys.platform == 'win32':
  base = 'Win32GUI'


includes  = []
include_files = [
  ('/usr/local/Cellar/tcl-tk/8.6.12_1/lib', 'tcl8.6'),
  ('/usr/local/Cellar/tcl-tk/8.6.12_1/lib', 'tk8.6')
]
os.environ['TCL_LIBRARY'] = '/usr/local/Cellar/tcl-tk/8.6.12_1/lib/tcl8.6'
os.environ['TK_LIBRARY'] = '/usr/local/Cellar/tcl-tk/8.6.12_1/lib/tk8.6'
packages = ['configparser', 'gc', 'math', 'multiprocessing', 'os', 'random', 'shutil', 'sys', 'tkinter']
excludes = []

build_exe_options = {
    'includes': includes,
    'include_files': include_files,
    'packages': packages,
    'excludes': excludes
}

directory_table = [
  ('ProgramMenuFolder', 'TARGETDIR', '.'),
  ('NNAppMenu', 'ProgramMenuFolder', 'NNApp')
]

msi_data = {
  'Directory': ['.']
}

setup(
    name='NNApp',
    version='0.1',
    description='GUI application',
    options={ 'build_exe': build_exe_options, 'bdist_msi': { 'data': msi_data } },
    executables=[Executable(script = 'app.py', base= base)]
)