%global debug_package %{nil}
%global commit a3c4e63e075f595e4039d6424a77765a6761f7d0

Name:           dotnet-jsonschema
Version:        7.4.0
Release:        1%{?dist}
Summary:        JSON Schema implementation for .NET
License:        MIT
URL:            https://github.com/json-everything/json-everything
Source0:        %{url}/archive/%{commit}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-8.0
BuildRequires:  aspnetcore-targeting-pack-8.0
BuildRequires:  dotnet-json-more-net-devel >= 2.1.1
BuildRequires:  dotnet-json-pointer-net-devel >= 5.3.1
BuildRequires:  dotnet-humanizer-core-devel >= 2.14.1

Requires:       dotnet-json-more-net%{?_isa} >= 2.1.1
Requires:       dotnet-json-pointer-net%{?_isa} >= 5.3.1
Requires:       dotnet-humanizer-core%{?_isa} >= 2.14.1

%description
JsonSchema.Net is a JSON Schema implementation built on the System.Text.Json
namespace. This package is built from upstream source for framework-dependent
Fedora .NET applications.

%prep
%autosetup -n json-everything-%{commit}

# These optional release-time dependencies and signing inputs are not needed
# for the Fedora net8.0 build. JsonSchema builds JsonPointer and Json.More as
# local project references, so clean all three projects consistently.
sed -i \
  -e '/<PackageReference Include="PolySharp"/d' \
  -e '/<PackageReference Include="Microsoft.SourceLink.GitHub"/d' \
  -e '/<SignAssembly>true<\/SignAssembly>/d' \
  -e '/<AssemblyOriginatorKeyFile>/d' \
  src/JsonSchema/JsonSchema.csproj \
  src/JsonPointer/JsonPointer.csproj \
  src/Json.More/Json.More.csproj

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

dotnet restore src/JsonSchema/JsonSchema.csproj \
  --ignore-failed-sources \
  --source "%{_builddir}/nuget-feed" \
  --source /usr/lib64/dotnet/library-packs \
  --source %{_datadir}/dotnet/nuget/dotnet-json-more-net-devel \
  --source %{_datadir}/dotnet/nuget/dotnet-json-pointer-net-devel \
  --source %{_datadir}/dotnet/nuget/dotnet-humanizer-core-devel \
  -p:NuGetAudit=false -p:TargetFrameworks=net8.0 \
  -p:EnablePackageValidation=false
dotnet build src/JsonSchema/JsonSchema.csproj --no-restore \
  --configuration Release -p:TargetFrameworks=net8.0 \
  -p:EnablePackageValidation=false

%install
install -Dpm0644 src/JsonSchema/bin/Release/net8.0/JsonSchema.Net.dll \
  %{buildroot}%{_libdir}/dotnet/%{name}/JsonSchema.Net.dll

%check
test -s src/JsonSchema/bin/Release/net8.0/JsonSchema.Net.dll

%files
%license LICENSE
%{_libdir}/dotnet/%{name}/JsonSchema.Net.dll

%changelog
* Fri Sep 11 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 7.4.0-1
- Initial COPR staging package, built from upstream source commit.
