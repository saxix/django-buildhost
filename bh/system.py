from fabric.api import *
from fabric.colors import green, red
from fabric.contrib.files import upload_template, exists, sed
from bh.utils import as_bool, get_env
from bh.user import setup_env_for_user


@task
def python():
    """ compile and install python
    """
    setup_env_for_user(env.user)
    with cd(env.build):
        if not exists('Python-%(PYTHON)s.tgz' % env):
            run('wget http://www.python.org/ftp/python/2.7.3/Python-%(PYTHON)s.tgz' % env)

    version = env.PYTHON.replace('Python-', '')
    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.build):
        run('tar -xzf Python-%(PYTHON)s.tgz' % env)
        with cd('Python-%(PYTHON)s' % env):
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

    run('wget http://python-distribute.org/distribute_setup.py')
    run('python distribute_setup.py')
    run('easy_install -U pip')
    run('pip install ipython')


@task
def apache():
    """ compile and install apache
    """
    setup_env_for_user(env.user)
    with cd('%(packages_cache)s' % env):
        if not exists('%(APACHE)s.tar.gz' % env):
            run('wget http://mirrors.issp.co.th/apache//httpd/%(APACHE)s.tar.gz' % env)

    run('mkdir -p %(admin_home_dir)s/~build' % env)
    run('mkdir -p %(admin_home_dir)s/etc/httpd/conf.d' % env)
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
                ' --enable-headers'\
                ' --with-included-apr'\
                ' --enable-ssl'
                % env)
            run('make clean')
            run('make')
            run('make install')


@task
def sqlite():
    setup_env_for_user(env.user)

    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.build):
        if not exists('%(SQLITE)s.tar.gz' % env):
            run('wget http://fossies.org/unix/misc/%(SQLITE)s.tar.gz' % env)

    with cd(env.build):
        run('tar -xzf %(SQLITE)s.tar.gz' % env)
        run('ls -al')
        with cd(env.SQLITE):
            run('./configure '\
                ' --prefix=%(base)s'\
                ' --exec_prefix=%(base)s'\
                ' --bindir=%(base)s/bin'\
                ' --sbindir=%(base)s/bin' % env)
            run('make')
            run('make install')
            run('sqlite3 -version')


@task
def uwsgi():
    """ compile and install uwsgi
    """
    setup_env_for_user(env.user)
    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.build):
        if not exists('%(UWSGI)s.tar.gz' % env):
            run("wget http://projects.unbit.it/downloads/%(UWSGI)s.tar.gz" % env)
        run('tar -xzf %(UWSGI)s.tar.gz' % env)
        with cd(env.UWSGI):
            run('python uwsgiconfig.py --build' % env)
            run("cp uwsgi %(base)s/bin/uwsgi" % env)


@task
def modwsgi():
    """ compile and install modwsgi
    """
    setup_env_for_user(env.user)
    with cd('%(packages_cache)s' % env):
        if not exists('%(MOD_WSGI)s.tar.gz' % env):
            put('%(tarball_dir)s/%(MOD_WSGI)s.tar.gz' % env, env.packages_cache)
        #            run('wget http://mirrors.issp.co.th/apache//httpd/%(APACHE)s.tar.gz' % env)

    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.build):
        run('tar xvfz %(packages_cache)s/%(MOD_WSGI)s.tar.gz' % env)
        with cd(env.MOD_WSGI):
            run('./configure --with-apxs=%(base)s/bin/apxs --with-python=%(base)s/bin/python' % env)
            run('make clean')
            run('make')
            run('make install')


@task
def sqlplus():
    setup_env_for_user(env.user)
    with cd('%(packages_cache)s' % env):
        with settings(warn_only=True):
            arch = run('uname -i')
            if arch == 'x86_64':
                c = run('find %(packages_cache)s -name "instantclient*86-64*"' % env)
            elif arch == 'i386':
                run('find %(packages_cache)s -name "instantclient*" -not -name "*86-64*"' % env)
        if not 'instantclient' in c:
            put('%(tarball_dir)s/instantclient-*' % env, env.packages_cache)

    run('rm -fr ~/~build/sqlplus')
    run('mkdir -p ~/~build/sqlplus')
    with cd('~/~build/sqlplus'):
        with cd(env.base):
            with cd('oracle'):
                # run('cp -f instantclient_11_2/* ~/oracle/instantclient_11_2/')
                run('mv ~/oracle/instantclient_11_2/sqlplus ~/bin/sqlplus')
    run('sqlplus  -V') # simple check


