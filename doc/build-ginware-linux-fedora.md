## Building the GINware executable on Fedora Linux

### Method based on physical or virtual linux machine

Execute the following commands from the terminal:

```
[gw@fedora /]# sudo yum update -y
[gw@fedora /]# sudo yum group install -y "Development Tools" "Development Libraries"
[gw@fedora /]# sudo yum install -y redhat-rpm-config python3-devel libusbx-devel libudev-devel cmake gcc-c++
[gw@fedora /]# sudo yum remove -y gmp-devel
[gw@fedora /]# sudo pip3 install virtualenv
[gw@fedora /]# cd ~
[gw@fedora /]# mkdir gw-env && cd gw-env
[gw@fedora /]# virtualenv -p python3 venv
[gw@fedora /]# . venv/bin/activate
[gw@fedora /]# pip install --upgrade setuptools
[gw@fedora /]# git clone https://github.com/GIN-coin/ginware
[gw@fedora /]# cd ginware
[gw@fedora /]# pip install -r requirements.txt
[gw@fedora /]# pyinstaller --distpath=../dist/linux --workpath=../dist/linux/build ginware.spec
```

The following files will be created once the build has completed successfully:
* Executable: `~/gw-env/dist/linux/GINware`
* Compressed executable: `~/gw-env/dist/all/GINware_<verion_string>.linux.tar.gz`
