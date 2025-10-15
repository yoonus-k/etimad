// Etimad Cookie Extractor
// Extracts all cookies from etimad.sa domain and formats them for Python

const statusDiv = document.getElementById('status');
const outputDiv = document.getElementById('output');
const cookiesTextPre = document.getElementById('cookiesText');
const cookieCountSpan = document.getElementById('cookieCount');
const extractBtn = document.getElementById('extractBtn');
const copyBtn = document.getElementById('copyBtn');

// Show status message
function showStatus(message, type = 'info') {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
}

// Extract cookies from all Etimad domains
async function extractCookies() {
    try {
        showStatus('🔍 جاري استخراج الكوكيز...', 'info');
        extractBtn.classList.add('loading');

        // Get all cookies for etimad.sa domains
        const domains = [
            'tenders.etimad.sa',
            'login.etimad.sa',
            '.tenders.etimad.sa',
            '.login.etimad.sa',
            '.etimad.sa',
            'etimad.sa'
        ];

        const allCookies = {};
        
        for (const domain of domains) {
            try {
                const cookies = await chrome.cookies.getAll({ domain: domain });
                cookies.forEach(cookie => {
                    // Use cookie name as key (latest value wins if duplicates)
                    allCookies[cookie.name] = cookie.value;
                });
            } catch (e) {
                console.log(`Could not get cookies for ${domain}:`, e);
            }
        }

        if (Object.keys(allCookies).length === 0) {
            showStatus('❌ لم يتم العثور على كوكيز. تأكد من تسجيل الدخول إلى موقع اعتماد', 'error');
            extractBtn.classList.remove('loading');
            outputDiv.classList.add('hidden');
            return;
        }

        // Format as Python dictionary
        let pythonCode = 'COOKIES = {\n';
        
        // Sort cookies alphabetically for consistency
        const sortedKeys = Object.keys(allCookies).sort();
        
        for (const key of sortedKeys) {
            const value = allCookies[key];
            // Escape single quotes in values
            const escapedValue = value.replace(/'/g, "\\'");
            pythonCode += `    '${key}': '${escapedValue}',\n`;
        }
        
        pythonCode += '}';

        // Display results
        cookiesTextPre.textContent = pythonCode;
        cookieCountSpan.textContent = `✅ تم استخراج ${Object.keys(allCookies).length} كوكي`;
        outputDiv.classList.remove('hidden');
        
        showStatus('✅ تم استخراج الكوكيز بنجاح!', 'success');
        extractBtn.classList.remove('loading');

    } catch (error) {
        console.error('Error extracting cookies:', error);
        showStatus('❌ حدث خطأ: ' + error.message, 'error');
        extractBtn.classList.remove('loading');
        outputDiv.classList.add('hidden');
    }
}

// Copy cookies to clipboard
async function copyCookies() {
    try {
        const text = cookiesTextPre.textContent;
        await navigator.clipboard.writeText(text);
        
        // Visual feedback
        copyBtn.textContent = '✅ تم النسخ';
        copyBtn.style.background = '#28a745';
        
        setTimeout(() => {
            copyBtn.textContent = 'نسخ';
            copyBtn.style.background = '';
        }, 2000);
        
    } catch (error) {
        console.error('Error copying to clipboard:', error);
        copyBtn.textContent = '❌ فشل النسخ';
        setTimeout(() => {
            copyBtn.textContent = 'نسخ';
        }, 2000);
    }
}

// Event listeners
extractBtn.addEventListener('click', extractCookies);
copyBtn.addEventListener('click', copyCookies);

// Check if we're on an Etimad page
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const currentTab = tabs[0];
    if (currentTab && currentTab.url && currentTab.url.includes('etimad.sa')) {
        showStatus('📍 أنت على موقع اعتماد - اضغط الزر للاستخراج', 'info');
    } else {
        showStatus('⚠️ يرجى فتح موقع tenders.etimad.sa أولاً', 'error');
    }
});
