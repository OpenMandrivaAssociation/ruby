%define subver %(echo %{version}|cut -d. -f1-2)
%define abiver %{subver}.0

### (Based on Fedora)
# https://src.fedoraproject.org/rpms/ruby/blob/master/f/macros.ruby
# sed -e 's,^%,%%define fedora_,g'
%define fedora_ruby_libarchdir %{_libdir}/%{name}
# Arch-dependent *.so must not be in /usr/share
#define fedora_ruby_libdir %%{_datadir}/%%{name}
%define fedora_ruby_libdir %{fedora_ruby_libarchdir}
%define fedora_ruby_sitedir site_ruby
%define ruby_sitedir site_ruby
# Instead of local prefix in Fedora, use normal system locations
# because macros like %%ruby_sitearchdir are widely used in ROSA packaging.
# Is it correct?! Debian/Ubuntu also use local prefix for them!
#define fedora_ruby_sitelibdir %%{_prefix}/local/share/%%{name}/%%{ruby_sitedir}
%define fedora_ruby_sitelibdir %{_datadir}/%{name}/%{ruby_sitedir}
#define fedora_ruby_sitearchdir %%{_prefix}/local/%%{_lib}/%{name}/%%{ruby_sitedir}
%define fedora_ruby_sitearchdir %{_libdir}/%{name}/%{ruby_sitedir}
# This is the general location for libs/archs compatible with all
# or most of the Ruby versions available in the Fedora repositories.
%define fedora_ruby_vendordir vendor_ruby
%define fedora_ruby_vendorlibdir %{fedora_ruby_libdir}/%{fedora_ruby_vendordir}
%define fedora_ruby_vendorarchdir %{fedora_ruby_libarchdir}/%{fedora_ruby_vendordir}
# (From Fedora spec)
# The RubyGems library has to stay out of Ruby directory tree, since the
# RubyGems should be shared by all Ruby implementations.
# Fedora uses /usr/share/rubygems/, but I like /usr/share/ruby/gems/ more
%define fedora_rubygems_dir %{_datadir}/ruby/gems

# as in Fedora from where we borrow patches
%global _default_patch_fuzz 2

Summary:	Object Oriented Script Language
Name:		ruby
Version:	3.2.0
Release:	1
License:	Ruby or GPLv2+
Group:		Development/Ruby
Url:		http://www.ruby-lang.org/
Source0:	https://cache.ruby-lang.org/pub/ruby/%{subver}/ruby-%{version}.tar.xz
Source1:	macros.ruby
Source2:	macros.rubygems
Source3:	rubygems.con
# from ruby 1.9, to prevent file conflicts
Source4:	ruby-mode.el
Source5:	rubygems.attr
Source6:	rubygems.prov
Source7:	rubygems.req
# Use shared libs as opposed to static for mkmf
# See bug rhbz#428384
Patch1:		ruby-2.1.2-mkmf-use-shared.patch
# http://redmine.ruby-lang.org/issues/5108
Patch3:		ruby-2.1.2-stdout-rouge-fix.patch
# From Fedora
Patch4:		ruby-2.1.0-Enable-configuration-of-archlibdir.patch
Patch5:		ruby-2.1.0-custom-rubygems-location.patch
BuildRequires:	byacc
BuildRequires:	db18-devel
BuildRequires:	gdbm-devel
BuildRequires:	readline-devel
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(libssl)
BuildRequires:	pkgconfig(yaml-0.1)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(gmp)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	glibc-static-devel
Provides:	rubygems = %{EVRD}
Provides:	ruby(abi) = %{abiver}

%description
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl).  It is simple, straight-forward, and extensible.

