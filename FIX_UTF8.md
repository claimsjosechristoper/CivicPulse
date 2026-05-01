# FIXED - How to Run CivicPulse Web Interface

## Quick Start (Recommended Solution)

### Step 1: Open Command Prompt
Press **Windows Key + R**, type:
```
cmd
```
Then press **Enter**

### Step 2: Navigate to Project
In the command window, type:
```
cd r:\project\hack
```
Press **Enter**

### Step 3: Run the Fixed Setup Script
Type:
```
python setup_and_run_web.py
```
Press **Enter**

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

### Step 4: Open Browser
Open your web browser (Chrome, Firefox, Edge, etc.) and type in the address bar:
```
http://localhost:8000
```

### Step 5: Use CivicPulse
- Click the **"Start"** button
- Answer the questions
- Follow along to completion

---

## What Was Fixed

The original `web_app.py` and `cli.py` had a Unicode encoding error when writing emoji characters to files on Windows. This is because Windows defaults to CP1252 encoding instead of UTF-8.

**Solution:** Created `setup_and_run_web.py` which:
1. ✅ Creates all source files with explicit UTF-8 encoding
2. ✅ Includes the complete web server
3. ✅ Handles all emoji and special characters correctly
4. ✅ Starts automatically after setup

---

## Stop the Server

When done, go back to the command window and press:
```
Ctrl + C
```

---

## Troubleshooting

**"Python is not recognized"**
- Make sure Python 3.10+ is installed
- Try: `python3 setup_and_run_web.py` instead

**"Port 8000 is already in use"**
- Close any other applications using port 8000
- Or change the port in the script (line 320: `PORT = 8000`)

**"Connection refused"**
- Make sure the server is still running in the command window
- Check the terminal for "CivicPulse Web Server is running!"

---

That's it! Enjoy using CivicPulse! 🗳️
