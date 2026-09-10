Name:           dotnet-humanizer-core-devel
Version:        2.14.1
Release:        1%{?dist}
Summary:        NuGet development package for Humanizer.Core
License:        MIT
URL:            https://github.com/Humanizr/Humanizer
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-8.0
Requires:       dotnet-humanizer-core%{?_isa} = %{version}-%{release}
BuildArch:      noarch

%description
The locally source-built NuGet package for applications compiling against
dotnet-humanizer-core. It is intended for an offline NuGet feed and contains
no downloaded binary NuGet artifact.

%prep
%autosetup -n Humanizer-%{version}

sed -i \
  -e '/<PackageReference Include="Nerdbank.GitVersioning"/d' \
  -e '/<PackageReference Include="Microsoft.SourceLink.GitHub"/d' \
  -e '/<SignAssembly>true<\/SignAssembly>/d' \
  -e '/<AssemblyOriginatorKeyFile>/d' \
  src/Directory.build.props src/Humanizer/Humanizer.csproj

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export NUGET_PACKAGES="%{_builddir}/nuget-packages"
export NUGET_XMLDOC_MODE=skip
mkdir -p "$NUGET_PACKAGES" "%{_builddir}/nuget-feed"

dotnet restore src/Humanizer/Humanizer.csproj \
  --ignore-failed-sources \
  --source /usr/lib64/dotnet/library-packs \
  -p:NuGetAudit=false -p:TargetFrameworks=net8.0 \
  -p:EnablePackageValidation=false
dotnet build src/Humanizer/Humanizer.csproj --no-restore \
  --configuration Release -p:TargetFrameworks=net8.0 \
  -p:EnablePackageValidation=false
dotnet pack src/Humanizer/Humanizer.csproj --no-restore \
  --configuration Release --output "%{_builddir}/nuget-feed" \
  -p:PackageId=Humanizer.Core -p:PackageVersion=%{version} \
  -p:TargetFrameworks=net8.0 -p:EnablePackageValidation=false

%install
install -Dpm0644 "%{_builddir}/nuget-feed/Humanizer.Core.%{version}.nupkg" \
  %{buildroot}%{_datadir}/dotnet/nuget/%{name}/Humanizer.Core.%{version}.nupkg

%check
test -s "%{buildroot}%{_datadir}/dotnet/nuget/%{name}/Humanizer.Core.%{version}.nupkg"

%files
%license LICENSE
%{_datadir}/dotnet/nuget/%{name}/Humanizer.Core.%{version}.nupkg

%changelog
* Thu Sep 10 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 2.14.1-1
- Initial COPR staging NuGet development package, built from upstream source.