%files
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*
%{_bindir}/bundle*
%{_bindir}/erb
%{_bindir}/gem
%{_bindir}/irb
%{_bindir}/racc*
%{_bindir}/rake
%{_bindir}/rdoc
%{_bindir}/ri
%{_bindir}/ruby
%{_bindir}/rbs
%{_bindir}/rdbg
%{_bindir}/typeprof
%{_datadir}/emacs/site-lisp/*
%{_mandir}/man1/*
%{_datadir}/ruby
%{_libdir}/ruby
%{_rpmmacrodir}/*ruby*
%{_rpmconfigdir}/fileattrs/rubygems.attr
%{_rpmconfigdir}/rubygems.req
%{_rpmconfigdir}/rubygems.prov
%{_rpmconfigdir}/rubygems.con

#----------------------------------------------------------------------------

%define libname %mklibname ruby %{subver}

%package -n %{libname}
Summary:	Shared main library for ruby %{subver}
Group:		System/Libraries

%description -n %{libname}
This package contains the shared ruby %{subver} library.

%files -n %{libname}
%{_libdir}/libruby.so.%{subver}*

#----------------------------------------------------------------------------

%package doc
Summary:	Documentation for the powerful language Ruby
Group:		Development/Ruby
BuildArch:	noarch

%description doc
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl). It is simple, straight-forward, and extensible.

This package contains the Ruby's documentation

%files doc
%{_datadir}/ri
%{_defaultdocdir}/%{name}-%{version}/COPYING*
%{_defaultdocdir}/%{name}-%{version}/ChangeLog
%{_defaultdocdir}/%{name}-%{version}/README.*
%{_defaultdocdir}/%{name}-%{version}/sample

#----------------------------------------------------------------------------

%package devel
Summary:	Development file for the powerful language Ruby
Group:		Development/Ruby
Requires:	%{name} = %{EVRD}
%define olddevname %mklibname -d ruby
%rename %{olddevname}

%description devel
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl). It is simple, straight-forward, and extensible.

This package contains the Ruby's devel files.

%files devel
%{_includedir}/*.h
%{_includedir}/ruby
%{_libdir}/libruby.so
%{_libdir}/pkgconfig/ruby-%{subver}.pc
%{_libdir}/pkgconfig/ruby.pc

#----------------------------------------------------------------------------

%prep
%autosetup -p1

# Remove bundled libraries to be sure they are not used.
rm -rf ext/psych/yaml
rm -rf ext/fiddle/libffi*

%build
autoreconf -fi
%configure \
	--enable-shared \
	--enable-rubygems \
	--without-baseruby \
	--disable-rpath \
	--enable-pthread \
	--with-setjmp-type=setjmp \
	--with-rubylibprefix='%{fedora_ruby_libdir}' \
	--with-archlibdir='%{_libdir}' \
	--with-rubyarchprefix='%{fedora_ruby_libarchdir}' \
	--with-sitedir='%{fedora_ruby_sitelibdir}' \
	--with-sitearchdir='%{fedora_ruby_sitearchdir}' \
	--with-vendordir='%{fedora_ruby_vendorlibdir}' \
	--with-vendorarchdir='%{fedora_ruby_vendorarchdir}' \
	--with-rubyhdrdir='%{_includedir}' \
	--with-rubyarchhdrdir='%{_includedir}' \
	--with-sitearchhdrdir='$(sitehdrdir)/$(arch)' \
	--with-vendorarchhdrdir='$(vendorhdrdir)/$(arch)' \
	--with-rubygemsdir='%{fedora_rubygems_dir}' \
	--with-ruby-pc='%{name}-%{subver}.pc' \
	--with-compress-debug-sections=no

# Force verconf.h regeneration (for build with frozen time)
[ -f verconf.h ] && rm verconf.h
%ifarch %{ix86}
%make_build COPY="cp -p" Q= EXTLDFLAGS="--rtlib=compiler-rt -Wl,-z,notext"
%else
%make_build COPY="cp -p" Q=
%endif

%install
TOP="$(pwd)"
# FIXME why do we have to specify extout and LIBRUBYARG_SHARED here?
# Seems to be a weird missing BuildRequires (since make install works
# as expected if built on a really complete development setup)
%make_install Q= V=1 extout=${TOP}/.ext LIBRUBYARG_SHARED="-L${TOP} -lruby"

install -d %{buildroot}%{_docdir}/%{name}-%{version}
cp -a COPYING* ChangeLog README* sample %{buildroot}%{_docdir}/%{name}-%{version}

install -m644 %{SOURCE4} -D %{buildroot}%{_datadir}/emacs/site-lisp/ruby-mode.el

install -d %{buildroot}%{_sysconfdir}/emacs/site-start.d
cat <<EOF >%{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.el
(autoload 'ruby-mode "ruby-mode" "Ruby editing mode." t)
(add-to-list 'auto-mode-alist '("\\\\.rb$" . ruby-mode))
(add-to-list 'interpreter-mode-alist '("ruby" . ruby-mode))
EOF

# Fix scripts permissions and location
find %{buildroot} sample -type f | file -i -f - | grep text | cut -d: -f1 >text.list
cat text.list | xargs chmod 0644
#  Magic grepping to get only files with '#!' in the first line
cat text.list | xargs grep -n '^#!' | grep ':1:#!' | cut -d: -f1 >shebang.list
cat shebang.list | xargs sed -i -e 's|/usr/local/bin|/usr/bin|; s|\./ruby|/usr/bin/ruby|'
cat shebang.list | xargs chmod 0755

mkdir -p %{buildroot}%{_libdir}/pkgconfig/
cp ruby-%{subver}.pc %{buildroot}%{_libdir}/pkgconfig/
ln -s ruby-%{subver}.pc %{buildroot}%{_libdir}/pkgconfig/ruby.pc

#install macros ruby and rubygems 
mkdir -p %{buildroot}%{_rpmconfigdir}/macros.d
install -m 644 %{SOURCE1} %{buildroot}%{_rpmconfigdir}/macros.d/macros.ruby
install -m 644 %{SOURCE2} %{buildroot}%{_rpmconfigdir}/macros.d/macros.rubygems
# RPM dependency generators.
install -D -m 644 %{SOURCE5} %{buildroot}%{_rpmconfigdir}/fileattrs/rubygems.attr
install -m 755 %{SOURCE3} %{buildroot}%{_rpmconfigdir}
install -m 755 %{SOURCE6} %{buildroot}%{_rpmconfigdir}
install -m 755 %{SOURCE7} %{buildroot}%{_rpmconfigdir}

%check
make test
