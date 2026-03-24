# Update Dossier Scheduled Tasks with full Python path

$pythonPath = "C:\Users\Carzl\AppData\Local\Microsoft\WindowsApps\python.exe"
$workingDir = "C:\Users\Carzl\Documents\Projects\Python Stuff\Reddit Helper Helper"
$scriptArgs = "mydossier.py update"

# Update 6AM task
$action6AM = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptArgs -WorkingDirectory $workingDir
Set-ScheduledTask -TaskName "DossierDigest_6AM" -Action $action6AM
Write-Host "Updated DossierDigest_6AM"

# Update 5PM task
$action5PM = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptArgs -WorkingDirectory $workingDir
Set-ScheduledTask -TaskName "DossierDigest_5PM" -Action $action5PM
Write-Host "Updated DossierDigest_5PM"

Write-Host "`nTask configuration updated successfully!"
