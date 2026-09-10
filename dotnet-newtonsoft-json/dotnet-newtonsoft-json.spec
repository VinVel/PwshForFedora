# There is no native debuginfo/debugsource in a pure managed assembly.
%global debug_package %{nil}
Name:           dotnet-newtonsoft-json
Version:        13.0.4
Release:        1%{?dist}
Summary:        Json.NET library for .NET
License:        MIT
URL:            https://github.com/JamesNK/Newtonsoft.Json
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-8.0
BuildRequires:  aspnetcore-targeting-pack-8.0

%description
Json.NET (Newtonsoft.Json) is a high-performance JSON framework for .NET,
built from the upstream source for framework-dependent Fedora applications.

%prep
%autosetup -n Newtonsoft.Json-%{version}

# The upstream project also builds legacy .NET Framework/netstandard1.x
# targets and enables release-only analyzers/SourceLink. PowerShell consumes
# the net8.0 library only; keep those unrelated targets out of the
# Fedora build and avoid introducing their network-only package graph.
sed -i \
  -e '/Microsoft.CodeAnalysis.NetAnalyzers/d' \
  -e '/Microsoft.SourceLink.GitHub/d' \
  Src/Newtonsoft.Json/Newtonsoft.Json.csproj

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export NUGET_PACKAGES="%{_builddir}/nuget-packages"
mkdir -p "$NUGET_PACKAGES" "%{_builddir}/nuget-feed"

# Fedora's source-built SDK artifact is the offline NuGet source for the
# framework/reference packages selected by the .NET 10 SDK.  It is not a
# downloaded upstream binary NuGet artifact.
source_built_artifacts=$(rpm -ql dotnet-sdk-10.0-source-built-artifacts | sed -n '/source-built-artifacts.*\.tar\.gz$/p' | head -n1)
tar -xzf "$source_built_artifacts" -C "%{_builddir}/nuget-feed" \
  --wildcards \
  'Microsoft.AspNetCore.App.Ref.[0-9]*.nupkg' \
  'Microsoft.NETCore.App.Ref.[0-9]*.nupkg' \
  'Microsoft.NET.ILLink.Tasks.[0-9]*.nupkg'

# No remote source is permitted here. If upstream adds package dependencies,
# they must be supplied by Fedora/RPM before this restore is run.
dotnet restore Src/Newtonsoft.Json/Newtonsoft.Json.csproj \
  --ignore-failed-sources --source "%{_builddir}/nuget-feed" \
  --source /usr/lib64/dotnet/library-packs \
  -p:NuGetAudit=false -p:LibraryFrameworks=net8.0 \
  -p:EnablePackageValidation=false
dotnet build Src/Newtonsoft.Json/Newtonsoft.Json.csproj --no-restore \
  --configuration Release -p:LibraryFrameworks=net8.0 \
  -p:EnablePackageValidation=false

%install
install -Dpm0644 Src/Newtonsoft.Json/bin/Release/net8.0/Newtonsoft.Json.dll \
  %{buildroot}%{_libdir}/dotnet/%{name}/Newtonsoft.Json.dll

%check
test -s Src/Newtonsoft.Json/bin/Release/net8.0/Newtonsoft.Json.dll

%files
%license LICENSE.md
%{_libdir}/dotnet/%{name}/Newtonsoft.Json.dll

%changelog
* Thu Sep 10 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 13.0.4-1
- Initial COPR staging package, built from upstream source.
