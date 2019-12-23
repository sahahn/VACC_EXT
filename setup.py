from setuptools import setup, find_packages

setup(name='ABCD_ML_VACC_EXT',
      version='0.1',
      description='ABCD_ML Vacc Ext',
      url='http://github.com/sahahn/ABCD_ML_VACC_EXT',
      author='Sage Hahn',
      author_email='sahahn@euvm.edu',
      license='MIT',
      packages=['VACC_EXT'],
      install_requires=['paramiko', 'IPython>=7', 'cffi>=1.13'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
