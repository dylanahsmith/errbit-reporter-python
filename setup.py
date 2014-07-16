from setuptools import setup

exec(open('errbit_reporter/version.py').read())

setup(name='errbit-reporter',
      version=VERSION,  # noqa
      description='Errbit Client',
      long_description=open('README.rst').read(),
      author='Dylan Thacker-Smith',
      author_email='Dylan.Smith@shopify.com',
      url='https://github.com/dylanahsmith/errbit-reporter-python',
      packages=['errbit_reporter'],
      license='MIT License',
      install_requires=[
          'six',
      ],
      setup_requires=[
          'sphinx-pypi-upload',
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