@task
def oracle():
    """ compile and install oracle drivers
    """
    setup_env_for_user(env.user)
    with cd('%(packages_cache)s' % env):
        with settings(warn_only=True):
            arch = run('uname -i')
            if arch == 'x86_64':
                c = run('find %(packages_cache)s -name "instantclient*86-64*"' % env)
            elif arch == 'i386':
                run('find %(packages_cache)s -name "instantclient*" -not -name "*86-64*"' % env)
        if not 'instantclient' in c:
            put('%(tarball_dir)s/instantclient-*' % env, env.packages_cache)

    run('mkdir -p %(admin_home_dir)s/~build' % env)
    with cd(env.base):
        run('rm -fr oracle*')
        run('mkdir -p oracle')
        with cd('oracle'):
            if arch == 'x86_64':
                run('find %(packages_cache)s -name "instantclient*86-64*" -exec unzip "{}" \;' % env)
            elif arch == 'i386':
                run('find %(packages_cache)s -name "instantclient*" -not -name "*86-64*" -exec unzip "{}" \;' % env)
            with cd('instantclient_*'):
                env.oracle_home = '%(base)s/oracle/instantclient_11_2' % env
                run('ln -sf libclntsh.so.11.1 libclntsh.so')

    assert exists('%(oracle_home)s/libclntsh.so' % env)
    run('pip install cx_Oracle')
    run('mkdir -p ~/logs/oracle')
    run('ln -s ~/logs/oracle %(base)s/oracle/instantclient_11_2/log' % env)
    # test
    out = run('python -c "import cx_Oracle;print(222)"')
    assert out.startswith("222")


@task
def ngnix():
    """ compile and install nginx
    """
    setup_env_for_user()
    run('mkdir -p %(build)s' % env)
    with cd(env.build):
        if not exists('%(NGINX)s.tar.gz' % env):
            run("wget http://nginx.org/download/%(NGINX)s.tar.gz" % env)
        if not exists('pcre-%(PCRE)s.tar.gz' % env):
            run("wget http://sourceforge.net/projects/pcre/files/pcre/%(PCRE)s/pcre-%(PCRE)s.tar.gz" % env)
        if not exists('%(UWSGI)s.tar.gz' % env):
            run("wget http://projects.unbit.it/downloads/%(UWSGI)s.tar.gz" % env)

    with cd(env.build):
        run("tar -xzf %(NGINX)s.tar.gz" % env)
        run("tar -xzf pcre-%(PCRE)s.tar.gz" % env)
        run("tar -xzf %(UWSGI)s.tar.gz" % env)
        with settings(prefix="%s/opt/ngnix" % env.base):
            with cd(env.NGINX):
                run("mkdir -p %(prefix)s/tmp" % env)
                run("./configure --prefix=%(prefix)s"
                    " --sbin-path=%(prefix)s/ngnix"
                    " --pid-path=%(prefix)s/run/ngnix.pid"
                    " --lock-path=%(prefix)s/run/ngnix.lck"
                    #                    " --user=ngnix"
                    " --group=%(group)s"
                    " --with-debug "
                    " --with-select_module"
                    " --with-http_ssl_module"
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
                    " --http-proxy-temp-path=%(prefix)s/tmp/proxy/"\
                    " --http-client-body-temp-path=%(prefix)s/tmp/client/"\
                    " --http-fastcgi-temp-path=%(prefix)s/tmp/fcgi/"\
                    " --http-uwsgi-temp-path=%(prefix)s/tmp/uwsgi/"\
                    " --http-scgi-temp-path=%(prefix)s/tmp/scgi/"\
                    " --http-log-path=%(prefix)s/logs/ngnix/access.log"\
                    " --error-log-path=%(prefix)s/logs/ngnix/error.log"\
                    " --with-pcre=../pcre-%(PCRE)s" % env
                )
                run("make")
                run("make install")

            path = run('echo $PATH')
            if env.prefix not in path:
                sed('~/.bashrc',
                    'export PATH=(.*)',
                    r'export PATH=\1:%(prefix)s' % env)


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
def openldap():
    setup_env_for_user(env.user)
    run('mkdir -p %(build)s' % env)

    with cd(env.build):
        if not exists('openldap-%(OPENLDAP)s.tgz' % env):
            run("wget ftp://ftp.openldap.org/pub/OpenLDAP/openldap-release/openldap-%(OPENLDAP)s.tgz" % env)
        if not exists('db-%(BERKELEY)s.tar.gz' % env):
            run('wget http://download.oracle.com/berkeley-db/db-%(BERKELEY)s.tar.gz' % env)
        if not exists('python-ldap-%(PYTHONLDAP)s.tar.gz' % env):
            run('wget http://pypi.python.org/packages/source/p/python-ldap/python-ldap-%(PYTHONLDAP)s.tar.gz' % env)
        if not exists('cyrus-sasl-%(SASL)s.tar.gz' % env):
            run('wget http://ftp.andrew.cmu.edu/pub/cyrus-mail/cyrus-sasl-%(SASL)s.tar.gz' % env)

        if not exists('libtool-%(LIBTOOL)s.tar.gz' % env):
            run('wget http://ftp.gnu.org/gnu/libtool/libtool-%(LIBTOOL)s.tar.gz' % env)

    with cd(env.build):
        run("tar -xzf db-%(BERKELEY)s.tar.gz" % env)
        with cd('db-%(BERKELEY)s/build_unix/' % env):
            run('../dist/configure --prefix=%(base)s/dbd' % env)
            run('make')
            run('make install')

        run("tar -xzf cyrus-sasl-%(SASL)s.tar.gz" % env)
        with cd('cyrus-sasl-%(SASL)s' % env):
            run('./configure --prefix=%(base)s/ --sysconfdir=%(base)s/etc --with-saslauthd=%(base)s/var/run/saslauthd'
                '--with-dbpath=%(base)s/var/lib/sasl/sasldb2' % env)
            run('make')
            run('make install')
        run("tar -xzf libtool-%(LIBTOOL)s.tar.gz" % env)
        with cd('libtool-%(LIBTOOL)s' % env):
            run('./configure --prefix=%(base)s' % env)
            run('make')
            run('make check')
            run('make install')
        run("tar -xzf openldap-%(OPENLDAP)s.tgz" % env)
        with prefix(
            'export CPPFLAGS="-I%(base)s/dbd/include -I";export LDFLAGS="-L%(base)s/dbd/lib -R%(base)s/dbd/lib"' % env):
            with prefix(
                'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:%(base)s/~build/db-%(BERKELEY)s/build_unix/.libs:%(base)s/dbd/lib' % env):
                with cd('openldap-%(OPENLDAP)s' % env):
                    run('env | sort')
                    run('./configure --prefix=%(base)s '
                        '--sysconfdir=%(base)s/etc '
                        '--localstatedir=%(base)s/var '
                        '--libexecdir=%(base)s/usr/lib '
                        '--disable-static '
                        '--disable-debug '
                        '--enable-dynamic '
                        '--enable-crypt '
                        '--enable-modules '
                        '--enable-rlookups '
                        '--enable-backends=mod '
                        '--enable-overlays=mod '
                        '--disable-ndb '
                        '--disable-sql ' % env)
                    run('make depend')
                    run('make')
                    run('make install')

                run("tar -xzf python-ldap-%(PYTHONLDAP)s.tar.gz" % env)
                with cd('python-ldap-%(PYTHONLDAP)s' % env):
                    run('cat setup.cfg')
                    sed('setup.cfg', '^library_dirs.*', 'library_dirs=%(base)s/dbd/lib' % env)
                    sed('setup.cfg', '^include_dirs.*', 'include_dirs=%(base)s/dbd/include' % env)
                    run('python setup.py install')


