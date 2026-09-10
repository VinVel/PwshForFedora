Name:           dotnet-newtonsoft-json-devel
Version:        13.0.4
Release:        1%{?dist}
Summary:        NuGet development package for Json.NET
License:        MIT
URL:            https://github.com/JamesNK/Newtonsoft.Json
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-8.0
BuildRequires:  aspnetcore-targeting-pack-8.0
Requires:       dotnet-newtonsoft-json%{?_isa} = %{version}-%{release}
BuildArch:      noarch

%description
The source-built NuGet package for applications compiling against
dotnet-newtonsoft-json. The package is produced locally for use by an offline
NuGet feed and contains no downloaded binary NuGet artifact.

%prep
%autosetup -n Newtonsoft.Json-%{version}

sed -i \
  -e '/Microsoft.CodeAnalysis.NetAnalyzers/d' \
  -e '/Microsoft.SourceLink.GitHub/d' \
  Src/Newtonsoft.Json/Newtonsoft.Json.csproj

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export NUGET_PACKAGES="%{_builddir}/nuget-packages"
export NUGET_XMLDOC_MODE=skip
mkdir -p "$NUGET_PACKAGES" "%{_builddir}/nuget-feed"

source_built_artifacts=$(rpm -ql dotnet-sdk-10.0-source-built-artifacts | sed -n '/source-built-artifacts.*\.tar\.gz$/p' | head -n1)
tar -xzf "$source_built_artifacts" -C "%{_builddir}/nuget-feed" \
  --wildcards \
  'Microsoft.AspNetCore.App.Ref.[0-9]*.nupkg' \
  'Microsoft.NETCore.App.Ref.[0-9]*.nupkg' \
  'Microsoft.NET.ILLink.Tasks.[0-9]*.nupkg'

# This package is deliberately restored from local SDK assets only. Any new
# upstream dependency must be represented by another Fedora/RPM feed package.
dotnet restore Src/Newtonsoft.Json/Newtonsoft.Json.csproj \
  --ignore-failed-sources --source "%{_builddir}/nuget-feed" \
  --source /usr/lib64/dotnet/library-packs \
  -p:NuGetAudit=false -p:LibraryFrameworks=net8.0 \
  -p:EnablePackageValidation=false
dotnet pack Src/Newtonsoft.Json/Newtonsoft.Json.csproj --no-restore \
  --configuration Release --output "%{_builddir}/nuget-feed" \
  -p:PackageVersion=%{version} -p:LibraryFrameworks=net8.0 \
  -p:EnablePackageValidation=false

%install
install -Dpm0644 "%{_builddir}/nuget-feed/Newtonsoft.Json.%{version}.nupkg" \
  %{buildroot}%{_datadir}/dotnet/nuget/%{name}/Newtonsoft.Json.%{version}.nupkg

%check
test -s "%{buildroot}%{_datadir}/dotnet/nuget/%{name}/Newtonsoft.Json.%{version}.nupkg"

%files
%license LICENSE.md
%{_datadir}/dotnet/nuget/%{name}/Newtonsoft.Json.%{version}.nupkg

%changelog
* Thu Sep 10 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 13.0.4-1
- Initial COPR staging NuGet development package, built from upstream source.
