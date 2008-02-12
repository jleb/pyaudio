"""
pyAudio v0.1.0: Python Bindings for PortAudio.

Copyright (c) 2006 Hubert Pham

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY
OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from distutils.core import setup, Extension
import sys

__revision__ = "$Revision: 14 $"


ALSA_SUPPORT = False
if "--with-alsa" in sys.argv:
    ALSA_SUPPORT = True
    sys.argv.remove("--with-alsa")

STATIC_LINKING = False

pyaudio_module_sources = ['_portaudiomodule.c']
external_includes = ['../include']

external_library_dirs = []
external_libraries = []

extra_compile_args = []
extra_link_args = []

scripts = []

# for dynamic linking
if not STATIC_LINKING:
    external_library_dirs = ['/usr/lib']
    external_libraries = ['portaudio']

# for static linking, be sure to include
# the static library archive
if STATIC_LINKING:
    extra_link_args += ['/usr/lib/libportaudio.a']


# platform specific configuration
if sys.platform == 'darwin':

    # take care of portaudio Darwin build dichotomy
    # (as of 5/23/2006, portaudio's Makefile.darwin
    #  stashes libraries in ../lib/ rather than
    #  ../lib/.libs as autoconf does.)
    if STATIC_LINKING:
        import os
        try:
            # see if this file exists
            os.stat('../lib/.libs/libportaudio.a')
        except OSError:
            # no? then get rid of it...
            try:
                extra_link_args.remove('../lib/.libs/libportaudio.a')
            except ValueError:
                pass
            # and add the static library from where
            # we suspect it to really be
            extra_link_args += ['../lib/libportaudio.a']
        else:
            pass
        
    extra_link_args += ['-framework', 'CoreAudio',
                        '-framework', 'AudioToolbox',
                        '-framework', 'AudioUnit',
                        '-framework', 'Carbon']
    try:
        import bdist_mpkg
    except ImportError, e:
        pass
    
elif sys.platform == 'cygwin':
    external_libraries += ['winmm']

    if STATIC_LINKING:
        extra_link_args += ['-lwinmm']    

    
elif sys.platform == 'win32':
    # i.e., Win32 Python with mingw32
    # run: python setup.py build -cmingw32
    # libraries += ['winmm']
    external_libraries += ['winmm']
    scripts += ['postinst.py']

    # a hack: be sure to include winmm libraries
    # at the end so that they are included after
    # static linking
    if STATIC_LINKING:
        extra_link_args += ['-lwinmm']    
    
else:
    # probably GNU/Linux
    external_libraries += ['rt', 'm', 'pthread']
    if ALSA_SUPPORT:
        external_libraries += ['asound']

pyAudio = Extension('_portaudio',
                    sources = pyaudio_module_sources,
                    include_dirs = external_includes,
                    library_dirs = external_library_dirs,
                    libraries = external_libraries,
                    extra_compile_args = extra_compile_args,
                    extra_link_args = extra_link_args)
               
setup (name = 'pyAudio',
       version = '0.1.0',
       author = "Hubert Pham",
       url = "http://people.csail.mit.edu/hubert/pyaudio/",
       description = 'PortAudio Python Bindings',
       long_description = __doc__.lstrip(),
       py_modules = ['pyaudio'],
       # postinstall script mainly for bdist_wininst
       scripts = scripts,
       ext_modules = [pyAudio])
