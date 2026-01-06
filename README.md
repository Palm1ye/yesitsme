<p align="center">
    <img src="https://github.com/blackeko/yesitsme/blob/media/logo.png" alt="yesitsme logo">
</p>

<h3 align="center">Yes, it's me!</h3>
<p align="center">
   Instagram OSINT tool to find profiles by name, email, and phone - Updated with working API endpoints for 2026
</p>

# 💬 Description
**yesitsme** is a simple Python script which tries to find Instagram accounts associated with a specific name, e-mail and phone number.

This is an **updated fork** that works with Instagram's current API endpoints (2026). The original version relied on dumpor.com and outdated Instagram APIs that no longer function.

### What's New
- ✅ Updated Instagram API endpoints
- ✅ Uses Instagram's native search instead of dumpor.com
- ✅ Fixed user profile fetching
- ✅ Better error handling
- ✅ Works with Python 3.10+

# ⚙️ Installation
```console
git clone https://github.com/Palm1ye/yesitsme/
cd yesitsme
pip3 install -r requirements.txt
python3 yesitsme.py -s SESSION_ID -n NAME -e EMAIL -p PHONE -t TIMEOUT 
```

# 🕹️ Usage
## Argument description
- ```-s``` "SESSION_ID"
  - *sessionid* cookie of your Instagram account (use a sockpuppet account);
- ```-n``` "Name Surname"
  - Target *name* and *surname* (case insensitive);
- ```-e``` "a****z@domain.tld"
  - *First* and *last letter* of target e-mail;
- ```-p``` "+39 ** 09"
  - *Area code* and *last two digits* of target phone number;
- ```-t``` "10"
  - *Timeout* between each request (default = 0).

## Example
```console
python3 yesitsme.py -s '5t3El3650d4Z7A3jA2%Y1R70vnYn%36U3' -n "John Doe" -e "j*****e@gmail.com" -p "+39 *** *** **09" -t 10
```

## Output
Three levels of match:
- **HIGH**: name, e-mail and phone number match; 
- **MEDIUM**: name and/or e-mail and/or phone match;
- **LOW**: only one of them matches.

# 📝 Notes
- Name and e-mail (or phone number) are **mandatory**;
- To leave e-mail/phone empty, simply set ```-e/-p " "```;
- E-mail/phone asterisks are just for show and **can be omitted**;
- If omitted, timeout is zero; it's recommended to set at least 10 seconds to avoid being rate-limited;
- Phone number must be in the **same format** as in the example, i.e. it must contain the area code (including plus symbol) and the whitespace;
- When the match level is HIGH, it will prompt whether to stop or continue searching.

# 🍪 Retrieve Instagram sessionid
While logged in your Instagram account:
1. Right-click and click on Inspect Element to open the developer console;
2. Go to the **Application** tab (Chrome) or **Storage** tab (Firefox);
3. Expand the Cookies menu and copy the "sessionid" cookie value.

# 🙏🏻 Credits
- Original project by [blackeko](https://github.com/blackeko/yesitsme)
- [Toutatis](https://github.com/megadose/toutatis) for inspiration
