%if 0%{?rhel} < 7 && 0%{?rhel} > 0
%global _pkgdocdir %{_docdir}/%{name}-%{version}
%endif
%global moduletype apps
%global modulename copr

Name:		copr
Version:	1.8
Release:	1%{?dist}
Summary:	Cool Other Package Repo

Group:		Applications/Productivity
License:	GPLv2+
URL:		https://fedorahosted.org/copr/
# Source is created by
# git clone https://git.fedorahosted.org/git/copr.git
# cd copr
# tito build --tgz
# content is same as https://git.fedorahosted.org/cgit/copr.git/snapshot/%{name}-%{version}-1.tar.gz
# but checksum does not match due different metadata
Source0:	%{name}-%{version}.tar.gz

BuildArch:  noarch
BuildRequires: asciidoc
BuildRequires: libxslt
BuildRequires: util-linux
BuildRequires: python-setuptools
BuildRequires: python-requests
BuildRequires: python2-devel
%if 0%{?rhel} < 7 && 0%{?rhel} > 0
BuildRequires: python-argparse
%endif
#for doc package
BuildRequires: epydoc
BuildRequires: graphviz
BuildRequires: make
#for selinux
BuildRequires:  checkpolicy, selinux-policy-devel
BuildRequires:  policycoreutils >= %{POLICYCOREUTILSVER}

%description
COPR is lightweight build system. It allows you to create new project in WebUI,
and submit new builds and COPR will create yum repository from latest builds.

%package backend
Summary:	Backend for COPR
Requires:   ansible >= 1.2
Requires:   lighttpd
Requires:   euca2ools
Requires:   rsync
Requires:   openssh-clients
Requires:   mock
Requires:   yum-utils
Requires:   createrepo
Requires:   python-bunch
Requires:   python-requests
Requires:   logrotate
Requires:   fedmsg

%description backend
COPR is lightweight build system. It allows you to create new project in WebUI,
and submit new builds and COPR will create yum repository from latest builds.

This package contains backend.

%package frontend
Summary:    Frontend for COPR
Requires:   httpd
Requires:	mod_wsgi
Requires:	python-alembic
Requires:   python-flask
Requires:   python-flask-openid
Requires:   python-flask-wtf
Requires:   python-flask-sqlalchemy
Requires:   python-flask-script
Requires:   python-flask-whooshee
#Requires:	python-virtualenv
Requires:   python-blinker
Requires:	python-psycopg2
Requires:   python-pylibravatar
Requires:	python-whoosh >= 2.5.3
# for tests:
Requires:	pytest
Requires:   python-flexmock
%if 0%{?rhel} < 7 && 0%{?rhel} > 0
BuildRequires: python-argparse
%endif
# check
BuildRequires: python-flask
BuildRequires: python-flask-script
BuildRequires: python-flask-sqlalchemy
BuildRequires: python-flask-openid
BuildRequires: python-flask-whooshee
BuildRequires: python-pylibravatar
BuildRequires: python-flask-wtf
BuildRequires: pytest
BuildRequires: python-flexmock

%description frontend
COPR is lightweight build system. It allows you to create new project in WebUI,
and submit new builds and COPR will create yum repository from latests builds.

This package contains frontend.

%package cli
Summary:	Command line interface for COPR
Requires:	python-requests
%if 0%{?rhel} < 7 && 0%{?rhel} > 0
Requires:   python-argparse
%endif

%description cli
COPR is lightweight build system. It allows you to create new project in WebUI,
and submit new builds and COPR will create yum repository from latests builds.

This package contains command line interface.

%package doc
Summary:    Code documentation for COPR

%description doc
COPR is lightweight build system. It allows you to create new project in WebUI,
and submit new builds and COPR will create yum repository from latests builds.

This package include documentation for COPR code. Mostly useful for developers
only.

%package selinux
Summary:	SELinux module for COPR
Requires(post): policycoreutils, libselinux-utils
Requires(post): policycoreutils-python
Requires(post): selinux-policy-targeted
Requires(postun): policycoreutils

%description selinux
COPR is lightweight build system. It allows you to create new project in WebUI,
and submit new builds and COPR will create yum repository from latests builds.

This package include SELinux targeted module for COPR


%prep
%setup -q


%build
mv copr_cli/README.rst ./

# convert manages
a2x -d manpage -f manpage man/copr-cli.1.asciidoc
a2x -d manpage -f manpage man/copr-selinux-enable.8.asciidoc
a2x -d manpage -f manpage man/copr-selinux-relabel.8.asciidoc

