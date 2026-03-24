# Windows Scheduled Task Setup for Daily Dossier

## Quick Setup

### 1. Test the Command First
```cmd
cd Z:\shared\Python Stuff\Pet\Reddit Helper Helper
python mydossier.py update
```

This should run the full digest and update GitHub Pages.

---

## Option A: Manual Task Scheduler Setup (Recommended)

### Morning Task (6 AM)

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create Task** (not "Create Basic Task")
   - Click "Create Task..." in the right sidebar

3. **General Tab:**
   - Name: `Daily Dossier - 6 AM`
   - Description: `Runs daily business dossier at 6 AM PST`
   - Run whether user is logged on or not: **Checked**
   - Run with highest privileges: **Checked**
   - Configure for: **Windows 10/11**

4. **Triggers Tab:**
   - Click "New..."
   - Begin the task: **On a schedule**
   - Settings: **Daily**
   - Start: **6:00:00 AM**
   - Recur every: **1 days**
   - Enabled: **Checked**
   - Click OK

5. **Actions Tab:**
   - Click "New..."
   - Action: **Start a program**
   - Program/script: `python`
   - Add arguments: `mydossier.py update`
   - Start in: `Z:\shared\Python Stuff\Pet\Reddit Helper Helper`
   - Click OK

6. **Conditions Tab:**
   - **Uncheck** "Start the task only if the computer is on AC power"
   - **Check** "Wake the computer to run this task" (if you want it to wake)

7. **Settings Tab:**
   - Allow task to be run on demand: **Checked**
   - Run task as soon as possible after a scheduled start is missed: **Checked**
   - If the task fails, restart every: **10 minutes**
   - Attempt to restart up to: **3 times**

8. **Click OK** and enter your Windows password if prompted

### Evening Task (5 PM)

Repeat the above steps with these changes:
- Name: `Daily Dossier - 5 PM`
- Trigger: **5:00:00 PM**

---

## Option B: Import XML (Advanced)

### Morning Task XML
Save as `DailyDossier_6AM.xml`:

```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2026-02-13T21:45:00</Date>
    <Author>Drew Shady</Author>
    <Description>Daily Business Dossier - 6 AM Update</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-02-14T06:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-21-CHANGE-THIS-TO-YOUR-USER-SID</UserId>
      <LogonType>Password</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT10M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>mydossier.py update</Arguments>
      <WorkingDirectory>Z:\shared\Python Stuff\Pet\Reddit Helper Helper</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
```

To import:
1. Save XML file
2. Open Task Scheduler
3. Click "Import Task..." in right sidebar
4. Select the XML file
5. Adjust the `<UserId>` in XML or edit task after import

---

## Testing

### Test Manually
```cmd
cd Z:\shared\Python Stuff\Pet\Reddit Helper Helper
python mydossier.py update
```

### Test from Task Scheduler
1. Open Task Scheduler
2. Find "Daily Dossier - 6 AM" or "Daily Dossier - 5 PM"
3. Right-click → **Run**
4. Check "Last Run Result" column (should show "0x0" for success)

### View Task History
1. Right-click task → **Properties**
2. Go to **History** tab
3. Look for Event ID 200 (task started) and 201 (task completed)

---

## Troubleshooting

### Task doesn't run
1. Check task is **Enabled** (right-click → Enable)
2. Verify "Next Run Time" is set correctly
3. Check if "Run whether user is logged on or not" is checked
4. Make sure Python is in your PATH

### Task runs but fails
1. Check "Last Run Result" in Task Scheduler
2. View logs in Task History
3. Test manually: `python mydossier.py update`
4. Check working directory is correct

### Python not found
Add Python to PATH or use full path:
```
C:\Python311\python.exe
```

Instead of just:
```
python
```

### Network drive issues
If `Z:\` isn't available at boot:
1. In Triggers, add a delay: "Delay task for: 5 minutes"
2. Or change "Start in" to a local directory and use full Z:\ paths in arguments

---

## Log Files

Create log files for debugging:

### Option 1: Redirect Output
Change Action to:
- Program: `cmd.exe`
- Arguments: `/c python mydossier.py update > Z:\shared\Python Stuff\Pet\Reddit Helper Helper\logs\dossier_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1`

### Option 2: Task Scheduler Logs
View in Event Viewer:
1. Press `Win + R`, type `eventvwr.msc`
2. Navigate to: Applications and Services Logs → Microsoft → Windows → TaskScheduler → Operational
3. Look for your task name

---

## Manual Run Shortcut

Create a desktop shortcut:
1. Right-click Desktop → New → Shortcut
2. Location: `python "Z:\shared\Python Stuff\Pet\Reddit Helper Helper\mydossier.py" update`
3. Name: `Update Daily Dossier`
4. Right-click shortcut → Properties → Change Icon (optional)

Or use the .bat file:
1. Create shortcut to `Z:\shared\Python Stuff\Pet\Reddit Helper Helper\mydossier.bat`
2. Edit shortcut to add argument: `mydossier.bat update`

---

## Monitoring

### Check if tasks are running
```cmd
schtasks /query /tn "Daily Dossier - 6 AM" /fo LIST /v
schtasks /query /tn "Daily Dossier - 5 PM" /fo LIST /v
```

### Force run a task
```cmd
schtasks /run /tn "Daily Dossier - 6 AM"
```

### Disable a task
```cmd
schtasks /change /tn "Daily Dossier - 6 AM" /disable
```

### Enable a task
```cmd
schtasks /change /tn "Daily Dossier - 6 AM" /enable
```

---

## Email Notifications (Optional)

To get email when task completes:

1. In Task Scheduler, right-click task → Properties
2. Go to **Actions** tab
3. Click "New..."
4. Action: **Send an e-mail** (if available)
   - Note: This feature is deprecated in newer Windows versions
5. Alternative: Use a PowerShell script to send email after `mydossier.py` completes

---

## Alternative: Python Scheduler

If Task Scheduler is unreliable, run a Python scheduler:

```python
# scheduler.py
import schedule
import time
import subprocess
import os

os.chdir('Z:/shared/Python Stuff/Pet/Reddit Helper Helper/')

def run_dossier():
    subprocess.run(['python', 'mydossier.py', 'update'])

schedule.every().day.at("06:00").do(run_dossier)
schedule.every().day.at("17:00").do(run_dossier)

print("Scheduler started. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(60)
```

Run with:
```cmd
python scheduler.py
```

Keep this running in background or set up as Windows Service.

---

## Verification

After setup, verify:
1. ✅ Both tasks appear in Task Scheduler
2. ✅ Tasks are **Enabled**
3. ✅ "Next Run Time" shows tomorrow at 6 AM / 5 PM
4. ✅ Manual run test: `python mydossier.py update` works
5. ✅ Check GitHub Pages after manual run: https://DiamondDeals.github.io/daily-dossier/dossier.html

---

**Last Updated:** 2026-02-13  
**Maintained By:** Bishop (OpenClaw AI Agent)
