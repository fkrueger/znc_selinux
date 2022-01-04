# vim: sw=4:ts=4:et

%define selinux_policyver 3.14.3-1
%define selinux_ppname znc
%define selinux_porttype znc_port_t
%define selinux_ports_tcp 6667 11577
%define selinux_ports_udp nil
%define selinux_dirs /var/lib/znc/ /usr/bin/znc /usr/lib64/znc/

Name:   znc_selinux
Version:	1.0
Release:	1%{?dist}
Summary:	SELinux policy module for znc
BuildRequires: policycoreutils, selinux-policy-devel

Group:	System Environment/Base		
License:	GPLv2+	
URL:		https://github.com/fkrueger/znc_selinux
Source0:	znc.te
Source1:	znc.fc
Source2:	znc.if
Source3:	znc_selinux.8
Source4:	znc_selinux-readme.md

Requires: policycoreutils, libselinux-utils
Requires(post): selinux-policy-base >= %{selinux_policyver}, policycoreutils
Requires(postun): policycoreutils
BuildArch: noarch

%description
This package installs and sets up the SELinux policy security module for znc.

%install
%{__mkdir_p} %{buildroot}%{_defaultdocdir}/%{name}-%{version} %{buildroot}%{_datadir}/selinux/devel/include/contrib %{buildroot}%{_datadir}/selinux/packages %{buildroot}%{_mandir}/man8 %{buildroot}/etc/selinux/targeted/contexts/users
install -m 644 %{SOURCE2} %{buildroot}%{_datadir}/selinux/devel/include/contrib/
install -m 600 %{SOURCE3} %{buildroot}%{_mandir}/man8/znc_selinux.8
install -m 644 %{SOURCE4} %{buildroot}%{_defaultdocdir}/%{name}-%{version}/readme.md
install -m 644 %{_builddir}/%{name}-%{version}-%{release}.%{_arch}/%{selinux_ppname}.pp %{buildroot}%{_datadir}/selinux/packages

%build
TMPB="%{_builddir}/%{name}-%{version}-%{release}.%{_arch}/"
mkdir -p "$TMPB"
cp %{SOURCE0} %{SOURCE1} %{SOURCE2} "$TMPB"
cd "$TMPB"
make -f /usr/share/selinux/devel/Makefile

%post
# install policy modules
## generic part
semodule -n -i %{_datadir}/selinux/packages/%{selinux_ppname}.pp
# then add port definitions and context mirroring from /home/foo/.steam/ and .local - stuff for /opt/znc/
for i in %{selinux_ports_tcp} XXX; do
    [ "x$i" != "xXXX" ] && semanage port -a -t %{selinux_porttype} -p tcp $i || :
done
for i in %{selinux_ports_udp} XXX; do
    [ "x$i" != "xXXX" ] && semanage port -a -t %{selinux_porttype} -p udp $i || :
done
## custom part
semanage fcontext -a -e '/var/lib/znc/.znc(/.*?)' '/home/[^/]+/.znc(/.*)?' || :
# setup
if /usr/sbin/selinuxenabled ; then
    /usr/sbin/load_policy
    restorecon -R %{selinux_dirs} || :
fi
if [ "x$1" == "x0" ]; then
  echo "-> ONLY for first install: Remember to restart your znc, so it gets run securely under this newly installed SELinux policy!"
  echo ""
fi
exit 0

%postun
if [ $1 -eq 0 ]; then
    # try to remove all port definitions and context-mirroring.
    # generic part
    for i in %{selinux_ports_tcp} XXX; do
        [ "x$i" != "xXXX" ] && semanage port -d -t %{selinux_porttype} -p tcp $i || :
    done
    for i in %{selinux_ports_udp} XXX; do
        [ "x$i" != "xXXX" ] && semanage port -d -t %{selinux_porttype} -p udp $i || :
    done
    ## custom part
    semanage fcontext -d '/home/[^/]+/.znc(/.*)?' || :
    # then try to remove the policy module
    semodule -n -r znc
    if /usr/sbin/selinuxenabled ; then
       /usr/sbin/load_policy
       /usr/sbin/restorecon -R %{selinux_dirs} || :
    fi;
fi;
exit 0

%files
%attr(0600,root,root) %{_datadir}/selinux/packages/%{selinux_ppname}.pp
%{_datadir}/selinux/devel/include/contrib/znc.if
%{_mandir}/man8/znc_selinux.8.*
%doc %{_defaultdocdir}/%{name}-%{version}/readme.md


%changelog
* Wed Oct 27 2021 Frederic Krueger <fkrueger-dev-selinux_znc@holics.at> 1.0-1
- Initial version

