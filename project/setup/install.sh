
# Ragul Balaji
# Using Ubuntu 20.04 LTS VM

sudo apt install -y git xterm python3 python3-pip

# old version from repo
# sudo apt install mininet

# new shit from git
git clone git://github.com/mininet/mininet
cd mininet
# git checkout 2.3.0
git checkout 2.2.2


PYTHON=python2 util/install.sh -nv
PYTHON=python3 util/install.sh -nv
