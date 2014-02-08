%define subver 1.9
%define abiver 1.9.1
%define rubyver 1.9.3
%define patchversion p385
%bcond_without	tcltk

Summary:	Object Oriented Script Language
Name:		ruby
Version:	%{rubyver}.%{patchversion}
Release: 	4
License:	Ruby or GPLv2
Group:		Development/Ruby

Source0:	ftp://ftp.ruby-lang.org/pub/ruby/%{subver}/ruby-%{rubyver}-%{patchversion}.tar.bz2
Source1:	http://www.rubycentral.com/faq/rubyfaqall.html
Source2:	http://dev.rubycentral.com/downloads/files/ProgrammingRuby-0.4.tar.bz2
# from ruby 1.9, to prevent file conflicts
Source4:	ruby-mode.el
Patch1:		ruby-do-not-use-system-ruby-to-generate-ri-doc.patch
Patch3:		ruby-do_not_propagate_no-undefined.patch
Patch4:		ruby-1.9.3-gnueabi.patch
# http://redmine.ruby-lang.org/issues/5108
Patch5:		ruby-1.8.7-p352-stdout-rouge-fix.patch
# Use shared libs as opposed to static for mkmf
# See bug rhbz#428384
Patch6:		ruby-1.8.7-p249-mkmf-use-shared.patch
#aarch64
Patch7:		ruby-1.9-aarch64.patch
URL:		http://www.ruby-lang.org/

BuildRequires:	autoconf
BuildRequires:	byacc
BuildRequires:	ncurses-devel
BuildRequires:	readline-devel
%if %{with tcltk}
BuildRequires:	tcl-devel tk-devel
%endif
BuildRequires:	db52-devel
BuildRequires:	gdbm-devel >= 1.8.3
BuildRequires:	openssl-devel
BuildRequires:	zlib-devel
BuildRequires:	yaml-devel
%rename		ruby-rexml
%rename		ruby-irb
%rename		ruby-libs
%rename		ruby-rdoc
%rename		ruby1.9
%rename		ruby-rake
%rename		rubygem-rake
Provides:	rubygem(rake) = 0.9.2.2
%rename		ruby-RubyGems
Provides:	rubygems = %version-%release

# explicit file provides (since such requires are automatically added by find-requires)
Provides:	/usr/bin/ruby
Provides:	ruby(abi) = %{abiver}
# will also apply to all subpackages also, but since they all depend on
# ruby = %version anyways for now, it doesn't really matter...
%if %{_use_internal_dependency_generator}
%define __noautoreq		'ruby\\(abi\\)'
%else
%define _requires_exceptions	ruby\(abi\)
%endif

%define my_target_cpu %{_target_cpu}
%ifarch ppc
%define my_target_cpu powerpc
%endif
%ifarch ppc64
%define my_target_cpu powerpc64
%endif
%ifarch amd64
%define my_target_cpu x86_64
%endif

%define	libname	%mklibname ruby %{subver}

%package -n	%{libname}
Summary:	Shared main library for ruby %{subver}
Group:		System/Libraries

%package	doc
Summary:	Documentation for the powerful language Ruby
Group:		Development/Ruby
BuildArch:	noarch
%rename		ruby1.9-doc

%package	devel
Summary:	Development file for the powerful language Ruby
Group:		Development/Ruby
Requires:	%{name} = %{version}
%rename		ruby-static
%rename		ruby1.9-devel

%if %{with tcltk}
%package	tk
Summary:	Tk extension for the powerful language Ruby
Group:		Development/Ruby
Requires:	%{name} = %{version}
%rename		ruby1.9-tk

%description	tk
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl). It is simple, straight-forward, and extensible.

This package contains the Tk extension for Ruby.
%endif

%description
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl).  It is simple, straight-forward, and extensible.

%description -n	%{libname}
This package contains the shared ruby %{subver} library.

%description	doc
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl). It is simple, straight-forward, and extensible.

This package contains the Ruby's documentation

%description	devel
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl). It is simple, straight-forward, and extensible.

This package contains the Ruby's devel files.


%prep
%setup -q -n ruby-%{rubyver}-%{patchversion}
%patch1 -p1 -b .ri
%patch3 -p1 -b .undefined
%ifarch %arm
%patch4 -p1
%endif
%patch5 -p1 -b .stdout~
%patch6 -p1 -b .shared~
%patch7 -p1 -b .aarch64

autoreconf -fi
touch configure.in

%build
CFLAGS=`echo %optflags | sed 's/-fomit-frame-pointer//'`
%configure2_5x	--enable-shared \
		--disable-rpath \
		--enable-wide-getaddrinfo \
		--enable-pthread \
		--with-sitedir=%{_prefix}/lib/ruby/%{abiver}/site_ruby \
		--with-vendordir=%{_prefix}/lib/ruby/%{abiver}/vendor_ruby \
		--with-rubylibprefix=%{_prefix}/lib/ruby
