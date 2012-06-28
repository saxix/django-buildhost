#!/bin/sh

if [ -z "$1" ];then
    echo "please specify a valid django command"
    exit 1
fi
COMMAND=$1

TARGET="/opt/pasport_instances/pasport"
OWNER=`stat -c %U $TARGET/bin`
ADMIN_HOME=`su - $OWNER -c "echo ~"`

if [ -e $ADMIN_HOME/bin/activate ]; then

    . $ADMIN_HOME/bin/activate
    echo "Running '$COMMAND' on $ADMIN_HOME as $OWNER"
    echo "su - $OWNER -c $ADMIN_HOME/bin/python $ADMIN_HOME/bin/pasport_admin.py $COMMAND"
    su - $OWNER -c "$ADMIN_HOME/bin/python $ADMIN_HOME/bin/pasport_admin.py $COMMAND"
    deactivate
fi

mkdir -p $HOME/var/projects
mkdir -p $HOME/opt
mkdir -p $HOME/var/VENV
sudo apt-get install python-setuptools
sudo apt-get install python-virtualenv
sudo easy_install pip
sudo pip install virtualenvwrapper


