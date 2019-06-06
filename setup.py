#from setuptools import setup
from distutils.core import setup

files = ['lib/*']

setup(name='dovalapi',
      version='2.2.2',
      description='Doval methods and tools',
      url='',
      author='Julian Dekker',
      author_email='Mai.me@julian-dekker.nl',
      license='MIT',
      packages=['dovalapi'],
      include_package_data = True,
      package_data = {'dovalapi' : files },
      )
