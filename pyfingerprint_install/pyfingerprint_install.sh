#.sh file needed for installing pyfingerprint package if it's missing

'''
Created on 07 September 2018

@author: Andrei Blindu
'''

echo 'Installing missing package pyfingerprint ...'
echo 'Installing the packages for building ...'
sudo apt-get install git devscripts
echo 'Cloning the repository ...'
git clone https://github.com/bastianraschke/pyfingerprint.git
echo 'Building the package ...'
cd ./pyfingerprint/src/
dpkg-buildpackage -uc -us
echo 'Install for Python 3 ...'
sudo dpkg -i ../python3-fingerprint*.deb
echo 'Install missing dependencies ...'
sudo apt-get -f install
echo 'Done, now you can import and use pyfingerprint package!'