# create-structure.ps1
# PowerShell script to create a frontend project directory structure

$directories = @(
    "src/app",
    "src/components",
    "src/lib",
    "src/hooks",
    "src/store",
    "src/types",
    "src/services",

    "src/components/ui",
    "src/components/forms",
    "src/components/layout",
    "src/components/dashboard",

    "src/app/auth",
    "src/app/dashboard",
    "src/app/api",

    "public/icons",
    "public/images"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created: $dir"
    } else {
        Write-Host "Exists:  $dir"
    }
}

Write-Host "`n✅ Directory structure setup completed."
