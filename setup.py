import os
from setuptools import setup
cedaic_define_macros = [(
    "NPY_NO_DEPRECATED_API",
)]

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='ceda_icompress',
    version='0.1.1',
    packages=['ceda_icompress'],
    install_requires=[
        'numpy', 
        'netcdf4', 
        'click'
    ],
    include_package_data=True,
    license='BSD License',  # example license
    description='A command line client to access data compression routines.',
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
    entry_points = {
        'console_scripts': [
            'cic_analyse=ceda_icompress.CLI.cic_analyse:main',
            'cic_compress=ceda_icompress.CLI.cic_compress:main',
            'cic_display=ceda_icompress.CLI.cic_display:main'
        ]
    }
)
