# Extract Cookies from Browser Console

## Method 1: Copy for Modal (Simple Format)
Open DevTools Console (F12 → Console tab) and run:

```javascript
// Extract ALL cookies in format for the modal
const cookieNames = [
  'login.etimad.ssk4', 'MobileAuthCookie', 'TS00000000076', 'TS01369bcc',
  'TS0145fac2', 'TS0147caf9', 'TS0147caf9030', 'TS0f286a6e029',
  'TS0f286a6e077', 'TS1c26927f027', 'TSPD_101', 'TSPD_101_DID',
  'url', 'X-CSRF-TOKEN-SSK3', '.AspNetCore.Antiforgery',
  '_ga', '_gid', 'ADRUM', 'Dammam', 'Identity.TwoFactorUserId',
  'idsrv.session', 'langcookie', 'language', 'SameSite'
];
const cookies = document.cookie.split('; ').filter(c => 
  cookieNames.some(name => c.startsWith(name + '='))
);
console.log(cookies.join('; '));
copy(cookies.join('; ')); // Automatically copies to clipboard!
```

This will:
- Extract the important cookies
- Format them as: `name=value; name2=value2`
- Copy to clipboard automatically
- You can paste directly into the app modal

## Method 2: Copy for config.py (Python Dict Format)
Run this in console to get Python dictionary format:

```javascript
// Extract ALL cookies as Python dict format
const cookieNames = [
  'login.etimad.ssk4', 'MobileAuthCookie', 'TS00000000076', 'TS01369bcc',
  'TS0145fac2', 'TS0147caf9', 'TS0147caf9030', 'TS0f286a6e029',
  'TS0f286a6e077', 'TS1c26927f027', 'TSPD_101', 'TSPD_101_DID',
  'url', 'X-CSRF-TOKEN-SSK3', '.AspNetCore.Antiforgery',
  '_ga', '_gid', 'ADRUM', 'Dammam', 'Identity.TwoFactorUserId',
  'idsrv.session', 'langcookie', 'language', 'SameSite'
];
const cookieDict = {};

document.cookie.split('; ').forEach(cookie => {
  const [name, ...valueParts] = cookie.split('=');
  const value = valueParts.join('=');
  if (cookieNames.some(cn => name.startsWith(cn))) {
    cookieDict[name] = value;
  }
});

// Format as Python dict
let pythonDict = "COOKIES = {\n";
for (const [name, value] of Object.entries(cookieDict)) {
  pythonDict += `    '${name}': '${value}',\n`;
}
pythonDict += "}";

console.log(pythonDict);
copy(pythonDict);
```

This gives you code you can paste directly into `config.py`

## Method 3: All Cookies (Complete)
To get ALL cookies including less important ones:

```javascript
// Get all cookies as Python dict
let pythonDict = "COOKIES = {\n";
document.cookie.split('; ').forEach(cookie => {
  const [name, ...valueParts] = cookie.split('=');
  const value = valueParts.join('=');
  pythonDict += `    '${name}': '${value}',\n`;
});
pythonDict += "}";

console.log(pythonDict);
copy(pythonDict);
```

## Quick Steps:
1. Go to https://tenders.etimad.sa (make sure you're logged in)
2. Press F12 → Console tab
3. Paste one of the scripts above
4. Press Enter
5. The cookies are now copied to your clipboard!
6. Paste into the app modal OR directly into config.py

## Important Cookies:
- **MobileAuthCookie** - Primary authentication (required)
- **.AspNetCore.Antiforgery.uI0FgwZS2KM** - Anti-forgery token (required)
- **TSPD_101** - Security token (required)
- **TS00000000076** - Session tracking (recommended)
- **TSPD_101_DID** - Device ID (recommended)
