import sys
import colorama
import time
import argparse
import json
import httpx
import hashlib
import urllib
import requests
import re
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style, init

colorama.init(autoreset=True)

# Updated User-Agent to a more recent one
DEFAULT_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 311.0.2.24.111 (iPhone14,5; iOS 16_6; en_US; en-US; scale=3.00; 1170x2532; 548339867)'
WEB_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def banner():
    print("                _ _   _                ")
    print("  _  _ ___ ___ (_) |_( )___  _ __  ___ ")
    print(r" | || / -_|_-< | |  _|/(_-< | '  \/ -_)")
    print(r"  \_, \___/__/ |_|\__| /__/ |_|_|_\___|")
    print("  |__/                                 ")
    print("\n\tTwitter: " + Fore.MAGENTA + "@blackeko5")


def getUserId(username, sessionsId):
    """Get Instagram user ID using the web API"""
    cookies = {'sessionid': sessionsId}
    headers = {
        'User-Agent': WEB_USER_AGENT,
        'X-IG-App-ID': '936619743392459',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'https://www.instagram.com/{username}/',
    }
    
    try:
        # Try the web profile API first
        r = requests.get(f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}',
                headers=headers, cookies=cookies, timeout=10)
        
        if r.status_code == 200:
            info = r.json()
            if 'data' in info and 'user' in info['data'] and info['data']['user']:
                user_id = info['data']['user']['id']
                return {"id": user_id, "error": None}
        
        # Fallback: Try scraping the profile page
        r = requests.get(f'https://www.instagram.com/{username}/',
                headers={'User-Agent': WEB_USER_AGENT}, cookies=cookies, timeout=10)
        
        if r.status_code == 200:
            # Look for user ID in the page source
            match = re.search(r'"profilePage_(\d+)"', r.text)
            if match:
                return {"id": match.group(1), "error": None}
            
            # Alternative pattern
            match = re.search(r'"user_id":"(\d+)"', r.text)
            if match:
                return {"id": match.group(1), "error": None}
        
        return {"id": None, "error": "User not found or rate limit"}
    except Exception as e:
        return {"id": None, "error": f"Error: {str(e)}"}


def getInfo(username, sessionId):
    """Get detailed user info from Instagram"""
    userId = getUserId(username, sessionId)
    if userId["error"] is not None:
        return {"user": None, "error": userId["error"]}
    
    cookies = {'sessionid': sessionId}
    headers = {
        'User-Agent': DEFAULT_USER_AGENT,
        'X-IG-App-ID': '936619743392459',
    }
    
    try:
        response = requests.get(f'https://i.instagram.com/api/v1/users/{userId["id"]}/info/',
                      headers=headers, cookies=cookies, timeout=10)
        
        if response.status_code == 200:
            info = response.json()
            if "user" in info:
                infoUser = info["user"]
                infoUser["userID"] = userId["id"]
                return {"user": infoUser, "error": None}
        
        # Try alternative web API
        headers_web = {
            'User-Agent': WEB_USER_AGENT,
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest',
        }
        response = requests.get(f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}',
                      headers=headers_web, cookies=cookies, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'user' in data['data'] and data['data']['user']:
                user = data['data']['user']
                # Convert web format to match expected format
                infoUser = {
                    'username': user.get('username', ''),
                    'full_name': user.get('full_name', ''),
                    'userID': user.get('id', userId["id"]),
                    'is_verified': user.get('is_verified', False),
                    'is_business': user.get('is_business_account', False),
                    'is_private': user.get('is_private', False),
                    'follower_count': user.get('edge_followed_by', {}).get('count', 0),
                    'following_count': user.get('edge_follow', {}).get('count', 0),
                    'media_count': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                    'external_url': user.get('external_url', '') or '',
                    'biography': user.get('biography', '') or '',
                    'public_email': user.get('business_email', '') or '',
                    'public_phone_number': user.get('business_phone_number', '') or '',
                    'hd_profile_pic_url_info': {'url': user.get('profile_pic_url_hd', '') or user.get('profile_pic_url', '')}
                }
                return {"user": infoUser, "error": None}
        
        return {"user": None, "error": "Could not fetch user info"}
    except Exception as e:
        return {"user": None, "error": f"Error: {str(e)}"}


