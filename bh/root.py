import crypt
import re
import os
from fabric.api import *
from fabric.contrib.files import contains, exists
from bh.utils import _upload_template, setup_env_for_user

@task
def du():
    run('for x in `ls %(PREFIX)s`;do test -e "%(PREFIX)s/$x/.bashrc" && du -sh %(PREFIX)s/$x; done' % env)
    run('df -h')

@task
def clear():
    run('for x in `ls %(PREFIX)s`;do test -e "%(PREFIX)s/$x/.bashrc" && rm -fr %(PREFIX)s/$x/logs/* %(PREFIX)s/$x/~*; done' % env)

@task
def allenv(cmd):
    with settings(xcmd=cmd):
        print('%(PREFIX)s/sbin/all_env_shell.sh %(xcmd)s' % env)

@task
def allenv(cmd):
    with settings(xcmd=cmd):
        print('%(PREFIX)s/sbin/all_env_shell.sh %(xcmd)s' % env)

@task
def init_env():
    """ create common artifacts on the target host

        - create pip cache directory
        - copy source tarballs
        - create 'pasport' group
        - install all required libraries/sources

    """
    if not contains("/etc/group", r"^%(group)s:x" % env, escape=False ):
        sudo('groupadd %(group)s' % env)

    sudo('mkdir -p %(pip_cache)s' % env)
    sudo('mkdir -p %(packages_cache)s' % env)
    sudo('mkdir -p %(PREFIX)s/sbin' % env)

    sudo('chown %(user)s:%(group)s %(PREFIX)s' % env)
    sudo('chown %(user)s:%(group)s %(packages_cache)s' % env)
    sudo('chown %(user)s:%(group)s %(pip_cache)s' % env)

    sudo('chmod g+rw,o-rw %(PREFIX)s' % env)
    sudo('chmod g+rw,o-rw %(pip_cache)s' % env)
    sudo('chmod g+rw,o-rw %(packages_cache)s' % env)

    copy_packages()
    install_libraries()
    upload_common_task()


@task
def install_libraries():
    """ install OS specific package via apt-get or yum
    """
    if exists('/etc/redhat-release'):
        redhat_prereq()
    else:
        ubuntu_prereq()

@task
def list_instances():
    """ list available pasport instances
    """
    run('for x in `ls %(PREFIX)s`;do test -e "%(PREFIX)s/$x/.bashrc" && echo $x; done' % env)

@task
def reset_host():
    """ remove ALL artifacts/instances ad users
    """
    out = sudo('ls -ld %(PREFIX)s' % env)
    perms, _, owner, group, _, _, _, _, name = out.split()
    if (group != env.group) or not 'pasport' in name: # simple check to avoi mistakes
        print "Error"
        return
    sudo('getent group pasport')
    #sudo('rm -fr %(PREFIX)s/*' % env)

@task
def user_create(admin, password='123'):
    """ create a user

    """

    if not contains("/etc/passwd", "^%s:" % admin):
        with settings(admin=admin):
            sudo('useradd -g %(group)s %(admin)s -M -g %(group)s' % env )
    else:
        out = sudo('groups %s' % admin)
        assert re.search(r"\%(group)s\b" % env, out) # check the user in pasport group

    setup_env_for_user(admin)
    user_setup( admin, password )

@task
def user_remove(admin):
    """ create a user

    """
    setup_env_for_user(admin)
    run('userdel %s' % admin)
    run('rm -fr %(admin_home_dir)s' % env)

@task
def user_setup(admin, password='123'):
    """ reinitialize user environment homedir and password
    """
    setup_env_for_user(admin)
    with settings(pwd=crypt.crypt(password, ".sax/")):
        sudo('mkdir -p %(admin_home_dir)s' % env)
        sudo('touch %(admin_home_dir)s/.scout' % env)
        sudo('usermod -p "%(pwd)s" -g %(group)s -d %(admin_home_dir)s -s /bin/bash %(admin)s' % env)
    sudo('touch %(admin_home_dir)s/.scout' % env)
    chown()


def chown():
    """ setup right permission on the install dir
    """
    require('admin', provided_by=setup_env_for_user)
    sudo('chown -R :%(group)s %(PREFIX)s' % env)
    sudo('chmod g+rwx %(PREFIX)s' % env)

    sudo('chown -R %(admin)s:%(group)s %(base)s' % env)
    sudo('chmod -R ug+rwx %(base)s ' % env)
    sudo('chmod g+rw,o-rw %(PREFIX)s' % env)
    sudo('chmod g+rw,o-rw %(pip_cache)s' % env)
    sudo('chmod g+rw,o-rw %(packages_cache)s' % env)


def ubuntu_prereq():
    reqs = ['gcc', 'build-essential', 'libaio-dev', 'libxml2-dev', 'libxslt1-dev',
            'curl', 'libssl-dev', 'libcurl4-openssl-dev', 'postgresql-server-dev-9.1']
    with settings(reqs=" ".join(reqs)):
        sudo('apt-get -y --force-yes install %(reqs)s' % env)


def redhat_prereq():
    """ install redhat/centos packages required to compile """
    reqs = ['autoconf', 'bzip2-devel', 'db4-devel', 'expat-devel', 'findutils', 'gcc-c++', 'gdbm-devel', 'glibc-devel',
            'gmp-devel', 'libGL-devel', 'libX11-devel', 'libtermcap-devel', 'ncurses-devel', 'openssl-devel',
            'pkgconfig', 'readline-devel', 'tar', 'tix-devel', 'tk-devel', 'zlib-devel', 'rpm-build',
            'make', 'libxml2-devel', 'curl', 'libxslt-devel', 'postgresql-libs']
    with settings(reqs=" ".join(reqs)):
        sudo('yum -y install %(reqs)s' % env)


def _redhat_prereq():
    sudo('yum remove gcc cpp kernel-headers glibc-headers glibc-devel libreadline5-dev')


@task
def copy_packages():
    """ copy local source code tarball to remote machine
    """
#    for source, dest in [(env.local_tarball , env.packages_cache), ('pip_cache', env.pip_cache)]:
    if not exists(env.packages_cache):
        run('mkdir -p %(packages_cache)s' % env)

    for source, dest in [(env.local_tarball , env.packages_cache), ]:
        with lcd(source):
            packages = local('ls *', True)
            for p in packages.split('\n'):
                target = '%s/%s' % (dest, p)
                if not exists(target):
                    with settings(p=os.path.abspath("%s/%s" % (source, p)), dest=dest):
                        local('scp %(p)s %(user)s@%(host)s:%(dest)s/' % env)



@task
def upload_common_task():
    _upload_template("sbin/all_env_command.sh", "%(PREFIX)s/sbin/all_env_command.sh" % env)
    _upload_template("sbin/cronhandler.sh", "%(PREFIX)s/sbin/cronhandler.sh" % env)
    run('chmod ugo+x-rw %(PREFIX)s/sbin' % env)
    run('chmod ugo-rw,o-rw+x %(PREFIX)s/sbin/*' % env)