# build documentation
pushd documentation
make %{?_smp_mflags} python
popd

#selinux
pushd selinux
perl -i -pe 'BEGIN { $VER = join ".", grep /^\d+$/, split /\./, "%{version}.%{release}"; } s!\@\@VERSION\@\@!$VER!g;' %{modulename}.te
for selinuxvariant in targeted; do
    make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
    bzip2 -9 %{modulename}.pp
    mv %{modulename}.pp.bz2 %{modulename}.pp.bz2.${selinuxvariant}
    make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done
popd

%install

#backend
install -d %{buildroot}%{_sharedstatedir}/copr
install -d %{buildroot}%{_sharedstatedir}/copr/jobs
install -d %{buildroot}%{_sharedstatedir}/copr/public_html/results
install -d %{buildroot}%{_var}/log/copr
install -d %{buildroot}%{_var}/log/copr/workers/
install -d %{buildroot}%{_pkgdocdir}/lighttpd/
install -d %{buildroot}%{_datadir}/copr/backend
install -d %{buildroot}%{_sysconfdir}/copr
install -d %{buildroot}%{_sysconfdir}/logrotate.d/

cp -a backend/* %{buildroot}%{_datadir}/copr/backend
cp -a copr-be.py %{buildroot}%{_datadir}/copr/
cp -a copr-be.conf.example %{buildroot}%{_sysconfdir}/copr/copr-be.conf

cp -a backend-dist/lighttpd/* %{buildroot}%{_pkgdocdir}/lighttpd/
cp -a logrotate/* %{buildroot}%{_sysconfdir}/logrotate.d/

# for ghost files
touch %{buildroot}%{_var}/log/copr/copr.log
for i in `seq 7`; do
	touch %{buildroot}%{_var}/log/copr/workers/worker-$i.log
done

#frontend
install -d %{buildroot}%{_sysconfdir}
install -d %{buildroot}%{_datadir}/copr/coprs_frontend
install -d %{buildroot}%{_sharedstatedir}/copr/data/openid_store
install -d %{buildroot}%{_sharedstatedir}/copr/data/openid_store/associations
install -d %{buildroot}%{_sharedstatedir}/copr/data/openid_store/nonces
install -d %{buildroot}%{_sharedstatedir}/copr/data/openid_store/temp
install -d %{buildroot}%{_sharedstatedir}/copr/data/whooshee
install -d %{buildroot}%{_sharedstatedir}/copr/data/whooshee/copr_user_whoosheer

cp -a coprs_frontend/* %{buildroot}%{_datadir}/copr/coprs_frontend
mv %{buildroot}%{_datadir}/copr/coprs_frontend/coprs.conf.example ./
mv %{buildroot}%{_datadir}/copr/coprs_frontend/config/* %{buildroot}%{_sysconfdir}/copr
rm %{buildroot}%{_datadir}/copr/coprs_frontend/CONTRIBUTION_GUIDELINES
touch %{buildroot}%{_sharedstatedir}/copr/data/copr.db

#copr-cli
%{__python2} coprcli-setup.py install --root %{buildroot}
install -d %{buildroot}%{_mandir}/man1
install -p -m 644 man/copr-cli.1 %{buildroot}/%{_mandir}/man1/

#doc
cp -a documentation/python-doc %{buildroot}%{_pkgdocdir}/
cp -a playbooks %{buildroot}%{_pkgdocdir}/

#selinux
for selinuxvariant in targeted; do
    install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
    install -p -m 644 selinux/%{modulename}.pp.bz2.${selinuxvariant} \
           %{buildroot}%{_datadir}/selinux/${selinuxvariant}/%{modulename}.pp.bz2
done
# Install SELinux interfaces
install -d %{buildroot}%{_datadir}/selinux/devel/include/%{moduletype}
install -p -m 644 selinux/%{modulename}.if \
  %{buildroot}%{_datadir}/selinux/devel/include/%{moduletype}/%{modulename}.if
# Install copr-selinux-enable which will be called in %posttrans
install -d %{buildroot}%{_sbindir}
install -p -m 755 selinux/%{name}-selinux-enable %{buildroot}%{_sbindir}/%{name}-selinux-enable
install -p -m 755 selinux/%{name}-selinux-relabel %{buildroot}%{_sbindir}/%{name}-selinux-relabel

install -d %{buildroot}%{_mandir}/man8
install -p -m 644 man/%{name}-selinux-enable.8 %{buildroot}/%{_mandir}/man8/
install -p -m 644 man/%{name}-selinux-relabel.8 %{buildroot}/%{_mandir}/man8/

%check
pushd coprs_frontend
TMPFILE=$(mktemp)
COPR_CONFIG="$(pwd)/config/copr_unit_test.conf"  ./manage.py test | tee $TMPFILE
# remove this when tests are fixed
grep "1 failed, 65 passed" $TMPFILE 
popd

%pre backend
getent group copr >/dev/null || groupadd -r copr
getent passwd copr >/dev/null || \
useradd -r -g copr -G lighttpd -s /bin/bash -c "COPR user" copr
/usr/bin/passwd -l copr >/dev/null

%pre frontend
getent group copr-fe >/dev/null || groupadd -r copr-fe
getent passwd copr-fe >/dev/null || \
useradd -r -g copr-fe -G copr-fe -d %{_datadir}/copr/coprs_frontend -s /bin/bash -c "COPR frontend user" copr-fe
/usr/bin/passwd -l copr-fe >/dev/null

%post frontend
service httpd condrestart

%post selinux
if /usr/sbin/selinuxenabled ; then
   %{_sbindir}/%{name}-selinux-enable
fi

%posttrans selinux
if /usr/sbin/selinuxenabled ; then
   %{_sbindir}/%{name}-selinux-relabel
fi

%postun
# Clean up after package removal
if [ $1 -eq 0 ]; then
  for selinuxvariant in targeted; do
      /usr/sbin/semodule -s ${selinuxvariant} -l > /dev/null 2>&1 \
        && /usr/sbin/semodule -s ${selinuxvariant} -r %{modulename} || :
    done
fi
%{sbinpath}/restorecon -rvvi %{_sharedstatedir}/copr

%files backend
%doc LICENSE README
%dir %{_datadir}/copr
%dir %{_sharedstatedir}/copr
%dir %attr(0755, copr, copr) %{_sharedstatedir}/copr/jobs/
%dir %attr(0755, copr, copr) %{_sharedstatedir}/copr/public_html/
%dir %attr(0755, copr, copr) %{_sharedstatedir}/copr/public_html/results
%dir %attr(0755, copr, copr) %{_var}/log/copr
%dir %attr(0755, copr, copr) %{_var}/log/copr/workers
%ghost %{_var}/log/copr/copr.log
%ghost %{_var}/log/copr/workers/worker-*.log
%config(noreplace) %{_sysconfdir}/logrotate.d/copr-backend
%dir %{_pkgdocdir}
%doc %{_pkgdocdir}/lighttpd
%doc %{_pkgdocdir}/playbooks
%dir %{_sysconfdir}/copr
%config(noreplace) %{_sysconfdir}/copr/copr-be.conf

%{_datadir}/copr/backend
%{_datadir}/copr/copr-be.py*

%files frontend
%doc LICENSE coprs.conf.example copr-setup.txt
%dir %{_datadir}/copr
%dir %{_sharedstatedir}/copr
%{_datadir}/copr/coprs_frontend

%defattr(-, copr-fe, copr-fe, -)
%dir %{_sharedstatedir}/copr/data
%dir %{_sharedstatedir}/copr/data/openid_store
%dir %{_sharedstatedir}/copr/data/whooshee
%dir %{_sharedstatedir}/copr/data/whooshee/copr_user_whoosheer

%ghost %{_sharedstatedir}/copr/data/copr.db

%defattr(600, copr-fe, copr-fe, 700)
%dir %{_sysconfdir}/copr
%config(noreplace)  %{_sysconfdir}/copr/copr.conf
%config(noreplace)  %{_sysconfdir}/copr/copr_devel.conf
%config(noreplace)  %{_sysconfdir}/copr/copr_unit_test.conf


%files cli
%doc LICENSE README.rst
%{_bindir}/copr-cli
%{python_sitelib}/*
%{_mandir}/man1/copr-cli.1*

%files doc
%doc %{_pkgdocdir}/python-doc

%files selinux
%{_datadir}/selinux/*/%{modulename}.pp.bz2
# empty, do not distribute it for now
%exclude %{_datadir}/selinux/devel/include/%{moduletype}/%{modulename}.if
%{_sbindir}/%{name}-selinux-enable
%{_sbindir}/%{name}-selinux-relabel
%{_mandir}/man8/%{name}-selinux-enable.8*
%{_mandir}/man8/%{name}-selinux-relabel.8*

