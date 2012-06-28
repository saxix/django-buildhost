from fabric.api import *
from fabric.contrib.files import contains, upload_template, sed, exists
from user import setup_env_for_user

from fabfile import usudo, _bool
from fabric.colors import green, red
import os

@task
def python():
    """ compile and install python
    """
    setup_env_for_user(env.user)
    version = env.PYTHON.replace('Python-', '')
    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.build):
        run('tar -xzf %(packages_cache)s/%(PYTHON)s.tgz' % env)
        with cd(env.PYTHON):
            run('./configure --prefix=%(base)s --enable-shared --with-threads' % env)
            run('make clean')
            run('make')
            run('make install')

    # check local install
    out = run('python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"')
    assert out.startswith("%(base)s/" % env), 'Error: `%s` ' % out

    # checl ssl support
    out = run('python -c "import socket;print socket.ssl"')
    assert out.startswith("<function ssl at "), out

    run('python %(packages_cache)s/distribute_setup.py && easy_install pip' % env)
    run('rm -f %(base)s/distribute-*' % env)
    run('pip install ipython')

@task
def apache():
    """ compile and install apache
    """
    setup_env_for_user(env.user)

    run('mkdir -p %(admin_home_dir)s/~build' % env)
    run('mkdir -p %(admin_home_dir)s/etc/httpd/conf.d' % env )
    with cd(env.build):
        run('tar -xzf %(packages_cache)s/%(APACHE)s.tar.gz' % env)
        with cd(env.APACHE):
            run('./configure '\
                ' --prefix=%(base)s'\
                ' --exec_prefix=%(base)s'\
                ' --bindir=%(base)s/bin'\
                ' --sbindir=%(base)s/bin'\
                ' --libexecdir=%(base)s/lib/apache'\
                ' --mandir=%(base)s/man'\
                ' --sysconfdir=%(base)s/etc/httpd/conf'\
                ' --datadir=%(base)s/var/www'\
                ' --includedir=%(base)s/lib/include/apache'\
                ' --localstatedir=%(base)s/var/run'\
                ' --enable-rewrite'\
#                ' --enable-rewrite=shared'\
#                ' --enable-mods-shared=most'\
                ' --with-included-apr'\
                ' --enable-ssl'
                % env)
            run('make clean')
            run('make')
            run('make install')


@task
def uwsgi():
    """ compile and install uwsgi
    """
    setup_env_for_user(env.user)
    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.build):
        run('tar -xzf %(packages_cache)s/%(UWSGI)s.tar.gz' % env)
        with cd(env.UWSGI):
            run('python uwsgiconfig.py --build' % env)
            run("cp uwsgi %(base)s/bin/uwsgi" % env)


@task
def modwsgi():
    """ compile and install modwsgi
    """
    setup_env_for_user(env.user)
    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.build):
        run('tar xvfz %(packages_cache)s/%(MOD_WSGI)s.tar.gz' % env)
        with cd(env.MOD_WSGI):
            run('./configure --with-apxs=%(base)s/bin/apxs --with-python=%(base)s/bin/python' % env)
            run('make clean')
            run('make')
            run('make install')


@task
def oracle():
    """ compile and install oracle drivers
    """
    setup_env_for_user(env.user)
    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.base):
        run('rm -fr oracle*')
        run('mkdir -p oracle')
        with cd('oracle'):
            arch = run('uname -i')
            if arch == 'x86_64':
                run('find %(packages_cache)s -name "instantclient*86-64*" -exec unzip "{}" \;' % env)
            elif arch== 'i386':
                run('find %(packages_cache)s -name "instantclient*" -name "*86-64*" -exec unzip "{}" \;' % env)
            with cd('instantclient_*'):
                env.oracle_home = '%(base)s/oracle/instantclient_11_2' % env
                run('ln -sf libclntsh.so.11.1 libclntsh.so')

    assert exists('%(oracle_home)s/libclntsh.so' % env )
    run('pip install cx_Oracle')
    run('mkdir ~/logs/oracle')
    run('ln -s ~/logs/oracle %(base)s/oracle/instantclient_11_2/log' % env)
    # test
    out = run('python -c "import cx_Oracle;print(222)"')
    assert out.startswith("222")


