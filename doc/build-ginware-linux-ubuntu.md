## Building the GINware executable on Ubuntu Linux

### Method based on physical or virtual linux machine

An Ubuntu distribution with Python 3.6 is required to build GINware. This example uses Ubuntu 17.10, which comes with an appropriate version installed by default. You can verify the Python version by typing:

```
python3 --version
```

You should see a response similar to the following:

  `Python 3.6.4`

After making sure that you have the correct Python version, execute the following commands from the terminal:

```
[gw@ubuntu /]# sudo apt-get update
[gw@ubuntu /]# sudo apt-get -y upgrade
[gw@ubuntu /]# sudo apt-get -y install libudev-dev libusb-1.0-0-dev libfox-1.6-dev autotools-dev autoconf automake libtool libpython3-all-dev python3.6-dev python3-pip git cmake
[gw@ubuntu /]# sudo pip3 install virtualenv
[gw@ubuntu /]# sudo pip3 install --upgrade pip
[gw@ubuntu /]# cd ~
[gw@ubuntu /]# mkdir gw-env && cd gw-env
[gw@ubuntu /]# virtualenv -p python3.6 venv
[gw@ubuntu /]# . venv/bin/activate
[gw@ubuntu /]# pip install --upgrade setuptools
[gw@ubuntu /]# git clone https://github.com/GIN-coin/ginware
[gw@ubuntu /]# cd ginware
[gw@ubuntu /]# pip install -r requirements.txt
[gw@ubuntu /]# pyinstaller --distpath=../dist/linux --workpath=../dist/linux/build ginware.spec
```

The following files will be created once the build has completed successfully:

* Executable: `~/gw-env/dist/linux/GINware`
* Compressed executable: `~/gw-env/dist/all/GINware_<verion_string>.linux.tar.gz`
