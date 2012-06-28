import json
from fabric.api import *
import os
from fabric.contrib.files import exists, upload_template
get_home_dir = lambda username: os.path.join(env.PREFIX, username)

def load_password(filename='~/.credentials.json'):
    try:
        env.passwords = json.load(open(os.path.expanduser(filename), 'r'))
    except IOError:
        pass

def init():
    env.packages_cache = "%s/packages_cache" % env.PREFIX
    env.pip_cache = "%s/pip_download_cache" % env.PREFIX

def usudo(command, shell=True, pty=True, combine_stderr=None, user=None):
    user = user or env.admin
    return sudo(command, shell, pty, combine_stderr, user)


def _bool(value, default):
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

