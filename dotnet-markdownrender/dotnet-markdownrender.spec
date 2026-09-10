%global debug_package %{nil}
%global commit 8be5371470e57c106c4eb5e6297115741dfcd8ba

Name:           dotnet-markdownrender
Version:        7.2.1
Release:        1%{?dist}
Summary:        PowerShell Markdown renderer for .NET
License:        MIT
URL:            https://github.com/PowerShell/MarkdownRender
Source0:        %{url}/archive/%{commit}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-10.0
BuildRequires:  dotnet-markdig-devel >= 0.44.0

Requires:       dotnet-markdig >= 0.44.0

%description
Microsoft.PowerShell.MarkdownRender provides the Markdown rendering component
used by PowerShell's Show-Markdown and ConvertFrom-Markdown cmdlets. This
package is built from the upstream source and is framework-dependent.

%prep
%autosetup -n MarkdownRender-%{commit}

# Fedora builds the unsigned assembly without upstream private signing
# material. The public key file is not copied into the build or RPM.
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

%install
install -Dpm0644 \
  src/bin/Release/net10.0/Microsoft.PowerShell.MarkdownRender.dll \
  %{buildroot}%{_libdir}/dotnet/%{name}/Microsoft.PowerShell.MarkdownRender.dll

%check
test -s %{buildroot}%{_libdir}/dotnet/%{name}/Microsoft.PowerShell.MarkdownRender.dll

%files
%license LICENSE
%{_libdir}/dotnet/%{name}/Microsoft.PowerShell.MarkdownRender.dll

%changelog
* Fri Sep 11 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 7.2.1-1
- Initial COPR staging package, built from upstream source.
