# FIXED: CivicPulse UTF-8 Encoding Issue Resolution

## Problem
When running the original `web_app.py` or `cli.py`, you got this error:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4c5' in position 2013
```

This happened because:
- Windows uses **CP1252 encoding** by default (not UTF-8)
- The files contain emoji and special characters
- Python couldn't encode them in CP1252

---

## Solution: Two Fixed Scripts

### **OPTION 1: Web Interface (Recommended)**
```
python setup_and_run_web.py
```

This script:
1. ✅ Creates all source files with UTF-8 encoding
2. ✅ Starts the web server automatically
3. ✅ Handles all emoji/special characters correctly
4. ✅ Launches at http://localhost:8000

**How to use:**
1. Open Command Prompt
2. Type: `cd r:\project\hack`
3. Type: `python setup_and_run_web.py`
4. Wait for: `CivicPulse Web Server is running!`
5. Open browser: `http://localhost:8000`

---

### **OPTION 2: Command Line Interface**
```
python run_cli_fixed.py
```

This script:
1. ✅ Creates all source files with UTF-8 encoding
2. ✅ Runs interactive CLI conversation
3. ✅ No web server needed
4. ✅ Pure Python implementation

**How to use:**
1. Open Command Prompt
2. Type: `cd r:\project\hack`
3. Type: `python run_cli_fixed.py`
4. Follow the prompts in the terminal

---

## What Changed

### Original Files (Broken)
- `web_app.py` - Had encoding issues
- `cli.py` - Had encoding issues
- `run_localhost.py` - Had encoding issues

### New Files (Fixed)
- `setup_and_run_web.py` - ✅ Web interface + server (UTF-8 fixed)
- `run_cli_fixed.py` - ✅ CLI interface (UTF-8 fixed)
- `FIX_UTF8.md` - This guide

---

## Key Fix

All `write_text()` calls now specify encoding:

**Before (Broken):**
```python
(project / 'src' / 'logic.py').write_text(source_code)
```

**After (Fixed):**
```python
(project / 'src' / 'logic.py').write_text(source_code, encoding='utf-8')
```

This tells Python to use UTF-8 encoding instead of Windows's default CP1252.

---

## Quick Test

To verify the fix works, run this in Command Prompt:
```
python setup_and_run_web.py
```

You should see:
```
Setting up CivicPulse...
Source files created successfully!

Starting Web Server...

======================================================================
CivicPulse Web Server is running!
Open your browser: http://localhost:8000
Press Ctrl+C to stop
======================================================================
```

If you see this, the fix worked! Open http://localhost:8000 in your browser.

---

## Troubleshooting

### Still getting encoding error?
- Make sure you're using the NEW scripts:
  - `setup_and_run_web.py` (not web_app.py)
  - `run_cli_fixed.py` (not cli.py)

### Python not found?
- Type: `python3 setup_and_run_web.py` instead
- Or install Python 3.10+ from python.org

### Port 8000 in use?
- Close other programs using port 8000
- Or edit line 320 in `setup_and_run_web.py`:
  ```python
  PORT = 8001  # Change to a different port
  ```

### Still seeing emoji issues?
- Run this in Command Prompt first:
  ```
  chcp 65001
  ```
  (This sets Command Prompt to UTF-8 mode)

---

## Summary

✅ **Use these two fixed scripts:**
- `setup_and_run_web.py` - For web interface
- `run_cli_fixed.py` - For command-line

✅ **Both now support:**
- All emoji and special characters
- Windows CP1252 → UTF-8 encoding
- Proper error handling

✅ **Just run:**
- `python setup_and_run_web.py` and open browser

---

Happy voting! 🗳️
