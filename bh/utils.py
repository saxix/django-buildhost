import json
from fabric.api import *
import os
from fabric.contrib.files import exists, upload_template
import sys
PASSWORD_FILE='~/.credentials.json'

get_home_dir = lambda username: os.path.join(env.PREFIX, username)

def load_password(filename=PASSWORD_FILE):
    try:
        env.passwords = json.load(open(os.path.expanduser(filename), 'r'))
    except IOError:
        pass

def save_password(filename=PASSWORD_FILE):
    try:
        json.dump(env.passwords, open(os.path.expanduser(filename), 'w'), indent=3)
    except IOError:
        pass

def init():
    env.packages_cache = "%s/packages_cache" % env.PREFIX
    env.pip_cache = "%s/pip_download_cache" % env.PREFIX
    env.template_dir = os.path.join(os.path.dirname(__file__), 'tpls')



def usudo(command, shell=True, pty=True, combine_stderr=None, user=None):
    user = user or env.admin
    return sudo(command, shell, pty, combine_stderr, user)


def as_bool(value, default):
    if value in (None, ''):
        return default
    if value in ('0', 'false', 'False', 'F', 'no', False, 0):
        return False
    elif value in ('1', 'true', 'True', 'T', 'yes', True, 1):
        return True
    else:
        return bool(value)

def _upload_template( name, dest, **kwargs ):
    upload_template(name % env, dest % env, env, use_jinja=True, template_dir=env.template_dir, **kwargs)


def setup_env_for_user(admin=None):
    """ setup enviroment for the selected admin.
    Must be called before each task.
    """
    admin = admin or env.user
    assert admin != 'root', "Cannot use root for this task"
    env.admin = admin
    env.admin_home_dir = get_home_dir(env.admin)
    env.base = env.admin_home_dir
    env.build = os.path.join(env.base, '~build')


def pip_install(pkg, upgrade=False, mask='"%s"'):
    up = upgrade and '--upgrade' or ''
    if isinstance(pkg, basestring):
        pkg = [pkg]
    pkgs = " ".join([mask % p for p in pkg])
    with settings(pkgs=pkgs, upgrade=up, alaska='http://wfpdevel:wfpdevel@alaska.k-tech.it/pypi/pasportng/'):
        run('pip install %(upgrade)s -f %(pypi)s -f %(alaska)s %(pkgs)s' % env)

def check_no_pending_commit(package, halt=True, forceto=''):
    package_dir = os.path.realpath(os.path.join(os.path.dirname(package.__file__)))
    product_dir = os.path.join(package_dir, os.pardir)
    if halt:
        exit_func=sys.exit
    else:
        exit_func = lambda x:x
    if os.path.isfile(os.path.join(product_dir, 'setup.py')):
        with lcd(product_dir):
            with hide('running', 'stdout', 'stderr'):
                if os.path.exists(os.path.join(product_dir, '.svn')):
                    r = local('svn status', True)
                    if r != "":
                        print 'Uncommitted files on ', product_dir
                        print r
                        exit_func(1)
                elif os.path.exists(os.path.join(product_dir, '.git')) or forceto=='git':
                    r = local('git status -s', True)
                    if r != "":
                        print 'Uncommitted files on ', product_dir
                        print r
                        exit_func(1)
                    r = local('git diff --stat origin/master', True)
                    if r != "":
                        print 'Pending commits to push ', product_dir
                        print r
                        exit_func(1)
                else:
                    print 'Error no valid SCM found'
                    sys.exit(1)

    else:
        raise Exception('Wrong directory tree for (%s)' % package)
    return package_dir, product_dir


@task
def help():
    """
        Steps to work with PASport console.

        PASport console is a set of scripts to install/update and manage multiple pasport installation.

        How to install in a new fresh system.

        $ fab -H root@targetsystem root.init_host root.create_user:admin,password
        $ fab -H admin@targetsystem user.init_home_env
        $ fab -H admin@targetsystem system.install
        $ fab -H admin@targetsystem pasport.configure:profile
        $ fab -H admin@targetsystem pasport.install:version

    """
    print help.__doc__

