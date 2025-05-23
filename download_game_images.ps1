# PowerShell script to download game cover images
$baseDir = "$PSScriptRoot\static\images\games"
$webClient = New-Object System.Net.WebClient

# Create an array of game IDs and their corresponding URLs
$gameImages = @{
    'witcher3' = 'https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg'
    'skyrim' = 'https://upload.wikimedia.org/wikipedia/en/1/15/The_Elder_Scrolls_V_Skyrim_cover.png'
    'masseffect2' = 'https://upload.wikimedia.org/wikipedia/en/0/05/MassEffect2_cover.PNG'
    'baldursgate3' = 'https://upload.wikimedia.org/wikipedia/en/3/3a/Baldur%27s_Gate_3_cover_art.jpg'
    'overwatch' = 'https://upload.wikimedia.org/wikipedia/en/5/51/Overwatch_cover_art.jpg'
    'leagueoflegends' = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/League_of_Legends_2019_vector.svg/800px-League_of_Legends_2019_vector.svg.png'
    'valorant' = 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Valorant_logo_-_pink_color_version.svg/800px-Valorant_logo_-_pink_color_version.svg.png'
    'apexlegends' = 'https://upload.wikimedia.org/wikipedia/en/thumb/d/db/Apex_legends_cover.jpg/220px-Apex_legends_cover.jpg'
    'civ6' = 'https://upload.wikimedia.org/wikipedia/en/3/3b/Civilization_VI_cover_art.jpg'
    'warhammer' = 'https://upload.wikimedia.org/wikipedia/en/0/02/Total_War_Warhammer_cover_art.jpg'
    'ageofempires2' = 'https://upload.wikimedia.org/wikipedia/en/8/8e/Age_of_Empires_II_-_The_Age_of_Kings_Coverart.png'
    'stellaris' = 'https://upload.wikimedia.org/wikipedia/en/9/94/Stellaris_cover_art.jpg'
    'animalcrossing' = 'https://upload.wikimedia.org/wikipedia/en/1/1f/Animal_Crossing_New_Horizons.jpg'
    'zelda' = 'https://upload.wikimedia.org/wikipedia/en/c/c6/The_Legend_of_Zelda_Breath_of_the_Wild.jpg'
    'stardewvalley' = 'https://upload.wikimedia.org/wikipedia/en/f/fd/Logo_of_Stardew_Valley.png'
    'hades' = 'https://upload.wikimedia.org/wikipedia/en/c/cc/Hades_cover_art.jpg'
    'mario' = 'https://upload.wikimedia.org/wikipedia/en/3/32/Super_Mario_World_Coverart.png'
    'chronotrigger' = 'https://upload.wikimedia.org/wikipedia/en/a/a7/Chrono_Trigger.jpg'
    'ff7' = 'https://upload.wikimedia.org/wikipedia/en/c/c2/Final_Fantasy_VII_Box_Art.jpg'
    'castlevania' = 'https://upload.wikimedia.org/wikipedia/en/0/0f/Castlevania_-_Symphony_of_the_Night_cover.png'
    'ff14' = 'https://upload.wikimedia.org/wikipedia/en/6/6d/Final_Fantasy_XIV%2C_A_Realm_Reborn_box_cover.jpg'
    'persona5' = 'https://upload.wikimedia.org/wikipedia/en/b/b0/Persona_5_cover_art.jpg'
    'nier' = 'https://upload.wikimedia.org/wikipedia/en/2/21/Nier_Automata_cover_art.jpg'
    'dragonquest11' = 'https://upload.wikimedia.org/wikipedia/en/4/4e/Dragon_Quest_XI_cover_art.jpg'
}

# Create the directory if it doesn't exist
if (-not (Test-Path -Path $baseDir)) {
    New-Item -ItemType Directory -Path $baseDir | Out-Null
}

# Download each image
foreach ($game in $gameImages.GetEnumerator()) {
    $gameId = $game.Key
    $imageUrl = $game.Value
    $extension = [System.IO.Path]::GetExtension($imageUrl).Split('?')[0]  # Remove query parameters if any
    $fileName = "${gameId}${extension}"
    $filePath = Join-Path -Path $baseDir -ChildPath $fileName
    
    Write-Host "Downloading ${gameId}..."
    try {
        $webClient.DownloadFile($imageUrl, $filePath)
        Write-Host "  -> Saved to ${filePath}"
    } catch {
        Write-Host "  -> Failed to download ${gameId}: $_" -ForegroundColor Red
    }
}

Write-Host "Done downloading game cover images!" -ForegroundColor Green
