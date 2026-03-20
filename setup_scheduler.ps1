# PowerShell script to create a scheduled task for Moltbook engagement

$taskName = "MoltbookEngagement"
$pythonPath = (Get-Command python).Source
$scriptPath = "c:\My Projects\End Of 2026\Moltbook Ai agent\moltbook_engage.py"
$workingDir = "c:\My Projects\End Of 2026\Moltbook Ai agent"

# Create the action
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath -WorkingDirectory $workingDir

# Create the trigger (every 30 minutes)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30)

# Create the task settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
try {
    # Remove existing task if it exists
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    
    # Register new task
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Moltbook engagement - checks feed and interacts every 30 minutes"
    
    Write-Host "✅ Scheduled task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Name: $taskName" -ForegroundColor Cyan
    Write-Host "Frequency: Every 30 minutes" -ForegroundColor Cyan
    Write-Host "Script: $scriptPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To view the task: Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
    Write-Host "To disable: Disable-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
    Write-Host "To enable: Enable-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
    Write-Host "To remove: Unregister-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
}
catch {
    Write-Host "❌ Error creating scheduled task: $_" -ForegroundColor Red
    exit 1
}
