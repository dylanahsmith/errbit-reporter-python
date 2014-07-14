from setuptools import setup
from errbit_reporter.version import VERSION


setup(name='Errbit Reporter',
      version=VERSION,
      description='Errbit Client',
      author='Dylan Thacker-Smith',
      author_email='Dylan.Smith@shopify.com',
      url='https://github.com/dylanahsmith/errbit-reporter-python',
      packages=['errbit_reporter'],
      license='MIT License',
      install_requires=[
          'six',
      ],
      test_suite='test',
      platforms='Any',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ])
