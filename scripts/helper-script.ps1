# Helper script for committing openrouter model testing changes
# Run this script from the project root directory

Write-Host "Starting commit process..." -ForegroundColor Cyan

# Commit 1: Core test script
Write-Host "`nCommit 1: Adding core test script with env configuration and output saving" -ForegroundColor Yellow
git add open-source-models.py
git commit -m "feat: add open-source model reasoning test script`n`n- add main test script with retry logic and rate limit handling`n- load api key, url, and model list from .env`n- save test results to output/ directory with lowercase naming`n- auto-trigger result formatting after successful test"

# Commit 2: Result formatting utility
Write-Host "`nCommit 2: Adding result formatting and summary export utility" -ForegroundColor Yellow
git add format-results.py
git commit -m "feat: add result formatting and summary export script`n`n- format json test results into readable console output`n- export markdown summary of all test results`n- support multiple reasoning detail blocks per call"

# Commit 3: Git ignore configuration
Write-Host "`nCommit 3: Adding gitignore configuration" -ForegroundColor Yellow
git add .gitignore
git commit -m "chore: add gitignore for env, output, and qwen directories"

Write-Host "`nAll commits completed successfully!" -ForegroundColor Green
