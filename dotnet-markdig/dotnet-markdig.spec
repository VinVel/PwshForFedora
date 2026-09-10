%global debug_package %{nil}

Name:           dotnet-markdig
Version:        0.44.0
Release:        1%{?dist}
Summary:        Markdown processor for .NET
License:        BSD-2-Clause
URL:            https://github.com/xoofx/markdig
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-8.0
BuildRequires:  aspnetcore-targeting-pack-8.0

%description
Markdig is a fast, powerful and extensible Markdown processor for .NET. This
package provides the Markdig.Signed assembly required by PowerShell's
Markdown-related components and is built from upstream source.

%prep
%autosetup -n markdig-%{version}

# MinVer is upstream release tooling only. The Fedora build supplies its
# version explicitly and does not restore release-time NuGet packages.
sed -i '/<PackageReference Include="MinVer">/,/<\/PackageReference>/d' \
  src/Markdig/Markdig.targets

# Do not carry upstream strong-name private key material into the build output.
sed -i \
  -e '/<SignAssembly>true<\/SignAssembly>/d' \
  -e '/<AssemblyOriginatorKeyFile>/d' \
  src/Markdig.Signed/Markdig.Signed.csproj

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export NUGET_PACKAGES="%{_builddir}/nuget-packages"
mkdir -p "$NUGET_PACKAGES" "%{_builddir}/nuget-feed"

dotnet restore src/Markdig.Signed/Markdig.Signed.csproj \
  --ignore-failed-sources \
  --source /usr/lib64/dotnet/library-packs \
  -p:NuGetAudit=false -p:TargetFrameworks=net8.0 \
  -p:Version=%{version} -p:AssemblyVersion=%{version}.0 \
  -p:FileVersion=%{version}.0 -p:EnablePackageValidation=false
dotnet build src/Markdig.Signed/Markdig.Signed.csproj --no-restore \
  --configuration Release -p:TargetFrameworks=net8.0 \
  -p:Version=%{version} -p:AssemblyVersion=%{version}.0 \
  -p:FileVersion=%{version}.0 -p:EnablePackageValidation=false

%install
install -Dpm0644 src/Markdig.Signed/bin/Release/net8.0/Markdig.Signed.dll \
  %{buildroot}%{_libdir}/dotnet/%{name}/Markdig.Signed.dll

%check
test -s src/Markdig.Signed/bin/Release/net8.0/Markdig.Signed.dll

%files
%license license.txt
%{_libdir}/dotnet/%{name}/Markdig.Signed.dll

%changelog
* Fri Sep 11 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 0.44.0-1
- Initial COPR staging package, built from upstream source.