@task
def odbc():
    setup_env_for_user(env.user)
    run('mkdir -p %(build)s' % env)
    with cd(env.build):
        if not exists('unixODBC-%(unixODBC)s.tar.gz' % env):
            run('wget ftp://ftp.unixodbc.org/pub/unixODBC/unixODBC-%(unixODBC)s.tar.gz' % env)
        run('tar -xzf unixODBC*.tar.gz ')
        with cd('unixODBC-%(unixODBC)s' % env):
            run('./configure '
                '--prefix=%(base)s/opt/odbc' % env)
            run('make')
            run('make install')
        with cd('%(base)s/opt/odbc/lib' % env):
            run('ln -fs libodbc.so libodbc.so.1')
            run('ln -fs libodbcinst.so libodbcinst.so.1')

        ldl = run('echo $LD_LIBRARY_PATH')
        if '%(base)s/opt/odbc/lib' % env not in ldl:
            sed('~/.bashrc',
                'export LD_LIBRARY_PATH=(.*)',
                r'export LD_LIBRARY_PATH=\1:$HOME/opt/odbc/lib')


@task
def psqlodbc():
    setup_env_for_user(env.user)
    with cd(env.build):
        if not exists('psqlodbc-%(PSQLODBC)s.tar.gz' % env):
            run('wget http://ftp.postgresql.org/pub/odbc/versions/src/psqlodbc-%(PSQLODBC)s.tar.gz' % env)
        run('tar -xzf psqlodbc-*.tar.gz ')

        ldl = run('echo $LD_LIBRARY_PATH')

        if '%(base)s/opt/odbc/lib' % env not in ldl:
            sed('~/.bashrc',
                'export LD_LIBRARY_PATH=(.*)',
                r'export LD_LIBRARY_PATH=\1:$HOME/opt/odbc/lib')

        if '$HOME/pgsql/lib' % env not in ldl:
            sed('~/.bashrc',
                'export LD_LIBRARY_PATH=(.*)',
                r'export LD_LIBRARY_PATH=\1:$HOME/pgsql/lib' % env)

        path = run('echo $PATH')
        if r':$HOME/opt/odbc/bin' not in path:
            sed('~/.bashrc',
                'export PATH=(.*)',
                r'export PATH=\1:$HOME/opt/odbc/bin')

        with prefix('source ~/.bashrc'):
            with cd('psqlodbc-%(PSQLODBC)s' % env):
                run('./configure '
                    ' --prefix=%(base)s/opt/psqlodbc'
                    ' --with-libpq=%(base)s/pgsql'
                    ' --with-unixodbc=%(base)s/opt/odbc'
                    ' --enable-pthreads'
                    % env)
                run('make')
                run('make install')

        ldl = run('echo $LD_LIBRARY_PATH')
        if ':$HOME/opt/psqlodbc/lib' % env not in ldl:
            sed('~/.bashrc',
                'export LD_LIBRARY_PATH=(.*)',
                r'export LD_LIBRARY_PATH=\1:$HOME/opt/psqlodbc/lib' % env)


