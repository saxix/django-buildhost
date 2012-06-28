#!/bin/sh
f_yesno(){
    echo -n "Do you want to exit ? (y/N)"
    read ans
    [ $ans == "y" ] && return 0 || return 1
}

VERSION=`python -c "import pasportng as p;print p.get_version()"`
echo "This will upgrade the PASport NG ($VERSION) instance on '{{base}}'"
echo -n "Please confirm (y/N) "
read ans

if [ "$ans" == "y" ];then
    pasport_admin.py offline activate
    pip install Wfp-PASPortNG --upgrade -f {{pypi}}
    pasport_admin.py collectstatic --noinput
    pasport_admin.py syncdb --noinput
    apachectl reload
    pasport_admin.py offline deactivate

else
    echo "Aborted"
fi
