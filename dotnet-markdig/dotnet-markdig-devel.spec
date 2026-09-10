Name:           dotnet-markdig-devel
Version:        0.44.0
Release:        1%{?dist}
Summary:        NuGet development package for Markdig.Signed
License:        BSD-2-Clause
URL:            https://github.com/xoofx/markdig
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-8.0
BuildRequires:  aspnetcore-targeting-pack-8.0
Requires:       dotnet-markdig%{?_isa} = %{version}-%{release}
BuildArch:      noarch

%description
The locally source-built NuGet package for applications compiling against
Markdig.Signed. It is intended for an offline NuGet feed and contains no
downloaded binary NuGet artifact.

%prep
%autosetup -n markdig-%{version}
sed -i '/<PackageReference Include="MinVer">/,/<\/PackageReference>/d' \
  src/Markdig/Markdig.targets
sed -i \
  -e '/<SignAssembly>true<\/SignAssembly>/d' \
  -e '/<AssemblyOriginatorKeyFile>/d' \
  src/Markdig.Signed/Markdig.Signed.csproj

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export NUGET_PACKAGES="%{_builddir}/nuget-packages"
export NUGET_XMLDOC_MODE=skip
mkdir -p "$NUGET_PACKAGES" "%{_builddir}/nuget-feed"

dotnet restore src/Markdig.Signed/Markdig.Signed.csproj \
  --ignore-failed-sources --source /usr/lib64/dotnet/library-packs \
  -p:NuGetAudit=false -p:TargetFrameworks=net8.0 \
  -p:Version=%{version} -p:AssemblyVersion=%{version}.0 \
  -p:FileVersion=%{version}.0 -p:EnablePackageValidation=false
dotnet build src/Markdig.Signed/Markdig.Signed.csproj --no-restore \
  --configuration Release -p:TargetFrameworks=net8.0 \
  -p:Version=%{version} -p:AssemblyVersion=%{version}.0 \
  -p:FileVersion=%{version}.0 -p:EnablePackageValidation=false
dotnet pack src/Markdig.Signed/Markdig.Signed.csproj --no-restore \
  --configuration Release --output "%{_builddir}/nuget-feed" \
  -p:PackageVersion=%{version} -p:Version=%{version} \
  -p:AssemblyVersion=%{version}.0 -p:FileVersion=%{version}.0 \
  -p:TargetFrameworks=net8.0 -p:EnablePackageValidation=false

%install
install -Dpm0644 "%{_builddir}/nuget-feed/Markdig.Signed.%{version}.nupkg" \
  %{buildroot}%{_datadir}/dotnet/nuget/%{name}/Markdig.Signed.%{version}.nupkg

%check
test -s "%{buildroot}%{_datadir}/dotnet/nuget/%{name}/Markdig.Signed.%{version}.nupkg"

%files
%license license.txt
%{_datadir}/dotnet/nuget/%{name}/Markdig.Signed.%{version}.nupkg

%changelog
* Fri Sep 11 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 0.44.0-1
- Initial COPR staging NuGet development package, built from upstream source.
