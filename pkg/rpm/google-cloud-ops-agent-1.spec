%if 0%{?sle_version} > 0
# we expect the distro suffix
%global dist .sles%(expr substr %{sle_version} 1 2)
%if %{sle_version} <= 12
# systemd macros have different names
%global systemd_post %{service_add_post %1}
%global systemd_preun %{service_del_preun %1}
%global systemd_postun %{service_del_postun %1}
%endif
%endif

Name: google-cloud-ops-agent-1
Version: %{package_version}
Release: 1%{?dist}
Summary: Google Cloud Ops Agent
Packager: Google Cloud Ops Agent <google-cloud-ops-agent-1@google.com>
License: ASL 2.0
%if 0%{?rhel} <= 7
BuildRequires: systemd
%else
BuildRequires: systemd-rpm-macros
%endif
Conflicts: stackdriver-agent, google-fluentd
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description
The Google Cloud Ops Agent collects metrics and logs from the system.

%define _prefix /opt/%{name}
%define _confdir /etc/%{name}
%define _subagentdir %{_prefix}/subagents

%prep

%install
cd %{_sourcedir}
build_distro=%{dist}
CODE_VERSION=%{version} BUILD_DISTRO=${build_distro#.} DESTDIR="%{buildroot}" ./build.sh

%files
%config %{_confdir}/config.yaml
%{_subagentdir}/fluent-bit/*
%{_subagentdir}/collectd/*
# We aren't using %{_libexecdir} here because that would be lib on some
# platforms, but the build.sh script hard-codes libexec.
%{_prefix}/libexec/google_cloud_ops_agent_engine
%{_unitdir}/%{name}*
%{_unitdir}-preset/*-%{name}*

%post
%systemd_post google-cloud-ops-agent-1.target
if [ $1 -eq 1 ]; then  # Initial installation
  systemctl start google-cloud-ops-agent-1.target >/dev/null 2>&1 || :
fi

%preun
%systemd_preun google-cloud-ops-agent-1.target

%postun
%systemd_postun_with_restart google-cloud-ops-agent-1.target

%changelog