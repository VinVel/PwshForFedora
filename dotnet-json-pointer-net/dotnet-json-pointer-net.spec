%global debug_package %{nil}

Name:           dotnet-json-pointer-net
Version:        5.3.1
Release:        1%{?dist}
Summary:        JSON Pointer implementation for .NET
License:        MIT
URL:            https://github.com/json-everything/json-everything
Source0:        %{url}/archive/refs/tags/pointer-v%{version}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-8.0
BuildRequires:  aspnetcore-targeting-pack-8.0
BuildRequires:  dotnet-json-more-net-devel >= 2.1.1
BuildRequires:  dotnet-humanizer-core-devel >= 2.14.1

Requires:       dotnet-json-more-net%{?_isa} >= 2.1.1
Requires:       dotnet-humanizer-core%{?_isa} >= 2.14.1

%description
JsonPointer.Net implements JSON Pointer (RFC 6901) and Relative JSON
Pointer for System.Text.Json-based .NET applications. This package is built
from upstream source for framework-dependent Fedora applications.

%prep
%autosetup -n json-everything-pointer-v%{version}

sed -i \
  -e '/<PackageReference Include="PolySharp"/d' \
  -e '/<PackageReference Include="Microsoft.SourceLink.GitHub"/d' \
  -e '/<SignAssembly>true<\/SignAssembly>/d' \
  -e '/<AssemblyOriginatorKeyFile>/d' \
  src/JsonPointer/JsonPointer.csproj src/Json.More/Json.More.csproj

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export NUGET_PACKAGES="%{_builddir}/nuget-packages"
mkdir -p "$NUGET_PACKAGES" "%{_builddir}/nuget-feed"

source_built_artifacts=$(rpm -ql dotnet-sdk-10.0-source-built-artifacts | sed -n '/source-built-artifacts.*\.tar\.gz$/p' | head -n1)
tar -xzf "$source_built_artifacts" -C "%{_builddir}/nuget-feed" \
  --wildcards \
  'Microsoft.AspNetCore.App.Ref.[0-9]*.nupkg' \
  'Microsoft.NETCore.App.Ref.[0-9]*.nupkg' \
  'Microsoft.NET.ILLink.Tasks.[0-9]*.nupkg'

dotnet restore src/JsonPointer/JsonPointer.csproj \
  --ignore-failed-sources \
  --source "%{_builddir}/nuget-feed" \
  --source /usr/lib64/dotnet/library-packs \
  --source %{_datadir}/dotnet/nuget/dotnet-json-more-net-devel \
  --source %{_datadir}/dotnet/nuget/dotnet-humanizer-core-devel \
  -p:NuGetAudit=false -p:TargetFrameworks=net8.0 \
  -p:EnablePackageValidation=false
dotnet build src/JsonPointer/JsonPointer.csproj --no-restore \
  --configuration Release -p:TargetFrameworks=net8.0 \
  -p:EnablePackageValidation=false

%install
install -Dpm0644 src/JsonPointer/bin/Release/net8.0/JsonPointer.Net.dll \
  %{buildroot}%{_libdir}/dotnet/%{name}/JsonPointer.Net.dll

%check
test -s src/JsonPointer/bin/Release/net8.0/JsonPointer.Net.dll

%files
%license LICENSE
%{_libdir}/dotnet/%{name}/JsonPointer.Net.dll

%changelog
* Thu Sep 10 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 5.3.1-1
- Initial COPR staging package, built from upstream source.
