# -*- coding: latin-1 -*-


from setuptools import setup

# NOTE: if there is a problem with symlinks, update setuptools:
# http://stackoverflow.com/questions/27459888/how-to-make-setuptools-follow-symlinks

with open('README') as file:
    long_description = file.read()

setup(name='pynotebook',
      version='0.3.0',
      description = 'A wxPython based notebook environment for interactive computing.',
      long_description = long_description,
      author='C. Ecker',
      author_email='textmodelview@gmail.com',
      url='https://github.com/chrisecker/pynotebook',
      license='BSD',
      packages=['pynotebook', 'pynotebook/textmodel', 'pynotebook/wxtextview'],
      install_requires = ['cerealizer'],
      keywords = ['Interactive', 'Interpreter', 'Notebook', 'Shell', 'wxPython'],
      classifiers = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.0',
      ],
     )