@task
def postgresql(port=5432):
    setup_env_for_user(env.user)
    run('mkdir -p %(build)s' % env)
    if exists('%(base)s/pgsql' % env):
        with settings(warn_only=True):
            run('~/pgsql/bin/pg_ctl stop -W -D ~/data/')
        with settings(warn_only=True):
            run('rm -fr ~/pgsql')

    with cd(env.build):
        if not exists('postgresql-%(POSTGRES)s.tar.bz2' % env):
            run('wget http://ftp.postgresql.org/pub/source/v%(POSTGRES)s/postgresql-%(POSTGRES)s.tar.bz2' % env)
        run('tar -xf postgresql-%(POSTGRES)s.tar.bz2' % env)

        with cd('postgresql-%(POSTGRES)s' % env):
            with settings(pgport=port):
                run('./configure '
                    '--with-iodbc '
                    '--enable-pthreads '
                    '--with-pgport=%(pgport)s '
                    '--prefix=%(base)s/pgsql' % env)
            run('make')
            run('make world')
            run('make install')
            run('make install-world')
    sed('~/.bashrc', '^export PATH=(.*)', r'export PATH=$HOME/pgsql/bin:\1' % env)

    if not exists('~/data'):
        run('~/pgsql/bin/initdb -D ~/data')

    sed('~/data/postgresql.conf', '#*port.*', r'port=%s' % port)
    #    sed('~/data/postgresql.conf', '#*listen_addresses.*', r"listen_addresses='*'")
    # run('~/pgsql/bin/postmaster --config-file=data/postgresql.conf -D ~/data')
    run('cp ~/pgsql/share/pg_hba.conf.sample  ~/data/pg_hba.conf')
    sed('~/data/pg_hba.conf', '@remove-line-for-nolocal@(.*)', r'\1')
    sed('~/data/pg_hba.conf', '@authmethod@', r'password')
    sed('~/data/pg_hba.conf', '@authmethodlocal@', r'ident')

    sed('~/data/pg_hba.conf', '@authcomment@', '')

    with settings(warn_only=True):
        run('~/pgsql/bin/initdb -D ~/data')

    run('cp ~/pgsql/share/pg_service.conf.sample ~/data/pg_service.conf')
    run('cp ~/pgsql/share/pg_ident.conf.sample ~/data/pg_ident.conf')
#    run('~/pgsql/bin/pg_ctl start -W -D ~/data/ -l ~/data/logfile.log')

    ldl = run('echo $LD_LIBRARY_PATH')
    if '$HOME/pgsql/lib' % env not in ldl:
        sed('~/.bashrc',
            'export LD_LIBRARY_PATH=(.*)',
            r'export LD_LIBRARY_PATH=\1:$HOME/pgsql/lib' % env)

    path = run('echo $PATH')
    if r':$HOME/pgsql/bin' not in path:
        sed('~/.bashrc',
            'export PATH=(.*)',
            r'export PATH=\1:$HOME/pgsql/bin')


@task
def clean():
    setup_env_for_user(env.user)
    run('rm -fr %(build)s' % env)


@task
def base():
    setup_env_for_user(env.user)
    execute(sqlite)
    execute(postgresql)
    execute(python)
    execute(uwsgi)
    execute(ngnix)


# @task
# def all():
#     """ install all required servers/appliance
#
#     this command
#     """
#     setup_env_for_user(env.user)
#
#     execute(sqlite)
#     execute(odbc)
#     execute(postgresql, port=int(get_env('HTTP_LISTEN_PORT')) + 1000)
#     # execute(psqlodbc)
#     execute(python)
#
#     execute(oracle)
#     # execute(sqlplus)
#
#     # execute(openldap)
#
#     execute(uwsgi)
#     execute(ngnix)
#
#     execute(apache)
#     execute(modwsgi)
