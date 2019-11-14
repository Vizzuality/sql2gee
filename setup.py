from distutils.core import setup

setup(name='sql2gee',
      version='0.3.0',
      description='Library to convert SQL-like queries into Google Earth Engine syntax, and return the responses',
      author='Vizzuality',
      author_email='info@vizzuality.com',
      keywords=['EarthEngine', 'SQL'],
      license='MIT',
      packages=['sql2gee', 'sql2gee.utils'],
      package_data={'sql2gee': ['tests/*.py', ], },
      test_suite='tests',
      install_requires=[
          'earthengine-api==0.1.140',
          'google-api-python-client==1.7.3',
          'cached-property==1.3.0'],
      url='https://github.com/Vizzuality/sql2gee',
      download_url='https://github.com/Vizzuality/sql2gee/tarball/0.3.0',
      zip_safe=False)
