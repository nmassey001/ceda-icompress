import os
from setuptools import Extension, setup
from Cython.Build import cythonize
cedaic_define_macros = [(
    "NPY_NO_DEPRECATED_API",
)]
import numpy

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

cedaic_extra_compile_args = ['-fno-strict-aliasing', '-O3']
in_place_build = True
lang_lev = 3

def ExtensionMacro(name, sources):
    """Shorthand to return an Extension with a default set of arguments."""
    return Extension(
                  name=name,
                  sources=sources,
                  define_macros=cedaic_define_macros,
                  extra_compile_args=cedaic_extra_compile_args,
                  include_dirs=[numpy.get_include()],
                  inplace=in_place_build,
                  language_level=lang_lev
           )

extensions = [
    ExtensionMacro(
            name="ceda_icompress.InfoMeasures.bitentropy",
            sources=["ceda_icompress/InfoMeasures/bitentropy.pyx"],
    ),
    ExtensionMacro(
            name="ceda_icompress.InfoMeasures.bitcount",
            sources=["ceda_icompress/InfoMeasures/bitcount.pyx"],
    ),
    ExtensionMacro(
            name="ceda_icompress.InfoMeasures.entropy",
            sources=["ceda_icompress/InfoMeasures/entropy.pyx"],
    ),
    ExtensionMacro(
            name="ceda_icompress.InfoMeasures.bitinformation",
            sources=["ceda_icompress/InfoMeasures/bitinformation.pyx"],
    ),
    ExtensionMacro(
            name="ceda_icompress.InfoMeasures.whichUint",
            sources=["ceda_icompress/InfoMeasures/whichUint.pyx"],
    ),
    ExtensionMacro(
            name="ceda_icompress.InfoMeasures.getsigmanexp",
            sources=["ceda_icompress/InfoMeasures/getsigmanexp.pyx"],
    ),
    ExtensionMacro(
            name="ceda_icompress.InfoMeasures.display",
            sources=["ceda_icompress/InfoMeasures/display.pyx"],
    ),
    ExtensionMacro(
            name="ceda_icompress.BitManipulation.bitshave",
            sources=["ceda_icompress/BitManipulation/bitshave.pyx"],
    ),
    ExtensionMacro(
            name="ceda_icompress.BitManipulation.bitset",
            sources=["ceda_icompress/BitManipulation/bitset.pyx"],
    ),
    ExtensionMacro(
            name="ceda_icompress.BitManipulation.bitgroom",
            sources=["ceda_icompress/BitManipulation/bitgroom.pyx"],
    ),
    ExtensionMacro(
            name="ceda_icompress.BitManipulation.bitmasks",
            sources=["ceda_icompress/BitManipulation/bitmasks.pyx"],
    ),
]

setup(
    name='ceda_icompress',
    version='0.1.1',
    packages=['ceda_icompress'],
    install_requires=[
        'numpy', 
        'cython', 
        'netcdf4', 
        'click'
    ],
    ext_modules=cythonize(extensions),
    include_package_data=True,
    license='BSD License',  # example license
    description='A command line client to access the joint-storage data migration app on JASMIN.',
    long_description=README,
    url='http://www.ceda.ac.uk/',
    author='Neil Massey',
    author_email='support@ceda.ac.uk',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: HTTP API',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