@task
def ngnix(recover=False, configure=True, make=True, install=True):
    """ compile and install nginx
    """
    setup_env_for_user()
    _recover = _bool(recover, False)
    _configure = _bool(configure, True)
    _make = _bool(make, True)
    _install = _bool(install, True)
    with cd(env.build):
        if not _recover:
            run("tar -xzf %(packages_cache)s/%(NGINX)s.tar.gz" % env)
            run("tar -xzf %(packages_cache)s/pcre-%(PCRE)s.tar.gz" % env)
            run("tar -xzf %(packages_cache)s/%(UWSGI)s.tar.gz" % env)

        with cd(env.NGINX):
            if _configure:
                run("./configure --prefix=%(base)s"\
                    " --sbin-path=%(base)s/bin"\
                    " --pid-path=%(base)s/run/nginx.pid"\
                    " --lock-path=%(base)s/run/nginx.lck"\
                    " --user=nginx"\
                    " --group=%(group)s"\
                    " --with-debug "\
                    #                " --with-google_perftools_module"\
                    " --with-select_module"\
                    " --with-http_ssl_module"\
                    " --with-http_gzip_static_module"\
                    " --with-http_stub_status_module"\
                    " --with-http_realip_module"\
                    " --with-http_ssl_module"\
                    " --with-http_sub_module"\
                    " --with-http_addition_module"\
                    " --with-http_flv_module"\
                    " --with-http_addition_module"\
                    " --with-file-aio"\
                    " --with-sha1-asm"\
                    " --http-proxy-temp-path=%(base)s/tmp/proxy/"\
                    " --http-client-body-temp-path=%(base)s/tmp/client/"\
                    " --http-fastcgi-temp-path=%(base)s/tmp/fcgi/"\
                    " --http-uwsgi-temp-path=%(base)s/tmp/uwsgi/"\
                    " --http-scgi-temp-path=%(base)s/tmp/scgi/"\
                    " --http-log-path=%(base)s/logs/nginx/access.log"\
                    " --error-log-path=%(base)s/logs/nginx/error.log"\
                    " --with-pcre=../pcre-8.20" % env
                )
            if _make:
                run("make")
            if _install:
                run("make install")


@task
def check():
    """ check installation of the servers/appliance
    """
    setup_env_for_user()

    def _test(cmd, where):
        print 'Checking `%s`..' % cmd,
        with settings(warn_only=True):
            out = run(cmd)
            if out.startswith(where):
                print green('Ok')
            else:
                print red("FAIL!!"), out

    puts('Checking installation...')

    with hide('everything'):
        _test('which httpd', '%(base)s/bin/httpd' % env)
        _test('which nginx', '%(base)s/bin/nginx' % env)
        _test('which uwsgi', '%(base)s/bin/uwsgi' % env)
        _test('which python', '%(base)s/bin/python' % env)
        _test('which pip', '%(base)s/bin/pip' % env)

        _test('python -V', 'Python 2.7.2')
        _test('python -c "import cx_Oracle;print(\'cx_Oracle imported\')"', 'cx_Oracle imported')
        _test('python -c "import socket;print socket.ssl"', '<function ssl at')

        print 'Checking $PATH..',
        out = run('echo $PATH')
        assert out.startswith("%(base)s/bin:%(base)s/apache/bin" % env), out
        print green('Ok (%s)' % out)

@task
def copy_cmds():
    """ initalize remote admin home directory
    """
    upload_template("tpls/sbin/all_env_command.sh", "%(PREFIX)s/sbin" % env, env, use_jinja=True)
    run('chmod +x %(PREFIX)s/sbin/*.sh' % env)


@task
def install():
    """ install all required servers/appliance

    this command
    """
    setup_env_for_user(env.user)

    execute(python)
    execute(apache)
    execute(oracle)
    execute(modwsgi)
    execute(uwsgi)
    execute(ngnix)
