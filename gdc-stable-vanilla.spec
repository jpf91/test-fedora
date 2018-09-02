#
# spec file for package gdc-stable-vanilla
# source code for this spec file is maintained at ...
#

# To detect whether we're on OBS
%if %(if [[ "%{vendor}" == obs://* ]] ; then echo 1 ; else echo 0 ; fi)
%define opensuse_bs 1
%endif

# OBS ppc64le builder often goes OOM
%if 0%{?opensuse_bs}
%ifarch ppc64le
%global make_multicore_flags -j1
%else
%global make_multicore_flags %{?_smp_mflags}
%endif
%else
%global make_multicore_flags %{?_smp_mflags}
%endif

# Note, gcc_release must be integer, if you want to add suffixes to
# %%{release}, append them after %%{gcc_release} on Release: line.
%global gdc_snapshot 20180729gitd28e61d
%global phobos_version 2.081.2
%global gcc_version 8.2.0
%global gcc_release 1

# Whether we want to build libphobos for this arch
%ifarch x86_64 %{ix86} %{arm}
  %global build_libphobos 1
%else
  %global build_libphobos 0
%endif

# Workaround the fact that OBS ignores the Release: information
%global obs_stupid_release %{gcc_release}.%{gdc_snapshot}%{?dist}.1

Summary: The GNU D Compiler GDC and runtime library, vanilla version
Name: gdc-stable-vanilla
Version: %{gcc_version}
Release: %{obs_stupid_release}
License: GPLv3+ and GPLv3+ with exceptions and GPLv2+ with exceptions and LGPLv2+ and BSD and Boost
Group: Development/Languages
Source0: gcc-%{version}.tar.xz
Source1: gdc-%{gdc_snapshot}.tar.gz
Source2: gdc-stable-vanilla-rpmlintrc
URL: http://gdcproject.org

BuildRequires: binutils, zlib-devel, gettext, dejagnu, bison, flex, sharutils
BuildRequires: glibc-devel, texinfo, gmp-devel, mpfr-devel
BuildRequires: gcc, gcc-c++
%if 0%{?suse_version}
BuildRequires: mpc-devel 
%else
BuildRequires: libmpc-devel texinfo-tex
%endif

# Required for SUSE builds
#!BuildIgnore: gcc-PIE

Requires: binutils
Requires: glibc-devel
Requires: gcc
Provides: gdc-stable = %{gcc_version}
Provides: gdc = %{gcc_version}

# We package everything as one package, so make sure to provide
# the libphobos packages as well, in case other packages depend on this
%if %{build_libphobos}
Provides: libgphobos-stable = %{phobos_version}
Provides: libgphobos = %{phobos_version}
Provides: libgphobos-stable-devel = %{phobos_version}
Provides: libgphobos-devel = %{phobos_version}
%endif

# Do not check .so files in an application-specific library directory
# or any files in the application's data directory for provides
%global __provides_exclude_from ^/opt/.*$



%description
D compiler (language version 2), based on the GCC backend. Generic,
non-patched GCC non-multilib build.



%prep
%setup -q -n gcc-%{version} -a 0
gcc_src_dir=$(pwd)
pushd ../
  mkdir gdc_src
  tar xf %{SOURCE1} -C gdc_src --strip-components 1
  pushd gdc_src
  ./setup-gcc.sh $gcc_src_dir
  popd
popd



%build
mkdir objdir
cd objdir
../configure --disable-bootstrap --enable-languages=d,lto --enable-checking=release \
    --disable-multilib --prefix=/opt/gdc-stable-vanilla \
%if !%{build_libphobos}
    --disable-libphobos \
%endif
%ifarch armv7hl
	--with-float=hard \
%if 0%{?fedora} >= 20 || 0%{?rhel} >= 6
	--with-tune=generic-armv7-a --with-arch=armv7-a \
	--with-fpu=vfpv3-d16 --with-abi=aapcs-linux \
%endif
%endif
    --libdir=/opt/gdc-stable-vanilla/%{_lib} --enable-linker-build-id

make %{make_multicore_flags}



%install
# Add ld.so.conf file so that ld.so loader finds our libgphobos libs in /opt
mkdir -p %{buildroot}/etc/ld.so.conf.d/
echo "/opt/gdc-stable-vanilla/%{_lib}" > %{buildroot}/etc/ld.so.conf.d/gdc-stable-vanilla.conf

cd objdir
make DESTDIR=%{buildroot} install
# Add symlink so that users can simply use gdc command. TODO: do rpm distros
# have something like debian's alternatives system?
mkdir -p %{buildroot}%{_bindir}/
ln -s /opt/gdc-stable-vanilla/bin/gdc %{buildroot}%{_bindir}/gdc



%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig



%files
%{_bindir}/gdc
/opt/gdc-stable-vanilla
/etc/ld.so.conf.d/gdc-stable-vanilla.conf
