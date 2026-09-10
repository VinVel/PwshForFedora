%global debug_package %{nil}

Name:           dotnet-humanizer-core
Version:        2.14.1
Release:        1%{?dist}
Summary:        Human-friendly string and date formatting for .NET
License:        MIT
URL:            https://github.com/Humanizr/Humanizer
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-8.0

%description
Humanizer is a .NET library that turns strings, type names, enum fields and
dates into human-friendly representations. This package is built from the
upstream source for framework-dependent Fedora .NET applications.

%prep
%autosetup -n Humanizer-%{version}

# These are private release/build tools and are not needed for the selected
# net8.0 library target. Do not introduce network-only restore inputs.
sed -i \
  -e '/<PackageReference Include="Nerdbank.GitVersioning"/d' \
  -e '/<PackageReference Include="Microsoft.SourceLink.GitHub"/d' \
  -e '/<SignAssembly>true<\/SignAssembly>/d' \
  -e '/<AssemblyOriginatorKeyFile>/d' \
  src/Directory.build.props src/Humanizer/Humanizer.csproj

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export NUGET_PACKAGES="%{_builddir}/nuget-packages"
mkdir -p "$NUGET_PACKAGES" "%{_builddir}/nuget-feed"

dotnet restore src/Humanizer/Humanizer.csproj \
  --ignore-failed-sources \
  --source /usr/lib64/dotnet/library-packs \
  -p:NuGetAudit=false -p:TargetFrameworks=net8.0 \
  -p:EnablePackageValidation=false
dotnet build src/Humanizer/Humanizer.csproj --no-restore \
  --configuration Release -p:TargetFrameworks=net8.0 \
  -p:EnablePackageValidation=false

%install
install -Dpm0644 src/Humanizer/bin/Release/net8.0/Humanizer.dll \
  %{buildroot}%{_libdir}/dotnet/%{name}/Humanizer.dll

%check
test -s src/Humanizer/bin/Release/net8.0/Humanizer.dll

%files
%license LICENSE
%{_libdir}/dotnet/%{name}/Humanizer.dll

%changelog
* Thu Sep 10 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 2.14.1-1
- Initial COPR staging package, built from upstream source.
