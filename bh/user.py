from fabric.api import *
from fabfile import _upload_template
from fabfile import setup_env_for_user

@task
def init_home_env(base_port):
    """ initalize remote admin home directory
    """
    setup_env_for_user()
    env.http_port = base_port
    run('mkdir -p ~/{bin,etc,var/run,var/www/media,var/www/static,logs/pasport,tmp,/etc/httpd/conf}')

    _upload_template("bashrc", "%(base)s/.bashrc")
    _upload_template("bash_profile", "%(base)s/.bash_profile")
    _upload_template("django_bash_completion", "%(base)s/.django_bash_completion")
    _upload_template("httpd.conf", "%(base)s/etc/httpd/conf/httpd.conf")
    bin_utils(env.http_port)


#@task
#def reset_home_env():
#    setup_env_for_user()
#    old_port = run('echo $HTTP_LISTEN_PORT')
#    run('rm -fr ~/*')
#    init_home_env(old_port)


@task(alias='bin')
def bin_utils(port=None):
    """copy user utilities to $HOME/bin directory"""

    if port is None:
        setup_env_for_user()
        env.http_port = run('echo $HTTP_LISTEN_PORT')
    _upload_template("bin/activate", "%(base)s/bin/activate")

    run('chmod +x %(base)s/bin/*.*' % env)



