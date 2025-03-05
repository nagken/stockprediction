# clean_large_files.ps1
# This script finds and removes large files from a Git repository and force pushes the changes.

# Set the threshold for large files (50MB)
$threshold = 50MB

Write-Host "🔍 Scanning Git repository for files larger than $threshold..."

# Step 1: Find Large Files
$largeFiles = git rev-list --objects --all | ForEach-Object { ($_ -split " ")[1] } | Where-Object { $_ -and (Test-Path $_) } | ForEach-Object { Get-Item $_ | Where-Object { $_.Length -gt $threshold } }

if ($largeFiles.Count -eq 0) {
    Write-Host "✅ No large files found. Exiting..."
    exit
}

Write-Host "⚠️  The following large files were found in your Git repository:"
$largeFiles | ForEach-Object { Write-Host "  - $_" }

# Step 2: Remove Large Files from Git History
Write-Host "🚀 Removing large files from Git history..."
foreach ($file in $largeFiles) {
    git filter-repo --path $file.FullName --invert-paths --force
}

# Step 3: Cleanup Git Repository
Write-Host "🧹 Cleaning up Git history..."
git reflog expire --expire=now --all
git gc --prune=now

# Step 4: Force Push Cleaned Repository
Write-Host "📤 Force pushing cleaned repository to GitHub..."
git push origin main --force

Write-Host "🎉 Cleanup complete! Your repository is now free of large files."
