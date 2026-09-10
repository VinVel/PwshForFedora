%global debug_package %{nil}

Name:           dotnet-json-more-net
Version:        2.1.1
Release:        1%{?dist}
Summary:        Additional JSON types and converters for .NET
License:        MIT
URL:            https://github.com/json-everything/json-everything
Source0:        %{url}/archive/refs/tags/more-v%{version}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-8.0
BuildRequires:  aspnetcore-targeting-pack-8.0

%description
Json.More.Net provides additional JSON types and converters based on
System.Text.Json. This package is built from the upstream source for use by
framework-dependent Fedora .NET applications.

%prep
%autosetup -n json-everything-more-v%{version}

# PolySharp and SourceLink are private upstream build tooling. They are not
# needed for the net8.0 assembly consumed by PowerShell and would otherwise
# add network-only restore dependencies.
sed -i \
  -e '/<PackageReference Include="PolySharp"/d' \
  -e '/<PackageReference Include="Microsoft.SourceLink.GitHub"/d' \
  -e '/<SignAssembly>true<\/SignAssembly>/d' \
  -e '/<AssemblyOriginatorKeyFile>/d' \
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

dotnet restore src/Json.More/Json.More.csproj \
  --ignore-failed-sources \
  --source "%{_builddir}/nuget-feed" \
  --source /usr/lib64/dotnet/library-packs \
  -p:NuGetAudit=false -p:TargetFrameworks=net8.0 \
  -p:EnablePackageValidation=false
dotnet build src/Json.More/Json.More.csproj --no-restore \
  --configuration Release -p:TargetFrameworks=net8.0 \
  -p:EnablePackageValidation=false

%install
install -Dpm0644 src/Json.More/bin/Release/net8.0/Json.More.dll \
  %{buildroot}%{_libdir}/dotnet/%{name}/Json.More.dll

%check
test -s src/Json.More/bin/Release/net8.0/Json.More.dll

%files
%license LICENSE
%{_libdir}/dotnet/%{name}/Json.More.dll

%changelog
* Thu Sep 10 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 2.1.1-1
- Initial COPR staging package, built from upstream source.
