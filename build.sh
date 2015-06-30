# Temporary solution until I get round to writing a makefile

set -e  # Exit on failure

VERSION=`python syrup.py --version 2>&1 | sed 's/syrup.py //g'`

echo Building Syrup $VERSION

echo Clean
find . -name "*pyc" -print0 | xargs -0 rm -rf
find . -name __pycache__ -print0 | xargs -0 rm -rf
rm -rf *spec dist build cover syrup-$VERSION.dmg

echo Tests
nosetests --with-coverage --cover-html --cover-inclusive --cover-erase --cover-tests --cover-package=syrup

echo Source build
./setup.py sdist
mv dist/syrup-$VERSION.tar.gz .
