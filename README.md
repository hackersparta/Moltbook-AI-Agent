# Moltbook Engagement - Quick Reference

## ✅ Status
**ACTIVE** - Automated engagement running every 30 minutes

## 🎯 What It Does
- Checks feed for new posts
- Upvotes interesting technical content (up to 3 per cycle)
- Uses keyword matching: python, javascript, docker, api, AI, automation, etc.
- Builds karma and network passively

## 🎛️ Quick Commands

**Check Status:**
```powershell
Get-ScheduledTask -TaskName 'MoltbookEngagement'
```

**Run Manually Now:**
```powershell
python "c:\My Projects\End Of 2026\Moltbook Ai agent\moltbook_engage.py"
```

**Pause Automation:**
```powershell
Disable-ScheduledTask -TaskName 'MoltbookEngagement'
```

**Resume Automation:**
```powershell
Enable-ScheduledTask -TaskName 'MoltbookEngagement'
```

**View Profile:**
https://www.moltbook.com/u/Nirmals_Jarvis

## 📊 First Run Results
- ✅ Scanned 15 posts
- ✅ Upvoted 3 interesting technical posts
- ⏰ Next check in 30 minutes

## 📁 Files
- `moltbook_engage.py` - Main script
- `moltbook_credentials.json` - API key (keep secure)
- `setup_scheduler.ps1` - Task setup

## 🔐 Security
API key stored in `moltbook_credentials.json` - never share this file!
