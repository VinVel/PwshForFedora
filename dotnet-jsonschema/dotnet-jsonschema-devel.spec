%global commit a3c4e63e075f595e4039d6424a77765a6761f7d0

Name:           dotnet-jsonschema-devel
Version:        7.4.0
Release:        1%{?dist}
Summary:        NuGet development package for JsonSchema.Net
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
Requires:       dotnet-jsonschema%{?_isa} = %{version}-%{release}
BuildArch:      noarch

%description
The locally source-built NuGet package for applications compiling against
JsonSchema.Net. It is intended for an offline NuGet feed and contains no
downloaded binary NuGet artifact.

%prep
%autosetup -n json-everything-%{commit}

sed -i \
  -e '/<PackageReference Include="PolySharp"/d' \
  -e '/<PackageReference Include="Microsoft.SourceLink.GitHub"/d' \
  -e '/<SignAssembly>true<\/SignAssembly>/d' \
  -e '/<AssemblyOriginatorKeyFile>/d' \
  -e '/<PackageIcon>json-logo-256.png<\/PackageIcon>/d' \
  -e '/<None Include="\.\.\\Resources\\json-logo-256\.png"/d' \
  src/JsonSchema/JsonSchema.csproj \
  src/JsonPointer/JsonPointer.csproj \
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
dotnet pack src/JsonSchema/JsonSchema.csproj --no-restore \
  --configuration Release --output "%{_builddir}/nuget-feed" \
  -p:PackageVersion=%{version} -p:TargetFrameworks=net8.0 \
  -p:IncludeBuildOutput=true \
  -p:EnablePackageValidation=false

%install
install -Dpm0644 "%{_builddir}/nuget-feed/JsonSchema.Net.%{version}.nupkg" \
  %{buildroot}%{_datadir}/dotnet/nuget/%{name}/JsonSchema.Net.%{version}.nupkg

%check
test -s "%{buildroot}%{_datadir}/dotnet/nuget/%{name}/JsonSchema.Net.%{version}.nupkg"

%files
%license LICENSE
%{_datadir}/dotnet/nuget/%{name}/JsonSchema.Net.%{version}.nupkg

%changelog
* Fri Sep 11 2026 PowerShell Fedora Packaging <noreply@example.invalid> - 7.4.0-1
- Initial COPR staging NuGet development package, built from upstream source commit.
