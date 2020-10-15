import setuptools
import glob
import os
from setuptools import setup, find_packages

required = [
    "requests",
    "pandas",
    "six",
    "pytools",
    "nest_asyncio",
    "jinja2",
    "uvicorn",
    "gunicorn",
    "aiohttp",
    "dominate",
    "pglast",
    "flask",
    "RestrictedPython"
]

setup(name="radixdb",
      version="0.1",
      description="RadixDB",
      long_description='A new way to program database',
      classifiers=[
          'Topic :: Nocode',
          'Topic :: KnowledgeBase',
          'Topic :: Database',
          'Topic :: SlackBot',
          ],
      author="Min Wei",
      author_email="minwei@acme",
      license="MIT",
      url="http://radixdb.com",
      packages=find_packages(),
      package_data={'radixdb': ['bin/*', 'sql/*.sql', 'web/*', 'web/scripts/*', 'web/css/*', 'web/images/*']},
      install_requires= required)
