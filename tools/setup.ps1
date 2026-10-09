# One-time setup: fetch the ReXGlue SDK submodules, pin imgui, and apply the Skate 2 SDK patch.
$ErrorActionPreference = 'Continue'
$root = Split-Path $PSScriptRoot -Parent
$sdk = Join-Path $root 'third_party\rexglue-sdk'
Set-Location $root

git submodule update --init third_party/rexglue-sdk
Set-Location $sdk

# The SDK pins an imgui commit that no longer exists upstream; use the nearest
# commit from the same day and fetch every other submodule at its pinned commit.
git submodule update --init thirdparty/imgui 2>$null
git -C thirdparty/imgui fetch origin docking 2>$null
git -C thirdparty/imgui checkout -q d94d0f3649c99d9a026518214f796aaacde707fe
$subs = git config --file .gitmodules --get-regexp path | ForEach-Object { ($_ -split ' ')[1] } | Where-Object { $_ -ne 'thirdparty/imgui' }
foreach ($s in $subs) { git submodule update --init --recursive -- $s }

# Apply the Skate 2 fixes to the SDK unless they are already in place.
$patch = Join-Path $root 'patches\rexglue-sdk.patch'
git apply --reverse --check $patch 2>$null
if ($LASTEXITCODE -eq 0) { 'SDK patch already applied' } else { git apply $patch; if ($LASTEXITCODE -eq 0) { 'SDK patch applied' } else { 'SDK patch FAILED'; exit 1 } }
