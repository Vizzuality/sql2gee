from setuptools import setup, find_packages

setup(name='sql2gee',
      version='0.2.0',
      description='Library to convert SQL-like queries into Google Earth Engine syntax, and return the responses',
      author='Benjamin Laken, Alicia Arenzana, Ivan Birkmingan, Adam Pain',
      author_email='benjamin.laken@vizzuality.com',
      keywords=['EarthEngine', 'SQL'],
      license='MIT',
      packages=find_packages(exclude=('tests',)),
      install_requires=[
          'earthengine-api==0.1.95',
          'google-api-python-client==1.5.5',
          'cached-property==1.3.0'],
      package_data={'sql2gee': ['tests/*.py', ], },
      test_suite='tests',
      url='https://github.com/Vizzuality/sql2gee',
      download_url='https://github.com/Vizzuality/sql2gee/tarball/0.2.0',
      zip_safe=False)