%make

%install
%makeinstall_std install-doc

install -d %{buildroot}%{_docdir}/%{name}-%{version}
cp -a COPYING* ChangeLog README* ToDo sample %{buildroot}%{_docdir}/%{name}-%{version}
install -m644 %{SOURCE1} -D %{buildroot}%{_docdir}/%{name}-%{version}/FAQ.html

install -m644 %{SOURCE4} -D %{buildroot}%{_datadir}/emacs/site-lisp/ruby-mode.el

install -d %{buildroot}%{_sysconfdir}/emacs/site-start.d
cat <<EOF >%{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.el
(autoload 'ruby-mode "ruby-mode" "Ruby editing mode." t)
(add-to-list 'auto-mode-alist '("\\\\.rb$" . ruby-mode))
(add-to-list 'interpreter-mode-alist '("ruby" . ruby-mode))
EOF

tar -C %{buildroot}%{_docdir}/%{name}-%{version} -xjf %{SOURCE2}
mv %{buildroot}%{_docdir}/%{name}-%{version}/ProgrammingRuby-*/{html/*,}
rm -rf %{buildroot}%{_docdir}/%{name}-%{version}/ProgrammingRuby-*/{html,xml}/

# Make the file/dirs list, filtering out tcl/tk and devel files
find %{buildroot}%{_prefix}/lib/ruby/%{abiver} \
          \( -not -type d -printf "%%p\n" \) \
          -or \( -type d -printf "%%%%dir %%p\n" \) \
| sed -e 's#%{buildroot}##g' \
| egrep -v '/(tcl)?tk|(%{my_target_cpu}-%{_target_os}/.*[ha]$)' > %{name}.list

# Fix scripts permissions and location
find %{buildroot} sample -type f | file -i -f - | grep text | cut -d: -f1 >text.list
cat text.list | xargs chmod 0644
#  Magic grepping to get only files with '#!' in the first line
cat text.list | xargs grep -n '^#!' | grep ':1:#!' | cut -d: -f1 >shebang.list
cat shebang.list | xargs sed -i -e 's|/usr/local/bin|/usr/bin|; s|\./ruby|/usr/bin/ruby|'
cat shebang.list | xargs chmod 0755

%check
make test

%files -f %{name}.list
%dir %{_docdir}/%{name}-%{version}
%doc %{_docdir}/%{name}-%{version}/README
%doc %{_docdir}/%name
%{_bindir}/*
%dir %{_prefix}/lib/%{name}/
%{_mandir}/*/*
%{_datadir}/emacs/site-lisp/*
%dir %_prefix/lib/%name/gems/%abiver/gems
%dir %_prefix/lib/%name/gems/%abiver/gems/rake-*
%dir %_prefix/lib/%name/gems/%abiver/gems/rake-*/bin
%{_prefix}/lib/%{name}/gems/%{abiver}/gems/rake-*/bin/rake
%dir %{_prefix}/lib/%{name}/gems/%{abiver}/gems/rdoc-*
%dir %{_prefix}/lib/%{name}/gems/%{abiver}/gems/rdoc-*/bin
%{_prefix}/lib/%{name}/gems/%{abiver}/gems/rdoc-*/bin/rdoc
%{_prefix}/lib/%{name}/gems/%{abiver}/gems/rdoc-*/bin/ri
%dir %_prefix/lib/%name/gems/%abiver/specifications
%{_prefix}/lib/%{name}/gems/%{abiver}/specifications/*.gemspec
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*

%files -n %{libname}
%{_libdir}/libruby.so.%{subver}*

%files doc
%{_datadir}/ri
%dir %{_docdir}/%{name}-%{version}
%{_docdir}/%{name}-%{version}/COPYING*
%{_docdir}/%{name}-%{version}/ChangeLog
%{_docdir}/%{name}-%{version}/README.*
%{_docdir}/%{name}-%{version}/FAQ.html
%{_docdir}/%{name}-%{version}/ToDo
%{_docdir}/%{name}-%{version}/sample
%{_docdir}/%{name}-%{version}/ProgrammingRuby*

%files devel
%{_includedir}/ruby-*
%{_libdir}/libruby-static.a
%{_libdir}/libruby.so
%{_libdir}/pkgconfig/ruby-%{subver}.pc

%if %{with tcltk}
%files tk
%{_prefix}/lib/%{name}/%{abiver}/%{my_target_cpu}-%{_target_os}/tcltk*
%{_prefix}/lib/%{name}/%{abiver}/%{my_target_cpu}-%{_target_os}/tk*
%{_prefix}/lib/%{name}/%{abiver}/tcltk*
%{_prefix}/lib/%{name}/%{abiver}/tk*
%endif


%changelog
* Wed May 16 2012 Bernhard Rosenkraenzer <bero@bero.eu> 1.9.3.p194-2
+ Revision: 799161
- Obsolete ruby-RubyGems, it's part of ruby in 1.9.x

