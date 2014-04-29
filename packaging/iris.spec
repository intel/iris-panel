#
# spec file for the iris-core package.
#
# Installs iris-core and related subpackages.
# Installed packages are under "iris" Python package.
#
# Please refer to documentation for additional information.
#

%define project_name iris
%define project_alias iris-panel
%define core_name core
%define packagedb_name packagedb
%define submissions_name submissions

###############################################################################
# Logical iris package that installs iris-core and iris-packagedb

Name:           %{project_name}
Summary:        Infrastructure and Release Information System
Version:        0.0.2

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
Requires(pre):  pwdutils

Requires:       %{project_name}-%{core_name} = %{version}
Requires:       %{project_name}-%{packagedb_name} = %{version}
Requires:       %{project_name}-%{submissions_name} = %{version}

%description
Common modules and dependancies for core and packagedb.

%prep
%setup -n %{project_alias}_%{version}

%build
python ./setup.py build

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || useradd -r -g %{name} -d /srv/www/%{name} -s /sbin/nologin -c "user for %{name}" %{name}
exit 0

%install
python ./setup.py install --prefix=%{_prefix} --root=%{buildroot}

install -D      README                              %{buildroot}%{_prefix}/share/doc/packages/%{name}/README
install -D      doc/iris/example.conf               %{buildroot}%{_prefix}/share/doc/packages/%{name}/iris.conf
install -D      etc/%{name}/%{name}.conf            %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
install -D      etc/apache2/vhosts.d/%{name}.conf   %{buildroot}%{_sysconfdir}/apache2/vhosts.d/%{name}.conf
install -D      srv/www/iris/wsgi.py                %{buildroot}/srv/www/iris/wsgi.py

# 06-check-installtest script runs %post before actual package post installation
# We need to check if we actually are at post install stage with dependancies
%post
if which apache2ctl; then
    install -d /srv/www/iris/static
    install -d /srv/www/iris/media
    MANAGE=$(python -c "from iris import manage; print(manage.__file__)")
    python $MANAGE collectstatic --noinput
    service apache2 stop
    service apache2 start
fi

# Generate Django secret file if it doesn't exist
secret_file=%{_sysconfdir}/%{name}/secret.txt
if ! test -e $secret_file; then
    %{_bindir}/generate_django_secret_key.py >$secret_file
    chown %{name}:%{name} $secret_file
    chmod 400 $secret_file
fi

%preun
if [ -d /srv/www/iris/static ]; then
    rm -rf /srv/www/iris/static
fi

if [ -d /srv/www/iris/media ]; then
    rm -rf /srv/www/iris/media
fi

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
Requires:       python-setuptools
Requires:       python-mysql
Requires:       django
Requires:       python-South
Requires:       python-ldap
Requires:       python-django-auth-ldap
Requires:       jquery
Requires:       jquery-multi-select
Requires:       bootstrap
Requires:       django-crispy-forms
Requires:       djangorestframework
Requires:       django-rest-swagger

%description %{core_name}
Core, an extendible web portal for pluggable applications.

%files %{core_name}
%defattr(-,root,root,-)
%dir                                                %{_datadir}/doc/packages/%{name}
%doc                %attr(0644, root, root)         %{_datadir}/doc/packages/%{name}/README
%doc                %attr(0644, root, root)         %{_datadir}/doc/packages/%{name}/iris.conf
%dir                                                %{_sysconfdir}/%{name}
%config(noreplace)  %attr(0644, root, root)         %{_sysconfdir}/%{name}/%{name}.conf
%dir                                                %{_sysconfdir}/apache2
%dir                                                %{_sysconfdir}/apache2/vhosts.d
%config(noreplace)  %attr(0644, root, root)         %{_sysconfdir}/apache2/vhosts.d/%{name}.conf
%dir                                                /srv/www/iris
                    %attr(0644, root, root)         /srv/www/iris/wsgi.py

%dir %{python_sitelib}/%{name}
%{python_sitelib}/%{name}/*.py
%{python_sitelib}/%{name}/*.pyc
%{python_sitelib}/%{name}/%{core_name}
%{python_sitelib}/%{name}-%{version}-*.egg-info
%{python_sitelib}/%{name}-%{version}-*-nspkg.pth

%{_bindir}/generate_django_secret_key.py

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

Requires:       datatables
Requires:       %{name}-%{core_name} = %{version}

%description %{submissions_name}
Submissions web portal and RESTful API.

%files %{submissions_name}
%defattr(-,root,root,-)
%{python_sitelib}/%{name}/%{submissions_name}
%{python_sitelib}/%{name}_%{submissions_name}-%{version}-*.egg-info
%{python_sitelib}/%{name}_%{submissions_name}-%{version}-*-nspkg.pth

%changelog %{submissions_name}
