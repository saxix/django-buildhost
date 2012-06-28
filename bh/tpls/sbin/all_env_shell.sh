#!/bin/sh
BASE={{ PREFIX }}
comand=$1

if [ -z "$1" ];then
    echo "please specify a valid django command"
    exit 1
fi

for dir in `ls $BASE`;do
  if [ -e $BASE/$dir/bin/activate ]; then
    TARGET=$BASE/$dir/
    OWNER=`stat -c %U $TARGET`
    cd $TARGET
    . $TARGET/bin/activate
    echo "Running $1 on $TARGET"
    su - $OWNER -c $BASE/$dir/bin/python $TARGET/bin/pasport_admin.py $1
    deactivate
  fi

done
