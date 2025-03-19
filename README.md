

ControlBot - Remote PC Control via Telegram
=========================================

Short Description
-----------------
ControlBot is a powerful utility for remotely controlling Windows PCs via Telegram. It allows you to gather system information, manage files, stress the system, extract data from browsers and messengers, capture webcam shots, list processes, and manage startup—all through simple Telegram chat commands.

Detailed Description
--------------------
ControlBot is a client application that runs on target PCs and communicates with a Telegram bot. Each client registers in the chat with a unique identifier (IP address), enabling control over multiple computers simultaneously. The program relies solely on Telegram for communication, simplifying setup and eliminating the need for additional servers or network configurations.

Key Features:
- System Information: Retrieve IP, location, Windows version, key, and uptime.
- File Management: Create, edit, and delete files on the remote PC.
- System Stress: Generate high CPU and disk load for testing.
- Data Stealer: Extract passwords and data from browsers (Chrome, Firefox, Edge, Opera, Yandex), Telegram, Discord, plus a desktop screenshot.
- Webcam & Clipboard: Capture webcam shots and retrieve clipboard contents.
- Processes: View a list of active processes (PID and name).
- Startup Management: Add the program to startup with file protection or remove it.
- PC Selection: Manage multiple PCs by selecting from a numbered list.

Technical Details:
- Language: Python 3.
- Dependencies: Uses `telebot`, `pycryptodome`, `opencv-python`, `pillow`, `psutil`, `pywin32`, `requests`, `wmi`.
- Encryption: Decrypts browser passwords using Windows DPAPI and AES-GCM.
- Compilation: Supports building to `.exe` with `pyinstaller`.

Examples of Use
---------------
1. Client Registration
   - Run `app.exe` on a PC.
   - Telegram message:
     [192.168.1.100] Program started:
     IP: 192.168.1.100
     Location: Moscow, Russia
     Windows Version: Windows-10-10.0.19045-SP0
     Windows Key: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
     Uptime: 2:34:56.789123

2. Selecting a PC
   - Send: `Select PC`
   - Bot response:
     Available PCs:
     1. IP: 192.168.1.100, Location: Moscow, Russia
     2. IP: 192.168.1.101, Location: Saint Petersburg, Russia
     Enter the PC number to select:
   - Enter: `1` to choose IP `192.168.1.100`.

3. Getting System Info
   - Command: `Get System Info`
   - Response:
     [192.168.1.100] IP: 192.168.1.100
     Location: Moscow, Russia
     Windows Version: Windows-10-10.0.19045-SP0
     Windows Key: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
     Uptime: 2:35:12.345678

4. Editing a File
   - Command: `Edit File`
   - Prompt: [192.168.1.100] Enter file path and new content (e.g., 'C:\\test.txt Hello World'):
   - Input: `C:\test.txt New text`
   - Response: [192.168.1.100] File C:\test.txt edited successfully

5. Stealing Data
   - Command: `Steal Data`
   - Result:
     - Desktop screenshot with caption: [192.168.1.100] Desktop shot
     - Message:
       [192.168.1.100] Stolen Data:
       Chrome: URL: https://example.com, Email: user@example.com, Password: pass123
       Opera: URL: https://site.com, Email: test@site.com, Password: qwerty
       Telegram: Found file D877F783D5D3EF8C1
       Discord: Found data in 000001.ldb

6. Webcam Shot
   - Command: `Take Webcam Shot`
   - Result: Photo in Telegram with caption [192.168.1.100] Webcam shot

Installation and Setup Instructions
-----------------------------------
Requirements:
- OS: Windows 10 or higher.
- Python: Version 3.7+ (recommended 3.13).
- Permissions: Must run as administrator.
- Internet: Required for Telegram and geolocation.

Installing Dependencies:
1. Open a command prompt as administrator.
2. Install required libraries:
   pip install requests wmi telebot psutil pywin32 pillow pyinstaller opencv-python pycryptodome

Setup:
1. Telegram Configuration:
   - Create a bot via BotFather (https://t.me/BotFather) and get a TELEGRAM_TOKEN.
   - Find your TELEGRAM_CHAT_ID (e.g., via @userinfobot).
   - Update the code with your values:
     TELEGRAM_TOKEN = "YOUR_TOKEN"
     TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

2. Saving the Code:
   - Copy the code into a file named `app.py` and save it, e.g., to `C:\Users\Your_Name\Desktop\sss\app.py`.

Running via Python:
1. Navigate to the folder:
   cd C:\Users\Your_Name\Desktop\sss
2. Run the script:
   python app.py
   or
   py app.py

Compiling to .exe:
1. Ensure all dependencies are installed.
2. Compile:
   pyinstaller --onefile --noconsole app.py
   - If dependency issues occur, use:
     pyinstaller --onefile --noconsole --hidden-import=pycryptodome --hidden-import=opencv-python app.py
3. Find `app.exe` in the `dist` folder.

Running the .exe:
1. Navigate to the `dist` folder:
   cd C:\Users\Your_Name\Desktop\sss\dist
2. Run as administrator:
   - Via Explorer: Right-click → "Run as Administrator".
   - Via CMD (as admin):
     app.exe

Troubleshooting
---------------
Error: `ModuleNotFoundError: No module named 'Cryptodome'`
- Install `pycryptodome`:
  pip install pycryptodome

Error: "No permission to open file"
- Run the `.exe` as administrator.

Program not sending messages to Telegram:
- Verify `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID`.
- Ensure an internet connection is available.

License
-------
This project is distributed "as is" with no warranties. Use at your own risk.
