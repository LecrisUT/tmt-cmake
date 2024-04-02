Name:           python-tmt-cmake
Version:        0.0.0
Release:        %autorelease
Summary:        TMT CMake plugin

License:        GPL-3.0-or-later
URL:            https://github.com/LecrisUT/tmt-cmake
Source:         %{pypi_source tmt_cmake}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
A tmt plugin for CMake prepare and testing framework
}

%description %_description

%package -n python3-tmt-cmake
Summary:        %{summary}
Requires:       cmake
%description -n python3-tmt-cmake %_description


%prep
%autosetup -n tmt-cmake-%{version}


%generate_buildrequires
%pyproject_buildrequires -x test


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files tmt_cmake


%check
%pytest


%files -n python3-tmt-cmake -f %{pyproject_files}
%license LICENSE.md
%doc README.md


%changelog
%autochangelog
