import sys, os
from cx_Freeze import setup, Executable

base = None

if sys.platform == 'win32':
  base = 'Win32GUI'

includes  = ['configparser', 'gc', 'math', 'multiprocessing', 'os', 'random', 'shutil', 'sys', 'tkinter']
# include_files = [
#   ('/Library/Frameworks/Python.framework/Versions/3.10/lib', 'tcl8.6'),
#   ('/Library/Frameworks/Python.framework/Versions/3.10/lib', 'tk8.6')
# ]
# os.environ['TCL_LIBRARY'] = '/Library/Frameworks/Python.framework/Versions/3.10/lib/tcl8.6'
# os.environ['TK_LIBRARY'] = '/Library/Frameworks/Python.framework/Versions/3.10/lib/tk8.6'
# packages = ['configparser', 'gc', 'math', 'multiprocessing', 'os', 'random', 'shutil', 'sys', 'tkinter']
# excludes = []

build_exe_options = {
    'includes': includes,
    # 'include_files': include_files,
    # 'packages': packages,
    # 'excludes': excludes
}

# directory_table = [
#   ('ProgramMenuFolder', 'TARGETDIR', '.'),
#   ('NNAppMenu', 'ProgramMenuFolder', 'NNApp')
# ]

setup(
    name='NNApp',
    version='0.1',
    description='GUI application',
    options={ 'build_exe': build_exe_options },
    executables=[Executable(script = 'app.py', base=base)]
)