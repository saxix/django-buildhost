import crypt
from fabric.api import *
from fabric.contrib.files import contains, upload_template, exists, sed
import re
from utils import setup_env_for_user
import os

#TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'tpls', 'profiles')


@task
def init_env():
    """ create common artifacts on the target host

        - create pip cache directory
        - copy source tarballs
        - create 'pasport' group
        - install all required libraries/sources

    """
#    print 11111,  contains("/etc/group", r"^%(group)s:" % env, escape=False )
#    print r"^%(group)s:x" % env

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
def create_user(admin, password='123'):
    """ create a user

    """

    if not contains("/etc/passwd", "^%s:" % admin):
        sudo('useradd -g pasport %s -M -g pasport' % admin)
    else:
        out = sudo('groups %s' % admin)
        assert re.search(r"\%(group)s\b" % env, out) # check the user in pasport group

    setup_env_for_user(admin)

    with settings(pwd=crypt.crypt(password, ".sax/")):
        sudo('mkdir %(admin_home_dir)s' % env)
        sudo('touch %(admin_home_dir)s/.scout' % env)
        sudo('usermod -p "%(pwd)s" -d %(admin_home_dir)s -m -s /bin/bash %(admin)s' % env)
    chown()

@task
def reset_user(admin, password='123'):
    """ reinitialize user environment
    """
    setup_env_for_user(admin)
    with settings(pwd=crypt.crypt(password, ".sax/")):
        sudo('usermod -p "%(pwd)s" -d %(admin_home_dir)s -s /bin/bash %(admin)s' % env)
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


def ubuntu_prereq():
    reqs = ['gcc', 'build-essential', 'libaio-dev', 'libxml2-dev', 'libxslt1-dev', 'libsqlite-dev', 'curl', 'sqlite3',
            'libssl-dev', 'libcurl4-openssl-dev', 'libsqlite3-dev', 'postgresql-server-dev-9.1']
    with settings(reqs=" ".join(reqs)):
        sudo('apt-get -y --force-yes install %(reqs)s' % env)


def redhat_prereq():
    """ install redhat/centos packages required to compile """
    reqs = ['autoconf', 'bzip2-devel', 'db4-devel', 'expat-devel', 'findutils', 'gcc-c++', 'gdbm-devel', 'glibc-devel',
            'gmp-devel', 'libGL-devel', 'libX11-devel', 'libtermcap-devel', 'ncurses-devel', 'openssl-devel',
            'pkgconfig', 'readline-devel', 'sqlite-devel', 'tar', 'tix-devel', 'tk-devel', 'zlib-devel', 'rpm-build',
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
    upload_template("all_env_command.sh", "%(PREFIX)s/sbin/all_env_command.sh" % env, env, use_jinja=True, template_dir=TEMPLATE_DIR)
    upload_template("pending_records.sh", "%(PREFIX)s/sbin/pending_records.sh" % env, env, use_jinja=True,template_dir=TEMPLATE_DIR)
    upload_template("payroll.sh", "%(PREFIX)s/sbin/payroll.sh" % env, env, use_jinja=True, template_dir=TEMPLATE_DIR)
    run('chmod ugo+x-rw %(PREFIX)s/sbin' % env)
    run('chmod ugo-rw,o-rw+x %(PREFIX)s/sbin/*' % env)