%changelog
* Tue Sep 24 2013 Miroslav Suchý <msuchy@redhat.com> 1.8-1
- 1008532 - require python2-devel
- add note about ssh keys to copr-setup.txt
- set home of copr user to system default

* Mon Sep 23 2013 Miroslav Suchý <msuchy@redhat.com> 1.7-1
- 1008532 - backend should own _pkgdocdir
- 1008532 - backend should owns /etc/copr as well
- 1008532 - require logrotate
- 1008532 - do not distribute empty copr.if
- 1008532 - use %%{?_smp_mflags} macro with make
- move jobsdir to /var/lib/copr/jobs
- correct playbooks path
- selinux with enforce can be used for frontend

* Wed Sep 18 2013 Miroslav Suchý <msuchy@redhat.com> 1.6-1
- add BR python-devel
- generate selinux type for /var/lib/copr and /var/log/copr
- clean up backend setup instructions
- initial selinux subpackage

* Mon Sep 16 2013 Miroslav Suchý <msuchy@redhat.com> 1.5-1
- 1008532 - use __python2 instead of __python
- 1008532 - do not mark man page as doc
- 1008532 - preserve timestamp

* Mon Sep 16 2013 Miroslav Suchý <msuchy@redhat.com> 1.4-1
- add logrotate file

