param(
    [string]$PythonPath = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$actualRoot = [System.IO.Path]::GetFullPath(
    (git -C $repoRoot rev-parse --show-toplevel).Trim()
)
if (-not [string]::Equals(
    $actualRoot,
    $repoRoot,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    throw "Refusing to configure hooks outside the release repository: $actualRoot"
}

git -C $repoRoot config --local core.hooksPath .githooks
git -C $repoRoot config --local credential.https://github.com.username jhf-dev
git -C $repoRoot config --local --unset-all credential.https://github.com.helper 2>$null
git -C $repoRoot config --local --add credential.https://github.com.helper '""'
git -C $repoRoot config --local --add credential.https://github.com.helper manager
if ([string]::IsNullOrWhiteSpace($PythonPath)) {
    $PythonPath = (Get-Command python -CommandType Application -ErrorAction Stop).Source
}
if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    throw "Configured Python does not exist: $PythonPath"
}
$resolvedPython = (Resolve-Path -LiteralPath $PythonPath).Path
git -C $repoRoot config --local wind3.python $resolvedPython
if ((git -C $repoRoot config --local --get core.hooksPath).Trim() -ne ".githooks") {
    throw "Failed to install tracked release hooks."
}
if ((git -C $repoRoot config --local --get wind3.python).Trim() -ne $resolvedPython) {
    throw "Failed to pin the release hook Python."
}
if ((git -C $repoRoot config --local --get credential.https://github.com.username).Trim() -ne "jhf-dev") {
    throw "Failed to pin the release GitHub credential namespace."
}
$localHelpers = @(git -C $repoRoot config --local --get-all credential.https://github.com.helper)
if ($localHelpers[-1].Trim() -ne "manager") {
    throw "Failed to pin Git Credential Manager for the release repository."
}

& $resolvedPython (Join-Path $repoRoot ".release\validate_release.py") `
    --root $repoRoot `
    --check-git-identity
