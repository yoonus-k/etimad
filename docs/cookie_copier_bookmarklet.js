// Cookie Copier Bookmarklet
// Drag this to your bookmarks bar or save as a bookmark

javascript:(function(){
  const cookieNames = [
    'login.etimad.ssk4',
    'MobileAuthCookie',
    'TS00000000076',
    'TS01369bcc',
    'TS0145fac2',
    'TS0147caf9',
    'TS0147caf9030',
    'TS0f286a6e029',
    'TS0f286a6e077',
    'TS1c26927f027',
    'TSPD_101',
    'TSPD_101_DID',
    'url',
    'X-CSRF-TOKEN-SSK3',
    '.AspNetCore.Antiforgery',
    '_ga',
    '_gid',
    'ADRUM',
    'Dammam',
    'Identity.TwoFactorUserId',
    'idsrv.session',
    'langcookie',
    'language',
    'SameSite'
  ];
  
  const cookies = document.cookie.split('; ').filter(c => 
    cookieNames.some(name => c.startsWith(name + '='))
  );
  const cookieString = cookies.join('; ');
  
  // Copy to clipboard
  navigator.clipboard.writeText(cookieString).then(() => {
    alert('✅ تم نسخ ' + cookies.length + ' كوكيز!\n\nالصقها في نافذة التطبيق.\n\n' + cookieString.substring(0, 100) + '...');
  });
})();


// Usage Instructions:
// 1. Open Chrome and log in to https://tenders.etimad.sa
// 2. Click this bookmarklet in your bookmarks bar
// 3. It will copy the necessary cookies to your clipboard
// 4. Paste the cookies into the app when prompted
// 5. Done! 
// AAZZZ🎉