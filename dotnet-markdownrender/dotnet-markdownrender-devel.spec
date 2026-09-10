%global debug_package %{nil}
%global commit 8be5371470e57c106c4eb5e6297115741dfcd8ba

Name:           dotnet-markdownrender-devel
Version:        7.2.1
Release:        1%{?dist}
Summary:        NuGet development package for PowerShell Markdown renderer
License:        MIT
URL:            https://github.com/PowerShell/MarkdownRender
Source0:        %{url}/archive/%{commit}.tar.gz
BuildArch:      noarch

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-10.0
BuildRequires:  dotnet-markdig-devel >= 0.44.0

%description
This package contains the source-built Microsoft.PowerShell.MarkdownRender
NuGet package for use by offline Fedora .NET builds. It does not contain a
private copy of the runtime assembly.

%prep
%autosetup -n MarkdownRender-%{commit}

sed -i \
  -e '/<DelaySign>true<\/DelaySign>/d' \
  -e '/<AssemblyOriginatorKeyFile>/d' \
  -e '/<SignAssembly>true<\/SignAssembly>/d' \
  -e 's#<TargetFramework>netstandard2.0</TargetFramework>#<TargetFramework>net10.0</TargetFramework>#' \
  -e 's#Version="0.31.0"#Version="0.44.0"#' \
  src/Microsoft.PowerShell.MarkdownRender.csproj

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

dotnet restore src/Microsoft.PowerShell.MarkdownRender.csproj \
  --ignore-failed-sources \
  --source "%{_builddir}/nuget-feed" \
  --source /usr/lib64/dotnet/library-packs \
  --source /usr/share/dotnet/nuget/dotnet-markdig-devel \
  -p:NuGetAudit=false -p:TargetFrameworks=net10.0 \
  -p:EnablePackageValidation=false
dotnet build src/Microsoft.PowerShell.MarkdownRender.csproj --no-restore \
  --configuration Release -p:TargetFrameworks=net10.0 \
  -p:Version=%{version} -p:AssemblyVersion=%{version}.0 \
  -p:FileVersion=%{version}.0 -p:EnablePackageValidation=false
dotnet pack src/Microsoft.PowerShell.MarkdownRender.csproj --no-restore \
  --configuration Release --output "%{_builddir}/nuget-feed" \
  -p:PackageVersion=%{version} -p:TargetFrameworks=net10.0 \
  -p:IncludeBuildOutput=true -p:EnablePackageValidation=false

%install
install -Dpm0644 \
  %{_builddir}/nuget-feed/Microsoft.PowerShell.MarkdownRender.%{version}.nupkg \
  %{buildroot}%{_datadir}/dotnet/nuget/%{name}/Microsoft.PowerShell.MarkdownRender.%{version}.nupkg

%check
test -s %{buildroot}%{_datadir}/dotnet/nuget/%{name}/Microsoft.PowerShell.MarkdownRender.%{version}.nupkg

%files
%license LICENSE
%{_datadir}/dotnet/nuget/%{name}/Microsoft.PowerShell.MarkdownRender.%{version}.nupkg

%changelog
* Fri Sep 11 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 7.2.1-1
- Initial COPR staging package, built from upstream source.
