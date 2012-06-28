from fabric.api import *
from fabric.contrib.files import contains, upload_template, sed, exists
#from root import *
from user import setup_env_for_user

from fabfile import usudo, _bool
from fabric.colors import green, red
import os


@task
def install():
    run('pip install buildbot buildbot-slave')
    with cd('~'):
        run('buildbot create-master master')
        run('mv master/master.cfg.sample master/master.cfg')
#        run('buildslave create-slave slave localhost:9989 example-slave pass')