def advanced_lookup(username):
    """Advanced lookup using Instagram's user lookup API"""
    USERS_LOOKUP_URL = 'https://i.instagram.com/api/v1/users/lookup/'
    
    # Modern approach without signature (Instagram has changed this)
    headers = {
        "Accept-Language": "en-US",
        "User-Agent": DEFAULT_USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate",
        "X-IG-App-ID": "936619743392459",
        "X-FB-HTTP-Engine": "Liger",
        "Connection": "close"
    }
    
    data = {
        'q': username,
        'skip_recovery': '1'
    }
    
    try:
        r = httpx.post(USERS_LOOKUP_URL, headers=headers, data=data, timeout=10)
        if r.status_code == 200:
            rep = r.json()
            return {"user": rep, "error": None}
        else:
            return {"user": None, "error": "rate limit or API changed"}
    except Exception as e:
        return {"user": None, "error": f"rate limit: {str(e)}"}


def search_instagram_users(name, sessionId):
    """Search for Instagram users using Instagram's search API"""
    headers = {
        'User-Agent': WEB_USER_AGENT,
        'X-IG-App-ID': '936619743392459',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': '*/*',
    }
    cookies = {'sessionid': sessionId}
    
    try:
        # Use Instagram's web search API
        search_url = f'https://www.instagram.com/web/search/topsearch/?query={urllib.parse.quote(name)}'
        response = requests.get(search_url, headers=headers, cookies=cookies, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            account_list = []
            
            if 'users' in data:
                for user in data['users']:
                    if 'user' in user:
                        username = user['user'].get('username', '')
                        full_name = user['user'].get('full_name', '').lower()
                        # Add @ prefix to match original format
                        if username:
                            # Prioritize if name matches
                            if name.lower() in full_name:
                                account_list.insert(0, f'@{username}')
                            else:
                                account_list.append(f'@{username}')
            
            if account_list:
                return {"user": account_list, "error": None}
            else:
                return {"user": None, "error": "No users found"}
        else:
            return {"user": None, "error": f"Search failed with status {response.status_code}"}
    except Exception as e:
        return {"user": None, "error": f"Search error: {str(e)}"}


def dumpor(name, sessionId=None):
    """Legacy function name wrapper - now uses Instagram search"""
    if sessionId:
        return search_instagram_users(name, sessionId)
    
    # Fallback: return empty if no session
    return {"user": None, "error": "Session ID required for search"}


def main():
    banner()
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('required arguments')
    parser.add_argument('-s', '--sessionid',
                        help="Instagram session ID", required=True)
    parser.add_argument(
        '-n', '--name', help="Target name & surname", required=True)
    parser.add_argument('-e', '--email', help="Target email", required=True)
    parser.add_argument(
        '-p', '--phone', help="Target phone number", required=True)
    parser.add_argument('-t', '--timeout',
                        help="Timeout between requests", required=False)

    args = parser.parse_args()

    sessionsId = args.sessionid
    name = args.name
    email = args.email
    phone = args.phone
    timeout = args.timeout

    print(Fore.CYAN + "\n[*] Searching for accounts matching: " + name)
    
    # Pass sessionId to dumpor for Instagram search
    accounts = dumpor(name, sessionsId)

    if accounts["user"] is None:
        print(Fore.RED + "[!] " + accounts["error"])
        sys.exit(1)
    else:
        print(Fore.GREEN + f"[+] Found {len(accounts['user'])} potential accounts\n")
        
        for account in accounts["user"]:
            name_f, email_f, phone_f = 0, 0, 0
            username = account[1:] if account.startswith('@') else account
            
            print(Fore.CYAN + f"[*] Checking account: {username}")
            infos = getInfo(username, sessionsId)
            
            if infos["user"] is None:
                print(Fore.YELLOW + f"[!] {infos['error']}")
                continue
            
            infos = infos["user"]

            print("\nInformation about      : " + infos.get("username", "N/A"))
            full_name = infos.get("full_name", "")
            if full_name and full_name.lower() == name.lower():
                print(Fore.GREEN + "Full Name              : " +
                      full_name + " \u2713")
                name_f = 1
            else:
                print("Full Name              : " + full_name)
            print("User ID                : " + str(infos.get("userID", "N/A")))
            print("Verified               : " + str(infos.get('is_verified', False)))
            print("Is business Account    : " + str(infos.get("is_business", False)))
            print("Is private Account     : " + str(infos.get("is_private", False)))
            print("Followers              : " + str(infos.get("follower_count", 0)))
            print("Following              : " + str(infos.get("following_count", 0)))
            print("Number of posts        : " + str(infos.get("media_count", 0)))
            print("External URL           : " + str(infos.get("external_url", "") or "N/A"))
            print("Biography              : " + str(infos.get("biography", "") or "N/A"))
            
            # Check public email
            public_email = infos.get("public_email", "")
            if public_email:
                try:
                    if (email and email != ' ' and 
                        public_email[0] == email[0] and 
                        public_email.split('@')[0][-1] == email.split('@')[0][-1] and
                        public_email.split('@')[1] == email.split('@')[1]):
                        print(Fore.GREEN + "Public email           : " +
                              public_email + " \u2713")
                        email_f = 1
                    else:
                        print("Public email           : " + public_email)
                except (IndexError, AttributeError):
                    print("Public email           : " + public_email)

            # Check public phone
            public_phone = str(infos.get("public_phone_number", ""))
            if public_phone and public_phone != '':
                try:
                    if (phone and phone != ' ' and 
                        public_phone.split()[0] == phone.split()[0] and 
                        public_phone[-2:] == phone[-2:]):
                        print(Fore.GREEN + "Public phone number    : " +
                              public_phone + " \u2713")
                        phone_f = 1
                    else:
                        print("Public phone           : " + public_phone)
                except (IndexError, AttributeError):
                    print("Public phone           : " + public_phone)

            # Advanced lookup (may be rate limited)
            other_infos = advanced_lookup(username)
            if other_infos["error"]:
                print(Fore.YELLOW + "[!] Advanced lookup: " + other_infos["error"])
            elif other_infos["user"]:
                if "message" in other_infos["user"]:
                    if other_infos["user"]["message"] == "No users found":
                        print("Advanced lookup        : No additional data")
                    else:
                        print(Fore.YELLOW + "[!] " + other_infos["user"]["message"])
                else:
                    # Check obfuscated email
                    obf_email = other_infos["user"].get("obfuscated_email", "")
                    if obf_email:
                        try:
                            if (email and email != ' ' and 
                                obf_email[0] == email[0] and 
                                len(obf_email) > 8 and
                                obf_email[8] == email.split('@')[0][-1] and
                                obf_email.split('@')[1] == email.split('@')[1]):
                                print(Fore.GREEN + "Obfuscated email       : " +
                                      obf_email + " \u2713")
                                email_f = 1
                            else:
                                print("Obfuscated email       : " + obf_email)
                        except (IndexError, AttributeError):
                            print("Obfuscated email       : " + obf_email)
                    else:
                        print("No obfuscated email found")

                    # Check obfuscated phone
                    obf_phone = str(other_infos["user"].get("obfuscated_phone", ""))
                    if obf_phone and obf_phone != '':
                        try:
                            if (phone and phone != ' ' and 
                                obf_phone.split()[0] == phone.split()[0] and 
                                obf_phone[-2:] == phone[-2:]):
                                print(Fore.GREEN + "Obfuscated phone       : " +
                                      obf_phone + " \u2713")
                                phone_f = 1
                            else:
                                print("Obfuscated phone       : " + obf_phone)
                        except (IndexError, AttributeError):
                            print("Obfuscated phone       : " + obf_phone)
                    else:
                        print("No obfuscated phone found")

            # Profile picture
            pic_info = infos.get("hd_profile_pic_url_info", {})
            pic_url = pic_info.get("url", "") if isinstance(pic_info, dict) else str(pic_info)
            if pic_url:
                print("Profile Picture        : " + pic_url + "\n")
            else:
                print("Profile Picture        : N/A\n")

            user_id = str(infos.get("userID", "unknown"))
            
            if(name_f + email_f + phone_f == 3):
                print(Fore.CYAN + "[*] " + Fore.GREEN + "Profile ID " +
                      user_id + " match level: HIGH\n")
                usr_choice = input("Stop searching? Y/n ")
                if(usr_choice.lower() == 'y'):
                    sys.exit(0)

            elif(name_f + email_f + phone_f == 2):
                print(Fore.CYAN + "[*] " + Fore.YELLOW + "Profile ID " +
                      user_id + " match level: MEDIUM\n")

            elif(name_f + email_f + phone_f == 1):
                print(Fore.CYAN + "[*] " + Fore.RED + "Profile with ID " +
                      user_id + " match level: LOW\n")

            print("-"*30)

            if timeout:
                time.sleep(int(timeout))


if __name__ == "__main__":
    main()