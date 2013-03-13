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
    run('mkdir -p ~/{bin,etc,.ssh,var/run,var/www/media,var/www/static,logs,tmp,/etc/httpd/conf}')

    _upload_template("home/bashrc", "%(base)s/.bashrc")
    _upload_template("home/bash_profile", "%(base)s/.bash_profile")
    _upload_template("home/django_bash_completion", "%(base)s/.django_bash_completion")
#    _upload_template("httpd.conf", "%(base)s/etc/httpd/conf/httpd.conf")
    bin_utils(env.http_port)
    chown()

@task(alias='bin')
def bin_utils(port=None):
    """copy user utilities to $HOME/bin directory"""

    if port is None:
        setup_env_for_user()
        env.http_port = run('echo $HTTP_LISTEN_PORT')
    _upload_template("bin/activate", "%(base)s/bin/activate")

    run('chmod ug+x %(base)s/bin/*' % env)

@task
def ssh():
    run('ssh-keygen -N "" -t rsa -f ~/.ssh/id_rsa.pub')
    local('ssh-copy-id -i ~/.ssh/id_rsa.pub %(user)s@%(host)s' % env)

@task
def fixssh():
    run('chmod 700 ~/.ssh')
    run('chmod 600 ~/.ssh/id*')
    run('chmod 644 ~/.ssh/*.pub')
    run('chmod go-w . ~/.ssh ~/.ssh/authorized_keys')


@task
def chown():
    """ setup right permission on the install dir
    """
    setup_env_for_user()
    # run('chown -R :%(group)s %(PREFIX)s' % env)
    # run('chmod g+rwx %(PREFIX)s' % env)

    run('chown -R %(admin)s:%(group)s %(admin_home_dir)s' % env)
    run('chmod -R ug+rwx %(admin_home_dir)s ' % env)
