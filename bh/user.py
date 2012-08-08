from fabric.api import *
from bh.utils import _upload_template, setup_env_for_user, save_password


@task
def passwd(newpassword):
    run(r'echo $USER:%s | chpasswd' % newpassword)
    env.passwords[env.host] = newpassword
    save_password('AAAAAAAA.json')

@task
def init_home_env(base_port):
    """ initalize remote admin home directory
    """
    setup_env_for_user()
    env.http_port = base_port
    run('mkdir -p ~/{bin,etc,var/run,var/www/media,var/www/static,logs/pasport,tmp,/etc/httpd/conf}')

    _upload_template("home/bashrc", "%(base)s/.bashrc")
    _upload_template("home/bash_profile", "%(base)s/.bash_profile")
    _upload_template("home/django_bash_completion", "%(base)s/.django_bash_completion")
#    _upload_template("httpd.conf", "%(base)s/etc/httpd/conf/httpd.conf")
    bin_utils(env.http_port)


@task(alias='bin')
def bin_utils(port=None):
    """copy user utilities to $HOME/bin directory"""

    if port is None:
        setup_env_for_user()
        env.http_port = run('echo $HTTP_LISTEN_PORT')
    _upload_template("bin/activate", "%(base)s/bin/activate")

    run('chmod ug+x %(base)s/bin/*' % env)



