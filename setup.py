
from setuptools import setup, find_packages

setup(name='sql2gee',
      version='0.0.1',
      description='Library to convert SQL queries into Google Earth Engine syntax',
      author='Raul Requero',
      author_email='raul.requero@vizzuality.com',
      license='MIT',
      packages=find_packages(exclude=('tests',)),
      install_requires=[
        'sqlparse>=0.2.2',
        'earthengine-api==0.1.95',
        'google-api-python-client==1.5.5'
      ],
      package_data={
        'sql2gee': [
            'tests/*.py',
        ],
      },
      test_suite='tests',
      zip_safe=False)