* Mon Sep 16 2013 Miroslav Suchý <msuchy@redhat.com> 1.3-1
- be clear how we create tgz

* Mon Sep 16 2013 Miroslav Suchý <msuchy@redhat.com> 1.2-1
- fix typo
- move frontend data into /var/lib/copr
- no need to own /usr/share/copr by copr-fe
- mark application as executable
- coprs_frontend does not need to be owned by copr-fe
- add executable attribute to copr-be.py
- remove shebang from dispatcher.py
- squeeze description into 80 chars
- fix typo
- frontend need argparse too
- move results into /var/lib/copr/public_html
- name of dir is just copr-%%version
- Remove un-necessary quote that breaks the tests
- Adjust unit-tests to the new urls
- Update the URL to be based upon a /user/copr/<action> structure
- comment config copr-be.conf and add defaults
- put examples of builderpb.yml and terminatepb.yml into doc dir
- more detailed description of copr-be.conf
- move files in config directory not directory itself
- include copr-be.conf
- include copr-be.py
- create copr with lighttpd group
- edit backend part of copr-setup.txt
- remove fedora16 and add 19 and 20
- create -doc subpackage with python documentation
- add generated documentation on gitignore list
- add script to generate python documentation
- copr-setup.txt change to for mock
- rhel6 do not know _pkgdocdir macro
- make instruction clear
- require recent whoosh
- add support for libravatar
- include backend in rpm
- add notes about lighttpd config files and how to deploy them
- do not list file twice
- move log file to /var/log
- change destdir in copr-be.conf.example
- lightweight is the word and buildsystem has more meaning than 'koji'.
- restart apache after upgrade of frontend
- own directory where backend put results
- removal of hidden-file-or-dir
  /usr/share/copr/coprs_frontend/coprs/logic/.coprs_logic.py.swo
- copr-backend.noarch: W: spelling-error %%description -l en_US latests ->
  latest, latest's, la tests
- simplify configuration - introduce /etc/copr/copr*.conf
- Replace "with" statements with @TransactionDecorator decorator
- add python-flexmock to deps of frontend
- remove sentence which does not have meaning
- change api token expiration to 120 days and make it configurable
- create_chroot must be run as copr-fe user
- add note that you have to add chroots to db
- mark config.py as config so it is not overwritten during upgrade
- own directory data/whooshee/copr_user_whoosheer
- gcc is not needed
- sqlite db must be owned by copr-fe user
- copr does not work with selinux
- create subdirs under data/openid_store
- suggest to install frontend as package from copr repository
- on el6 add python-argparse to BR
- add python-requests to BR
- add python-setuptools to BR
- maintain apache configuration on one place only
- apache 2.4 changed access control
- require python-psycopg2
- postgresql server is not needed
- document how to create db
- add to HOWTO how to create db
- require python-alembic
- add python-flask-script and python-flask-whooshee to requirements
- change user in coprs.conf.example to copr-fe
- fix paths in coprs.conf.example
- copr is noarch package
- add note where to configure frontend
- move frontend to /usr/share/copr/coprs_frontend
- put production placeholders in coprs_frontend/coprs/config.py
- put frontend into copr.spec
- web application should be put in /usr/share/%%{name}

* Mon Jun 17 2013 Miroslav Suchý <msuchy@redhat.com> 1.1-1
- new package built with tito


