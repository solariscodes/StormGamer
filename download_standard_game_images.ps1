# PowerShell script to download standard game cover images
$baseDir = "$PSScriptRoot\static\images\games"
$webClient = New-Object System.Net.WebClient

# Create the directory if it doesn't exist
if (-not (Test-Path -Path $baseDir)) {
    New-Item -ItemType Directory -Path $baseDir | Out-Null
}

# Standard game images to download
$gamesToDownload = @(
    @{ 
        id = 'witcher3'
        url = 'https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg'
    },
    @{ 
        id = 'zelda-botw'
        url = 'https://upload.wikimedia.org/wikipedia/en/c/c6/The_Legend_of_Zelda_Breath_of_the_Wild.jpg'
    },
    @{ 
        id = 'eldenring'
        url = 'https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg'
    },
    @{ 
        id = 'baldursgate3'
        url = 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0f/Baldur%27s_Gate_3_cover_art.jpg/220px-Baldur%27s_Gate_3_cover_art.jpg'
    }
)

# Download each image
foreach ($game in $gamesToDownload) {
    $gameId = $game['id']
    $imageUrl = $game['url']
    $extension = [System.IO.Path]::GetExtension($imageUrl).Split('?')[0]  # Remove query parameters if any
    $fileName = "${gameId}${extension}"
    $filePath = Join-Path -Path $baseDir -ChildPath $fileName
    
    # Skip if file already exists
    if (Test-Path -Path $filePath) {
        Write-Host "Skipping ${gameId} - already exists"
        continue
    }
    
    Write-Host "Downloading ${gameId}..."
    try {
        $webClient.DownloadFile($imageUrl, $filePath)
        Write-Host "  -> Saved to ${filePath}"
    } catch {
        Write-Host "  -> Failed to download ${gameId}: $_" -ForegroundColor Red
    }
}

Write-Host "Done downloading standard game cover images!" -ForegroundColor Green
