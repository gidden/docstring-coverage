from setuptools import setup
from docstringcoverage import cover
setup(name='docstring-coverage',
      version=cover.__version__,
      author='Alexey Strelkov',
      author_email='datagreed@gmail.com',
      url='https://bitbucket.org/DataGreed/docstring-coverage/',
      license='MIT',
      packages=['docstringcoverage'],
      entry_points = {
              'console_scripts': [
                  'docstring-coverage = docstringcoverage.cover:main',                  
              ],              
          },
      long_description="A simple audit tool for examining python source files for missing docstrings. Lists missing docstring, shows percentage of docstring coverage and rates it.")