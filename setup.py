from setuptools import setup, find_packages, Extension
import sys
import re


def get_requires():
    reqs = []
    for line in open('requirements.txt', 'r').readlines():
        reqs.append(line)
    return reqs

setup(
    name='whereistheplanet',
    version='1.0.0',
    description='predict exoplanet locations',
    url='https://github.com/semaphoreP/whereistheplanet',
    author='',
    author_email='',
    license='BSD',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'whereistheplanet = whereistheplanet:main',
        ],
    },
    include_dirs=[],
    data_files=[],
    zip_safe=False,
    classifiers=[
        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Astronomy',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        ],
    keywords='Orbits Astronomy Astrometry',
    install_requires=get_requires()
    )
