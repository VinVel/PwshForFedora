Name:           dotnet-json-more-net-devel
Version:        2.1.1
Release:        1%{?dist}
Summary:        NuGet development package for Json.More.Net
License:        MIT
URL:            https://github.com/json-everything/json-everything
Source0:        %{url}/archive/refs/tags/more-v%{version}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  dotnet-runtime-10.0
BuildRequires:  dotnet-sdk-10.0-source-built-artifacts
BuildRequires:  dotnet-targeting-pack-8.0
BuildRequires:  aspnetcore-targeting-pack-8.0
Requires:       dotnet-json-more-net%{?_isa} = %{version}-%{release}
BuildArch:      noarch

%description
The locally source-built NuGet package for applications compiling against
dotnet-json-more-net. It is intended for an offline NuGet feed and contains
no downloaded binary NuGet artifact.

%prep
%autosetup -n json-everything-more-v%{version}

sed -i \
  -e '/<PackageReference Include="PolySharp"/d' \
  -e '/<PackageReference Include="Microsoft.SourceLink.GitHub"/d' \
  -e '/<SignAssembly>true<\/SignAssembly>/d' \
  -e '/<AssemblyOriginatorKeyFile>/d' \
  src/Json.More/Json.More.csproj

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export NUGET_PACKAGES="%{_builddir}/nuget-packages"
export NUGET_XMLDOC_MODE=skip
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
dotnet pack src/Json.More/Json.More.csproj --no-restore \
  --configuration Release --output "%{_builddir}/nuget-feed" \
  -p:PackageVersion=%{version} -p:TargetFrameworks=net8.0 \
  -p:EnablePackageValidation=false

%install
install -Dpm0644 "%{_builddir}/nuget-feed/Json.More.Net.%{version}.nupkg" \
  %{buildroot}%{_datadir}/dotnet/nuget/%{name}/Json.More.Net.%{version}.nupkg

%check
test -s "%{buildroot}%{_datadir}/dotnet/nuget/%{name}/Json.More.Net.%{version}.nupkg"

%files
%license LICENSE
%{_datadir}/dotnet/nuget/%{name}/Json.More.Net.%{version}.nupkg

%changelog
* Thu Sep 10 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 2.1.1-1
- Initial COPR staging NuGet development package, built from upstream source.
