"""
PyAudio v0.2.11: Python Bindings for PortAudio.

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

import os
import platform
import sys

try:
    from setuptools import setup, Extension
    from setuptools.command.build_ext import build_ext

except ImportError:
    from distutils.core import setup, Extension
    from distutils.command.build_ext import build_ext

__version__ = "0.2.11"

# distutils will try to locate and link dynamically against portaudio.
#
# If you would rather statically link in the portaudio library (e.g.,
# typically on Microsoft Windows), run:
#
# % python setup.py build --static-link
#
# Specify the environment variable PORTAUDIO_PATH with the build tree
# of PortAudio.

STATIC_LINKING = False

if "--static-link" in sys.argv:
    STATIC_LINKING = True
    sys.argv.remove("--static-link")

portaudio_path = os.environ.get("PORTAUDIO_PATH", "./portaudio-v19")
mac_sysroot_path = os.environ.get("SYSROOT_PATH", None)

pyaudio_module_sources = ['src/_portaudiomodule.c']
include_dirs = []
external_libraries = []
extra_compile_args = []
extra_link_args = []
scripts = []
defines = []

if sys.platform == 'darwin':
    defines += [('MACOSX', '1')]
    if mac_sysroot_path:
        extra_compile_args += ["-isysroot", mac_sysroot_path]
        extra_link_args += ["-isysroot", mac_sysroot_path]
elif sys.platform == 'win32':
    bits = platform.architecture()[0]
    if '64' in bits:
        defines.append(('MS_WIN64', '1'))

if not STATIC_LINKING:
    extra_link_args = []
    external_libraries = ['portaudio']

else:
    include_dirs = [os.path.join(portaudio_path, 'include/')]
    extra_link_args = [
        os.path.join(portaudio_path, 'lib/.libs/libportaudio.a')
        ]

    # platform specific configuration
    if sys.platform == 'darwin':
        extra_link_args += ['-framework', 'CoreAudio',
                            '-framework', 'AudioToolbox',
                            '-framework', 'AudioUnit',
                            '-framework', 'Carbon']
    elif sys.platform == 'cygwin':
        external_libraries += ['winmm']
        extra_link_args += ['-lwinmm']
    elif sys.platform == 'win32':
        # i.e., Win32 Python with mingw32
        # run: python setup.py build -cmingw32
        external_libraries += ['winmm']
        extra_link_args += ['-lwinmm']
    elif sys.platform == 'linux2':
        extra_link_args += ['-lrt', '-lm', '-lpthread']
        # GNU/Linux has several audio systems (backends) available; be
        # sure to specify the desired ones here.  Start with ALSA and
        # JACK, since that's common today.
        extra_link_args += ['-lasound', '-ljack']


myextension = Extension(
    '_portaudio',
    sources=pyaudio_module_sources,
    include_dirs=include_dirs,
    define_macros=defines,
    libraries=external_libraries,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args
)

class build_ext_compiler_check(build_ext):
    def build_extensions(self):
        compiler = self.compiler.compiler_type

        # print('\n\ncompiler', compiler, 'debug_variable_value', debug_variable_value)
        for extension in self.extensions:

            # https://stackoverflow.com/questions/22954119/linker-error-while-linking-some-windows-apis
            # https://docs.microsoft.com/en-us/cpp/error-messages/tool-errors/linker-tools-warning-lnk4098?view=vs-2019
            if extension == myextension:

                if 'msvc' in compiler:
                    # extension.extra_link_args.append('/VERBOSE:LIB')
                    extension.extra_link_args.append('/NODEFAULTLIB:libcmt.lib')
                    extension.extra_link_args.append('/DEFAULTLIB:advapi32.lib')

                # else:
                    # extension.extra_compile_args.append( '-ggdb' )
                    # extension.extra_link_args.append( '-std=c++11' )
                    # extension.libraries.append( 'hs' )
                    # extension.include_dirs.append( '/usr/include/hs' )

        super().build_extensions()

cmdclass = {}
cmdclass['build_ext'] = build_ext_compiler_check


setup(name='PyAudio',
      version=__version__,
      author="Hubert Pham",
      url="http://people.csail.mit.edu/hubert/pyaudio/",
      description='PortAudio Python Bindings',
      long_description=__doc__.lstrip(),
      scripts=scripts,
      cmdclass=cmdclass,
      py_modules=['pyaudio'],
      package_dir={'': 'src'},
      ext_modules=[myextension]
    )
