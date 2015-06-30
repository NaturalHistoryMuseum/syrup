REM Temporary solution until I get round to writing a makefile

echo Building Syrup

echo Clean
del /S *pyc
del *spec
rmdir /Q /S dist build 

echo Tests
nosetests --with-coverage --cover-html --cover-inclusive --cover-erase --cover-tests --cover-package=syrup

echo Building MSI
python setup.py bdist_msi
