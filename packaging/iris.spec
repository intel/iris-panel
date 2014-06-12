#
# spec file for the iris-core package.
#
# Installs iris-core and related subpackages.
# Installed packages are under "iris" Python package.
#
# Please refer to documentation for additional information.
#

%define project_alias iris-panel
%define core_name core
%define packagedb_name packagedb
%define submissions_name submissions
%define media_root /srv/www/iris/media
%define static_root /srv/www/iris/static

###############################################################################
# Logical iris package that installs iris-core and iris-packagedb

Name:           iris
Summary:        Infrastructure and Release Information System
Version:        0.1.1

%if 0%{?opensuse_bs}
Release:        0.dev.<CI_CNT>.<B_CNT>
%else
Release:        0
%endif

Group:          Development/Tools/Other
License:        GPL-2.0
BuildArch:      noarch
URL:            https://otctools.jf.intel.com/pm/projects/iris
Source0:        %{project_alias}_%{version}.tar.gz
Source5:        iris-rpmlintrc

BuildRequires:  python-setuptools
BuildRequires:  jquery-multi-select
BuildRequires:  python-django
BuildRequires:  python-django-rest-swagger
BuildRequires:  python-South
BuildRequires:  python-xml
BuildRequires:  python-django-debug-toolbar

Requires:       %{name}-%{core_name} = %{version}
Requires:       %{name}-%{packagedb_name} = %{version}
Requires:       %{name}-%{submissions_name} = %{version}

%description
Common modules and dependancies for core and packagedb.

%prep
%setup -n %{project_alias}_%{version}

%build
python ./setup.py build

%install
python ./setup.py install --prefix=%{_prefix} --root=%{buildroot}

mediapath=%{buildroot}%{media_root}
staticpath=%{buildroot}%{static_root}
install -d $mediapath
install -d $staticpath

# Static files from django admin site and all django plugins
# need be collected here
python -m iris.manage shell <<EOF
from django.conf import settings
settings.MEDIA_ROOT="${mediapath}"
settings.STATIC_ROOT="${staticpath}"
from django.core.management import call_command
call_command('collectstatic', interactive=False)
EOF

install -D      README                              %{buildroot}%{_prefix}/share/doc/packages/%{name}/README
install -D      doc/iris/example.conf               %{buildroot}%{_prefix}/share/doc/packages/%{name}/iris.conf
install -D      etc/%{name}/%{name}.conf            %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
install -D      etc/apache2/vhosts.d/%{name}.conf   %{buildroot}%{_sysconfdir}/apache2/vhosts.d/%{name}.conf
install -D      srv/www/iris/wsgi.py                %{buildroot}/srv/www/iris/wsgi.py

jspath=/usr/share/javascript
csspath=/usr/share/css
imgpath=/usr/share/images
fontpath=/usr/share/fonts

install -D $jspath/jquery-multi-select/*        $staticpath
install -D $csspath/jquery-multi-select/*       $staticpath
install -D $imgpath/jquery-multi-select/*       $staticpath

install -D iris/core/static/*                   $staticpath

%files
%defattr(-,root,root,-)

%clean
rm -rf %{buildroot}

###############################################################################
# Binary iris-core package that installs the Core project for IRIS server

%package %{core_name}
Summary:        Core

Requires:       apache2
Requires:       apache2-mod_wsgi
Requires:       mysql-community-server
Requires:       mysql-community-server-client
Requires:       python >= 2.6
Requires:       python-xml
Requires:       python-setuptools
Requires:       python-mysql
Requires:       python-django
Requires:       python-South
Requires:       python-ldap
Requires:       python-django-auth-ldap
Requires:       python-django-crispy-forms
Requires:       python-djangorestframework
Requires:       python-django-rest-swagger
Requires:       git
Requires(pre):  pwdutils

%description %{core_name}
Core, an extendible web portal for pluggable applications.

%pre %{core_name}
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || useradd -r -g %{name} -d /srv/www/%{name} -s /sbin/nologin -c "user for %{name}" %{name}

%post %{core_name}
# Generate Django secret file if it doesn't exist
secret_file=%{_sysconfdir}/%{name}/secret.txt
if ! test -e $secret_file; then
    %{_bindir}/generate_django_secret_key.py >$secret_file
    chown %{name}:%{name} $secret_file
    chmod 400 $secret_file
fi

if which apache2ctl; then
    # 06-check-installtest script runs %post before actual package post installation
    # We need to check if we actually are at post install stage with dependancies
    service apache2 stop
    service apache2 start
fi

%files %{core_name}
%defattr(-,root,root,-)
%dir                                                %{_datadir}/doc/packages/%{name}
%doc                %attr(0644, root, root)         %{_datadir}/doc/packages/%{name}/README
%doc doc/RELEASE_NOTES
%doc                %attr(0644, root, root)         %{_datadir}/doc/packages/%{name}/iris.conf
%dir                                                %{_sysconfdir}/%{name}
%config(noreplace)  %attr(0644, root, root)         %{_sysconfdir}/%{name}/%{name}.conf
%dir                                                %{_sysconfdir}/apache2
%dir                                                %{_sysconfdir}/apache2/vhosts.d
%config(noreplace)  %attr(0644, root, root)         %{_sysconfdir}/apache2/vhosts.d/%{name}.conf
%dir                                                /srv/www/iris
                    %attr(0644, root, root)         /srv/www/iris/wsgi.py
%dir %{static_root}
%{static_root}/*

%dir %{python_sitelib}/%{name}
%{python_sitelib}/%{name}/*.py
%{python_sitelib}/%{name}/*.pyc
%{python_sitelib}/%{name}/%{core_name}
%{python_sitelib}/%{name}-%{version}-*.egg-info
%{python_sitelib}/%{name}-%{version}-*-nspkg.pth

%{_bindir}/generate_django_secret_key.py
%{_bindir}/import_scm.py
%{_bindir}/update_iris_data.sh

%changelog %{core_name}

###############################################################################
# Binary iris-packagedb package that installs the Package Database application

%package %{packagedb_name}
Summary:        Package Database

Requires:       %{name}-%{core_name} = %{version}

%description %{packagedb_name}
Package Database web portal and RESTful API.

%files %{packagedb_name}
%defattr(-,root,root,-)
%{python_sitelib}/%{name}/%{packagedb_name}
%{python_sitelib}/%{name}_%{packagedb_name}-%{version}-*.egg-info
%{python_sitelib}/%{name}_%{packagedb_name}-%{version}-*-nspkg.pth

%changelog %{packagedb_name}

###############################################################################
# Binary iris-submissions package that installs the Submissions application

%package %{submissions_name}
Summary:        Submissions

Requires:       %{name}-%{core_name} = %{version}

%description %{submissions_name}
Submissions web portal and RESTful API.

%files %{submissions_name}
%defattr(-,root,root,-)
%{python_sitelib}/%{name}/%{submissions_name}
%{python_sitelib}/%{name}_%{submissions_name}-%{version}-*.egg-info
%{python_sitelib}/%{name}_%{submissions_name}-%{version}-*-nspkg.pth

%changelog %{submissions_name}
