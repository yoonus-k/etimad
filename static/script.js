document.addEventListener('DOMContentLoaded', function() {
    // ===========================
    // Phase 5: Tab Navigation
    // ===========================
    
    // Tab switching logic
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            
            // Remove active class from all tabs and contents
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            btn.classList.add('active');
            const activeContent = document.getElementById(`${tabName}Tab`);
            if (activeContent) {
                activeContent.classList.add('active');
            }
            
            // Load data for specific tabs
            if (tabName === 'downloads') {
                loadDownloads();
            } else if (tabName === 'costs') {
                loadCostSummary();
            }
        });
    });
    
    // ===========================
    // Main UI Elements
    // ===========================
    
    // Button to open cookie-paste modal (matches templates/index.html)
    const updateCookiesBtn = document.getElementById('updateCookiesBtn');
    const fetchBtn = document.getElementById('fetchBtn');
    const fetchQuickBtn = document.getElementById('fetchQuickBtn');
    const checkClassificationBtn = document.getElementById('checkClassificationBtn');
    const tendersContainer = document.getElementById('tendersContainer');
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const tenderCount = document.getElementById('tenderCount');
    const connectionStatus = document.getElementById('connectionStatus');
    const keepAliveStatus = document.getElementById('keepAliveStatus');
    
    // Keep-alive status checker
    async function updateKeepAliveStatus() {
        try {
            const response = await fetch('/api/keep-alive-status');
            const data = await response.json();
            
            if (keepAliveStatus) {
                const status = data.status;
                const lastPing = data.last_ping;
                
                if (status === 'active') {
                    keepAliveStatus.textContent = `🔄 نشط - آخر تحديث: ${lastPing ? new Date(lastPing).toLocaleTimeString('ar-SA') : 'الآن'}`;
                    keepAliveStatus.style.background = '#10b981';
                    keepAliveStatus.title = `الجلسة نشطة - يتم التحديث كل دقيقة\nعدد الكوكيز: ${data.cookies_count}`;
                } else if (status === 'starting') {
                    keepAliveStatus.textContent = '🔄 جاري البدء...';
                    keepAliveStatus.style.background = '#f59e0b';
                } else if (status === 'no_cookies') {
                    keepAliveStatus.textContent = '⚠️ لا توجد كوكيز';
                    keepAliveStatus.style.background = '#ef4444';
                } else {
                    keepAliveStatus.textContent = `⚠️ خطأ: ${status}`;
                    keepAliveStatus.style.background = '#ef4444';
                }
            }
        } catch (error) {
            console.error('Failed to fetch keep-alive status:', error);
            if (keepAliveStatus) {
                keepAliveStatus.textContent = '⚠️ غير متصل';
                keepAliveStatus.style.background = '#ef4444';
            }
        }
    }
    
    // Update keep-alive status every 10 seconds
    updateKeepAliveStatus(); // Initial check
    setInterval(updateKeepAliveStatus, 10000); // Check every 10 seconds

    // Helper function to proxy Etimad URLs through our backend to avoid CORS
    function proxyEtimadUrl(etimadUrl) {
        return `/api/proxy/etimad?url=${encodeURIComponent(etimadUrl)}`;
    }

    // Wire cookie modal open
    if (updateCookiesBtn) {
        console.log('✅ Update Cookies Button Found');
        updateCookiesBtn.addEventListener('click', () => {
            console.log('🍪 Update Cookies Button Clicked');
            openCookieModal();
        });
    } else {
        console.error('❌ Update Cookies Button NOT Found');
    }
    fetchBtn.addEventListener('click', () => fetchTenders(false));
    if (fetchQuickBtn) fetchQuickBtn.addEventListener('click', () => fetchTenders(true));
    if (checkClassificationBtn) checkClassificationBtn.addEventListener('click', checkAllClassifications);

    // ---- Cookie modal workflow ----
    function openCookieModal() {
        console.log('🔓 Opening Cookie Modal');
        const modal = document.getElementById('cookieModal');
        if (!modal) {
            console.error('❌ Cookie Modal Element NOT Found');
            return showError('نافذة الكوكيز غير متوفرة');
        }
        console.log('✅ Adding active class to modal');
        modal.classList.add('active');
    }

    function closeCookieModal() {
        console.log('🔒 Closing Cookie Modal');
        const modal = document.getElementById('cookieModal');
        if (!modal) return;
        modal.classList.remove('active');
    }

    // Wire modal buttons
    const saveCookiesBtn = document.getElementById('saveCookiesBtn');
    const cancelCookiesBtn = document.getElementById('cancelCookiesBtn');
    const cookieInput = document.getElementById('cookieInput');

    if (cancelCookiesBtn) cancelCookiesBtn.addEventListener('click', closeCookieModal);
    
    // Close modal when clicking outside the content
    const cookieModal = document.getElementById('cookieModal');
    if (cookieModal) {
        cookieModal.addEventListener('click', (e) => {
            if (e.target === cookieModal) {
                console.log('🖱️ Clicked outside modal - closing');
                closeCookieModal();
            }
        });
    }

    if (saveCookiesBtn) {
        saveCookiesBtn.addEventListener('click', async function () {
            const raw = cookieInput ? cookieInput.value.trim() : '';
            if (!raw) {
                return showError('الرجاء لصق الكوكيز في الحقل أولاً');
            }

            saveCookiesBtn.disabled = true;
            saveCookiesBtn.textContent = '⏳ جاري الحفظ...';

            try {
                const resp = await fetch('/api/update-cookies', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cookies: raw })
                });

                const data = await resp.json();
                if (data.success) {
                    // Show success message with details
                    const successMsg = `✅ ${data.message}\n\n` +
                        `📊 تم حفظ ${data.cookie_count} كوكي\n` +
                        `📝 تم تحديث ملف config.py\n` +
                        `🔄 جاهز للاستخدام`;
                    
                    alert(successMsg);
                    showSuccess(data.message);
                    connectionStatus.textContent = `✅ متصل - ${data.total_tenders} منافسة`;
                    connectionStatus.style.background = '#10b981';
                    
                    // Clear the input
                    if (cookieInput) cookieInput.value = '';
                    closeCookieModal();
                } else {
                    showError(data.error || 'فشل تحديث الكوكيز');
                }
            } catch (err) {
                showError('فشل الاتصال بالخادم: ' + err.message);
            } finally {
                saveCookiesBtn.disabled = false;
                saveCookiesBtn.textContent = '💾 حفظ';
            }
        });
    }

    async function fetchTenders(quickMode = false) {
        // Show loading
        loading.style.display = 'block';
        const loadingMsg = quickMode 
            ? 'جاري جلب 10 منافسات بشكل سريع...'
            : 'جاري جلب المنافسات من موقع اعتماد... قد يستغرق هذا دقيقة أو دقيقتين';
        loading.querySelector('p').textContent = loadingMsg;
        errorDiv.style.display = 'none';
        tendersContainer.innerHTML = '';
        fetchBtn.disabled = true;
        if (fetchQuickBtn) fetchQuickBtn.disabled = true;
        if (checkClassificationBtn) checkClassificationBtn.style.display = 'none';

        try {
            const maxPages = quickMode ? 1 : 100;
            const response = await fetch(`/api/tenders?max_pages=${maxPages}`);
            const data = await response.json();

            if (data.success) {
                displayTenders(data.tenders);
                const countMsg = quickMode 
                    ? `⚡ عرض سريع: ${data.count} منافسة`
                    : `عدد المنافسات: ${data.count}`;
                tenderCount.textContent = countMsg;
                // Show the bulk classification check button
                if (checkClassificationBtn && data.count > 0) {
                    checkClassificationBtn.style.display = 'inline-block';
                }
            } else {
                // Check if it's a cookie expiry error
                if (data.action === 'update_cookies') {
                    showError(
                        `❌ ${data.error}\n\n` +
                        `⚠️ الكوكيز منتهية الصلاحية. يرجى تحديثها:\n` +
                        `1. انقر على زر "🍪 تحديث الكوكيز" أعلاه\n` +
                        `2. الصق الكوكيز الجديدة من إضافة المتصفح\n` +
                        `3. اضغط "حفظ" ثم حاول مرة أخرى`
                    );
                    
                    // Highlight the update cookies button
                    if (updateCookiesBtn) {
                        updateCookiesBtn.style.animation = 'pulse 1s infinite';
                        updateCookiesBtn.style.boxShadow = '0 0 20px rgba(239, 68, 68, 0.5)';
                    }
                } else {
                    showError(data.error || 'حدث خطأ أثناء جلب المنافسات');
                }
            }
        } catch (error) {
            showError('فشل الاتصال بالخادم: ' + error.message);
        } finally {
            loading.style.display = 'none';
            fetchBtn.disabled = false;
            if (fetchQuickBtn) fetchQuickBtn.disabled = false;
        }
    }

    function displayTenders(tenders) {
        if (tenders.length === 0) {
            tendersContainer.innerHTML = `
                <div style="text-align: center; padding: 40px; background: white; border-radius: 15px;">
                    <h2>لا توجد منافسات متاحة</h2>
                </div>
            `;
            return;
        }

        tenders.forEach(tender => {
            const card = createTenderCard(tender);
            tendersContainer.appendChild(card);
        });
    }

    function createTenderCard(tender) {
        const card = document.createElement('div');
        card.className = 'tender-card';
        card.setAttribute('data-tender-id', tender.tenderId);

        card.innerHTML = `
            <div class="tender-header">
                <h2 class="tender-title tender-name">${tender.tenderName}</h2>
                <div class="tender-actions">
                    <button class="btn-classification" data-tender-id-str="${tender.tenderIdString}">
                        🏷️ عرض التصنيف
                    </button>
                    <button class="btn-analyze">
                        🤖 تحليل بالذكاء الاصطناعي
                    </button>
                    <button class="btn-download">
                        📥 تحميل المرفقات
                    </button>
                    <button class="btn-delete">
                        🗑️ حذف
                    </button>
                </div>
            </div>

            <div class="tender-info">
                <div class="info-item">
                    <div class="info-label">الجهة</div>
                    <div class="info-value">${tender.agencyName}</div>
                </div>

                <div class="info-item">
                    <div class="info-label">المدة المتبقية</div>
                    <div class="info-value remaining-time">⏰ ${tender.remainingTime}</div>
                </div>

                <div class="info-item">
                    <div class="info-label">الرقم المرجعي</div>
                    <div class="info-value reference-number">${tender.referenceNumber}</div>
                </div>

                <div class="info-item">
                    <div class="info-label">معرف المنافسة</div>
                    <div class="info-value" style="font-family: monospace; font-size: 0.85rem; direction: ltr; text-align: right;">${tender.tenderIdString}</div>
                </div>

                <div class="info-item">
                    <div class="info-label">نوع المنافسة</div>
                    <div class="info-value">${tender.tenderType}</div>
                </div>

                <div class="info-item">
                    <div class="info-label">قيمة الوثائق</div>
                    <div class="info-value">${tender.documentPrice} ريال</div>
                </div>

                <div class="info-item classification-item" style="display: none;">
                    <div class="info-label">التصنيف</div>
                    <div class="info-value classification-value">⏳ جاري التحميل...</div>
                </div>

                <div class="info-item bundles-item" style="display: none;">
                    <div class="info-label">الحزم</div>
                    <div class="info-value bundles-value"></div>
                </div>
            </div>
        `;

        // Attach event listeners to the buttons
        const classificationBtn = card.querySelector('.btn-classification');
        const analyzeBtn = card.querySelector('.btn-analyze');
        const downloadBtn = card.querySelector('.btn-download');
        const deleteBtn = card.querySelector('.btn-delete');

        if (classificationBtn) {
            classificationBtn.addEventListener('click', function () {
                const tenderIdStr = this.getAttribute('data-tender-id-str');
                fetchAndDisplayClassification(card, tenderIdStr, this);
            });
        }

        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', function () {
                startTenderAnalysis(tender, analyzeBtn);
            });
        }

        if (downloadBtn) {
            downloadBtn.addEventListener('click', function () {
                downloadTenderDocs(tender.tenderId, downloadBtn);
            });
        }

        if (deleteBtn) {
            deleteBtn.addEventListener('click', function () {
                deleteTender(tender.tenderId);
            });
        }

        return card;
    }

    // Fetch and display classification
    async function fetchAndDisplayClassification(card, tenderIdStr, button) {
        const classificationItem = card.querySelector('.classification-item');
        const classificationValue = card.querySelector('.classification-value');
        const bundlesItem = card.querySelector('.bundles-item');
        const bundlesValue = card.querySelector('.bundles-value');
        
        // Show the classification item
        classificationItem.style.display = '';
        classificationValue.textContent = '⏳ جاري التحميل...';
        
        // Disable button
        button.disabled = true;
        const originalText = button.textContent;
        button.textContent = '⏳ جاري...';

        try {
            const response = await fetch(`/api/tender/${encodeURIComponent(tenderIdStr)}/classification`);
            const data = await response.json();

            if (data.success) {
                const classification = data.classification;
                const requiresClassification = data.requires_classification;
                const bundles = data.bundles || [];
                
                // Update display with color coding
                if (requiresClassification) {
                    classificationValue.innerHTML = `<span style="color: #dc3545; font-weight: bold;">⚠️ ${classification}</span>`;
                } else {
                    classificationValue.innerHTML = `<span style="color: #28a745; font-weight: bold;">✅ ${classification}</span>`;
                }
                
                // Show bundles if available
                if (bundles.length > 0) {
                    bundlesItem.style.display = '';
                    bundlesValue.innerHTML = bundles.map(bundle => 
                        `<div style="padding: 4px 8px; background: #f0f9ff; border-radius: 4px; margin: 2px 0; font-size: 0.9rem;">📦 ${bundle}</div>`
                    ).join('');
                }
                
                // Update button
                button.textContent = requiresClassification ? '⚠️ يتطلب تصنيف' : '✅ لا يتطلب تصنيف';
                button.style.background = requiresClassification ? '#ffc107' : '#28a745';
                button.disabled = true; // Keep disabled after fetching
            } else {
                classificationValue.textContent = '❌ فشل التحميل';
                button.textContent = originalText;
                button.disabled = false;
            }
        } catch (error) {
            classificationValue.textContent = '❌ خطأ في الاتصال';
            button.textContent = originalText;
            button.disabled = false;
            console.error('Error fetching classification:', error);
        }
    }

    // Make function global
    // Accept an optional button element so we don't rely on a global `event` variable.
    window.downloadTenderDocs = async function(tenderId, btn) {
        const button = btn || document.querySelector(`[data-tender-id="${tenderId}"] .btn-download`);
        if (!button) return alert('زر التحميل غير موجود');

        button.disabled = true;
        const originalText = button.textContent;
        button.textContent = '⏳ جاري التحميل...';

        try {
            // Get tender info from card for folder naming
            const card = button.closest('.tender-card');
            const tenderName = card?.querySelector('.tender-name')?.textContent?.trim() || '';
            const referenceNumber = card?.querySelector('.reference-number')?.textContent?.trim() || '';
            
            // Step 1: Download attachments with tender info for proper folder naming
            button.textContent = '⏳ جاري تحميل المرفقات...';
            const downloadUrl = `/api/tender/${tenderId}/download?tenderName=${encodeURIComponent(tenderName)}&referenceNumber=${encodeURIComponent(referenceNumber)}`;
            const response = await fetch(downloadUrl);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error);
            }

            // Step 2: Get tenderIdString from same card
            const tenderIdString = card?.querySelector('.btn-classification')?.getAttribute('data-tender-id-str');
            
            if (tenderIdString) {
                // Step 3: Download كراسة الشروط as PDF and save to folder
                button.textContent = '⏳ جاري تحميل كراسة الشروط...';
                
                try {
                    // Call backend to fetch HTML, convert to PDF, and save to folder
                    const pdfUrl = `/api/tender/${tenderIdString}/download-pdf?tenderName=${encodeURIComponent(tenderName)}&referenceNumber=${encodeURIComponent(referenceNumber)}`;
                    const pdfResponse = await fetch(pdfUrl);
                    const pdfData = await pdfResponse.json();
                    
                    if (pdfData.success) {
                        console.log('✅ كراسة الشروط downloaded and saved:', pdfData.path);
                    } else {
                        console.warn('⚠️ Failed to download كراسة الشروط:', pdfData.error);
                        // Open in browser as fallback
                        const rfpUrl = `https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId=${tenderIdString}`;
                        window.open(rfpUrl, '_blank');
                        console.log('⚠️ Opened in browser as fallback');
                    }
                } catch (rfpError) {
                    console.warn('⚠️ Failed to download كراسة الشروط:', rfpError);
                    // Open in browser as fallback
                    const rfpUrl = `https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId=${tenderIdString}`;
                    window.open(rfpUrl, '_blank');
                    console.log('⚠️ Opened in browser as fallback');
                }
            }

            // Success
            button.textContent = '✅ تم التحميل بنجاح';
            button.style.background = '#28a745';
            setTimeout(() => {
                button.textContent = originalText || '📥 تحميل جدول الكميات والمرفقات';
                button.disabled = false;
                button.style.background = '';
            }, 3000);
            
        } catch (error) {
            button.textContent = '❌ فشل التحميل';
            button.style.background = '#dc3545';
            alert('حدث خطأ أثناء التحميل: ' + error.message);
            setTimeout(() => {
                button.textContent = originalText || '📥 تحميل جدول الكميات والمرفقات';
                button.disabled = false;
                button.style.background = '';
            }, 3000);
        }
    };

    function showError(message) {
        errorDiv.textContent = '❌ ' + message;
        errorDiv.style.display = 'block';
    }

    function showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = '✅ ' + message;
        successDiv.style.cssText = `
            background: #10b981;
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        
        const container = document.querySelector('.container');
        const controls = container.querySelector('.controls');
        controls.parentNode.insertBefore(successDiv, controls.nextSibling);
        
        setTimeout(() => {
            successDiv.remove();
        }, 5000);
    }

    // Make delete function global
    window.deleteTender = async function(tenderId) {
        const card = document.querySelector(`[data-tender-id="${tenderId}"]`);
        
        if (!confirm('هل أنت متأكد من حذف هذه المنافسة من القائمة؟')) {
            return;
        }

        card.classList.add('deleting');

        try {
            const response = await fetch(`/api/tender/${tenderId}/delete`, {
                method: 'DELETE'
            });
            const data = await response.json();

            if (data.success) {
                card.classList.remove('deleting');
                card.classList.add('deleted');
                
                // Remove from DOM after animation
                setTimeout(() => {
                    card.remove();
                    // Update count
                    const remainingTenders = document.querySelectorAll('.tender-card').length;
                    tenderCount.textContent = `عدد المنافسات: ${remainingTenders}`;
                }, 500);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            card.classList.remove('deleting');
            alert('حدث خطأ أثناء الحذف: ' + error.message);
        }
    };

    // Bulk classification check and delete function
    async function checkAllClassifications() {
        const allCards = document.querySelectorAll('.tender-card');
        
        if (allCards.length === 0) {
            alert('لا توجد منافسات للفحص');
            return;
        }

        // Confirm action
        const confirmed = confirm(
            `هل أنت متأكد من فحص التصنيف لجميع المنافسات (${allCards.length})؟\n\n` +
            'سيتم حذف المنافسات التي تتطلب تصنيفاً تلقائياً.'
        );

        if (!confirmed) return;

        // Disable button and show progress
        checkClassificationBtn.disabled = true;
        checkClassificationBtn.textContent = '⏳ جاري الفحص...';

        let checked = 0;
        let deleted = 0;
        let errors = 0;

        // Process each tender
        for (const card of allCards) {
            const tenderIdStr = card.querySelector('.btn-classification')?.getAttribute('data-tender-id-str');
            
            if (!tenderIdStr) {
                errors++;
                continue;
            }

            try {
                // Fetch classification
                const response = await fetch(`/api/tender/${tenderIdStr}/classification`);
                const data = await response.json();

                checked++;
                
                // Update button text with progress
                checkClassificationBtn.textContent = `⏳ فحص ${checked}/${allCards.length}...`;

                if (data.success && data.requires_classification) {
                    // This tender requires classification - delete it
                    card.classList.add('deleting');
                    
                    // Delete the tender (UI only)
                    await fetch(`/api/tender/${card.getAttribute('data-tender-id')}/delete`, {
                        method: 'DELETE'
                    });

                    card.classList.remove('deleting');
                    card.classList.add('deleted');
                    
                    // Remove from DOM
                    setTimeout(() => card.remove(), 300);
                    
                    deleted++;
                    console.log(`✅ Deleted: ${tenderIdStr} - Classification: ${data.classification}`);
                } else if (data.success) {
                    console.log(`✓ Kept: ${tenderIdStr} - No classification required`);
                } else {
                    console.warn(`⚠ Error checking: ${tenderIdStr}`);
                    errors++;
                }

                // Small delay to avoid overwhelming the server
                await new Promise(resolve => setTimeout(resolve, 500));

            } catch (error) {
                console.error(`Error processing ${tenderIdStr}:`, error);
                errors++;
            }
        }

        // Update final count
        const remainingTenders = document.querySelectorAll('.tender-card:not(.deleted)').length;
        tenderCount.textContent = `عدد المنافسات: ${remainingTenders}`;

        // Show summary
        alert(
            `✅ تم الفحص!\n\n` +
            `📊 تم فحص: ${checked} منافسة\n` +
            `🗑️ تم حذف: ${deleted} منافسة (تتطلب تصنيف)\n` +
            `✓ المتبقي: ${remainingTenders} منافسة\n` +
            (errors > 0 ? `⚠️ أخطاء: ${errors}\n` : '')
        );

        // Re-enable button
        checkClassificationBtn.disabled = false;
        checkClassificationBtn.textContent = '🔍 فحص التصنيف وحذف المطلوب';

        // Hide button if no tenders left
        if (remainingTenders === 0) {
            checkClassificationBtn.style.display = 'none';
        }
    }

    // =============================================================================
    // PHASE 4: AI ANALYSIS FUNCTIONS
    // =============================================================================

    let currentAnalysisTenderId = null;
    let currentAnalysisReports = null;
    let analysisPollingInterval = null;

    async function startTenderAnalysis(tender, button) {
        // Check if tender has been downloaded first
        try {
            button.disabled = true;
            button.textContent = '⏳ جاري التحضير...';

            // Start analysis
            const response = await fetch(`/api/tender/${tender.tenderId}/analyze`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    tenderName: tender.tenderName,
                    referenceNumber: tender.referenceNumber
                })
            });

            const data = await response.json();

            if (data.success) {
                currentAnalysisTenderId = tender.tenderId;
                openAnalysisModal(tender);
                startAnalysisPolling(tender.tenderId);
            } else {
                alert(`فشل بدء التحليل: ${data.error}`);
                button.disabled = false;
                button.textContent = '🤖 تحليل بالذكاء الاصطناعي';
            }

        } catch (error) {
            alert(`خطأ في بدء التحليل: ${error.message}`);
            button.disabled = false;
            button.textContent = '🤖 تحليل بالذكاء الاصطناعي';
        }
    }

    function openAnalysisModal(tender) {
        const modal = document.getElementById('analysisModal');
        const tenderNameEl = document.getElementById('analysisTenderName');
        
        tenderNameEl.textContent = tender.tenderName;
        modal.style.display = 'flex';
    }

    function closeAnalysisModal() {
        const modal = document.getElementById('analysisModal');
        modal.style.display = 'none';
        
        if (analysisPollingInterval) {
            clearInterval(analysisPollingInterval);
            analysisPollingInterval = null;
        }
    }

    function startAnalysisPolling(tenderId) {
        // Poll every 2 seconds
        analysisPollingInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/tender/${tenderId}/analysis-status`);
                const data = await response.json();

                if (data.success) {
                    updateAnalysisProgress(data);

                    if (data.status === 'completed') {
                        clearInterval(analysisPollingInterval);
                        analysisPollingInterval = null;
                        
                        // Fetch full results
                        await fetchAndDisplayResults(tenderId);
                    } else if (data.status === 'error') {
                        clearInterval(analysisPollingInterval);
                        analysisPollingInterval = null;
                        
                        closeAnalysisModal();
                        alert(`فشل التحليل: ${data.error}`);
                    }
                }
            } catch (error) {
                console.error('Error polling analysis status:', error);
            }
        }, 2000);
    }

    function updateAnalysisProgress(data) {
        const progressBar = document.getElementById('analysisProgressBar');
        const progressText = document.getElementById('analysisProgressText');
        const currentStep = document.getElementById('analysisCurrentStep');

        if (progressBar) {
            progressBar.style.width = `${data.progress}%`;
        }
        
        if (progressText) {
            progressText.textContent = `${data.progress}%`;
        }

        if (currentStep) {
            currentStep.textContent = data.step;
        }
    }

    async function fetchAndDisplayResults(tenderId) {
        try {
            const response = await fetch(`/api/tender/${tenderId}/analysis-result`);
            const data = await response.json();

            if (data.success) {
                closeAnalysisModal();
                currentAnalysisReports = data.result.reports;
                showResultModal(data.result);
            } else {
                alert(`فشل جلب النتائج: ${data.error}`);
            }
        } catch (error) {
            alert(`خطأ في جلب النتائج: ${error.message}`);
        }
    }

    function showResultModal(result) {
        const modal = document.getElementById('resultModal');
        const content = document.getElementById('resultContent');

        const recommendation = result.recommendation;
        const financial = result.financial;
        const technical = result.technical;
        const market = result.market;

        const priorityClass = recommendation.priority.toLowerCase();
        const shouldBidIcon = recommendation.should_bid ? '✅' : '❌';
        const shouldBidText = recommendation.should_bid ? 'نعم - يُوصى بالمشاركة' : 'لا - لا يُوصى بالمشاركة';

        content.innerHTML = `
            <div class="result-summary">
                <div class="result-item">
                    <div class="result-item-label">التوصية</div>
                    <div class="result-item-value ${recommendation.should_bid ? 'success' : 'danger'}">
                        ${shouldBidIcon} ${shouldBidText}
                    </div>
                </div>
                
                <div class="result-item">
                    <div class="result-item-label">الأولوية</div>
                    <div class="result-item-value">
                        <span class="recommendation-badge ${priorityClass}">
                            ${recommendation.priority === 'High' ? '🟢 عالية' : recommendation.priority === 'Medium' ? '🟡 متوسطة' : '🔴 منخفضة'}
                        </span>
                    </div>
                </div>
            </div>

            <div class="result-summary">
                <div class="result-item">
                    <div class="result-item-label">التكلفة المقدرة</div>
                    <div class="result-item-value">${financial.total_cost.toLocaleString('ar-SA')} ريال</div>
                </div>

                <div class="result-item">
                    <div class="result-item-label">سعر العرض المقترح</div>
                    <div class="result-item-value success">${financial.recommended_bid.toLocaleString('ar-SA')} ريال</div>
                </div>

                <div class="result-item">
                    <div class="result-item-label">هامش الربح</div>
                    <div class="result-item-value ${financial.profit_margin >= 15 ? 'success' : 'warning'}">
                        ${financial.profit_margin.toFixed(1)}%
                    </div>
                </div>

                <div class="result-item">
                    <div class="result-item-label">الربح المتوقع</div>
                    <div class="result-item-value success">${financial.expected_profit.toLocaleString('ar-SA')} ريال</div>
                </div>
            </div>

            <div class="result-summary">
                <div class="result-item">
                    <div class="result-item-label">درجة الجدوى الفنية</div>
                    <div class="result-item-value ${technical.feasibility_score >= 70 ? 'success' : 'warning'}">
                        ${technical.feasibility_score.toFixed(0)}% - ${technical.feasibility_level}
                    </div>
                </div>

                <div class="result-item">
                    <div class="result-item-label">توافق القدرات</div>
                    <div class="result-item-value">${technical.capability_match.toFixed(0)}%</div>
                </div>

                <div class="result-item">
                    <div class="result-item-label">منافسات مماثلة</div>
                    <div class="result-item-value">${market.similar_tenders}</div>
                </div>

                <div class="result-item">
                    <div class="result-item-label">موردون محتملون</div>
                    <div class="result-item-value">${market.suppliers_found}</div>
                </div>
            </div>

            <div style="margin: 20px 0; padding: 15px; background: #f0f9ff; border-radius: 10px;">
                <h4 style="color: #0369a1; margin-bottom: 10px;">💡 نقاط القوة:</h4>
                <ul style="margin: 0; padding-right: 20px;">
                    ${recommendation.key_strengths.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>

            ${recommendation.key_concerns && recommendation.key_concerns.length > 0 ? `
            <div style="margin: 20px 0; padding: 15px; background: #fef3c7; border-radius: 10px;">
                <h4 style="color: #92400e; margin-bottom: 10px;">⚠️ نقاط الاهتمام:</h4>
                <ul style="margin: 0; padding-right: 20px;">
                    ${recommendation.key_concerns.map(c => `<li>${c}</li>`).join('')}
                </ul>
            </div>
            ` : ''}
        `;

        modal.style.display = 'flex';
    }

    // Wire up modal close buttons
    const closeAnalysisBtn = document.getElementById('closeAnalysisBtn');
    if (closeAnalysisBtn) {
        closeAnalysisBtn.addEventListener('click', closeAnalysisModal);
    }

    // Global functions for result modal
    window.closeResultModal = function() {
        const modal = document.getElementById('resultModal');
        modal.style.display = 'none';
    };

    window.viewReport = function(language) {
        if (!currentAnalysisReports) {
            alert('التقرير غير متوفر');
            return;
        }

        const reportPath = language === 'ar' ? currentAnalysisReports.arabic : currentAnalysisReports.english;
        
        if (!reportPath) {
            alert('التقرير غير متوفر');
            return;
        }

        // Open report in new window
        window.open(`file:///${reportPath.replace(/\\/g, '/')}`, '_blank');
    };
    
    // ===========================
    // Phase 5: Downloads Management
    // ===========================
    
    async function loadDownloads() {
        const container = document.getElementById('downloadsContainer');
        const countBadge = document.getElementById('downloadsCount');
        
        if (!container) return;
        
        container.innerHTML = '<div class="loading"><div class="spinner"></div><p>جاري تحميل القائمة...</p></div>';
        
        try {
            const response = await fetch('/api/downloads');
            const data = await response.json();
            
            if (!data.success) {
                container.innerHTML = '<div class="error-message">فشل تحميل القائمة</div>';
                return;
            }
            
            if (countBadge) {
                countBadge.textContent = `${data.count} منافسة محملة`;
            }
            
            if (data.count === 0) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 60px; color: #64748b;">
                        <div style="font-size: 64px; margin-bottom: 20px;">📥</div>
                        <h3>لا توجد منافسات محملة</h3>
                        <p>ابدأ بجلب المنافسات من تبويب "المنافسات" ثم قم بتحميل المرفقات</p>
                    </div>
                `;
                return;
            }
            
            // Group by analyzed status
            const analyzed = data.tenders.filter(t => t.analyzed);
            const notAnalyzed = data.tenders.filter(t => !t.analyzed);
            
            let html = '';
            
            // Show analyzed tenders first
            if (analyzed.length > 0) {
                html += '<h3 style="margin: 20px 0; color: #1e293b;">✅ تم التحليل</h3>';
                analyzed.forEach(tender => {
                    html += createDownloadCard(tender, true);
                });
            }
            
            // Then not analyzed
            if (notAnalyzed.length > 0) {
                html += '<h3 style="margin: 30px 0 20px 0; color: #1e293b;">⚪ لم يتم التحليل</h3>';
                notAnalyzed.forEach(tender => {
                    html += createDownloadCard(tender, false);
                });
            }
            
            container.innerHTML = html;
            
            // Wire up batch analyze button
            const batchBtn = document.getElementById('batchAnalyzeBtn');
            if (batchBtn) {
                batchBtn.addEventListener('click', handleBatchAnalyze);
            }
            
        } catch (error) {
            console.error('Failed to load downloads:', error);
            container.innerHTML = '<div class="error-message">فشل تحميل القائمة</div>';
        }
    }
    
    function createDownloadCard(tender, isAnalyzed) {
        const statusClass = isAnalyzed ? 'analyzed' : 'not-analyzed';
        const statusText = isAnalyzed ? '✅ تم التحليل' : '⚪ لم يتم التحليل';
        const tenderId = tender.tender_id || '';
        const folderName = tender.folder_name || '';
        
        // Format dates
        const createdDate = tender.created_at ? new Date(tender.created_at).toLocaleDateString('ar-SA') : 'غير متوفر';
        const analysisDate = tender.analysis_date ? new Date(tender.analysis_date).toLocaleDateString('ar-SA') : '';
        
        // Get priority
        const priority = tender.recommendation?.priority || 'Unknown';
        const priorityClass = priority.toLowerCase();
        const priorityText = priority === 'High' ? 'عالية' : (priority === 'Medium' ? 'متوسطة' : 'منخفضة');
        
        return `
            <div class="download-card ${statusClass}">
                <div class="download-header">
                    <div class="download-title">📁 ${folderName}</div>
                    <div class="download-status ${statusClass}">${statusText}</div>
                </div>
                
                <div class="download-info">
                    <div class="info-item">
                        <strong>معرف:</strong> ${tenderId || 'غير متوفر'}
                    </div>
                    <div class="info-item">
                        <strong>تاريخ التحميل:</strong> ${createdDate}
                    </div>
                    <div class="info-item">
                        <strong>عدد الملفات:</strong> ${tender.file_count || 0}
                    </div>
                    ${isAnalyzed ? `
                    <div class="info-item">
                        <strong>تاريخ التحليل:</strong> ${analysisDate}
                    </div>
                    <div class="info-item">
                        <strong>الأولوية:</strong> 
                        <span class="priority-badge ${priorityClass}">
                            ${priorityText}
                        </span>
                    </div>
                    ` : ''}
                </div>
                
                <div class="download-actions">
                    ${isAnalyzed ? `
                        <button class="btn-view-report" onclick="viewDownloadReport('${folderName}', '${tender.reports?.arabic || ''}')">� عرض التقرير</button>
                        <button class="btn-analyze" onclick="reAnalyzeTender('${tenderId}', '${folderName}')">🔄 إعادة التحليل</button>
                    ` : `
                        <button class="btn-analyze" onclick="analyzeSingleDownload('${tenderId}', '${folderName}')">🤖 تحليل</button>
                    `}
                    <button class="btn-delete" onclick="deleteTender('${folderName}')">🗑️ حذف</button>
                </div>
            </div>
        `;
    }
    
    window.openFolder = function(folderName) {
        // This would need a backend endpoint to open folder
        alert(`فتح مجلد: ${folderName}\n(سيتم تنفيذه في النسخة المكتملة)`);
    };
    
    window.viewDownloadReport = function(folderName, reportPath) {
        if (!reportPath) {
            alert('التقرير غير متوفر');
            return;
        }
        // Open report in new window
        window.open(`/data/tender_analyses/${reportPath.split('/').pop()}`, '_blank');
    };
    
    window.analyzeSingleDownload = async function(tenderId, folderName) {
        if (!tenderId) {
            alert('معرف المنافسة غير متوفر');
            return;
        }
        
        // Confirm before analyzing
        if (!confirm(`هل تريد تحليل المنافسة:\n${folderName}؟`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/tender/${tenderId}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(`✅ بدأ تحليل المنافسة!\nسيتم إشعارك عند الانتهاء.`);
                // Reload downloads after a delay
                setTimeout(() => loadDownloads(), 2000);
            } else {
                alert(`❌ فشل بدء التحليل:\n${data.error}`);
            }
        } catch (error) {
            console.error('Analysis error:', error);
            alert('حدث خطأ أثناء بدء التحليل');
        }
    };
    
    window.reAnalyzeTender = async function(tenderId, folderName) {
        if (!confirm(`هل تريد إعادة تحليل المنافسة:\n${folderName}؟\nسيتم استبدال التحليل السابق.`)) {
            return;
        }
        await analyzeSingleDownload(tenderId, folderName);
    };
    
    window.deleteTender = async function(folderName) {
        if (!confirm(`⚠️ تحذير!\nهل أنت متأكد من حذف المنافسة:\n${folderName}؟\n\nسيتم حذف جميع الملفات والتحليلات بشكل نهائي.`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/downloads/${encodeURIComponent(folderName)}/delete`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(`✅ ${data.message}`);
                // Reload downloads
                loadDownloads();
            } else {
                alert(`❌ فشل الحذف:\n${data.error}`);
            }
        } catch (error) {
            console.error('Delete error:', error);
            alert('حدث خطأ أثناء الحذف');
        }
    };
    
    async function handleBatchAnalyze() {
        const checkboxes = document.querySelectorAll('.tender-checkbox:checked');
        
        if (checkboxes.length === 0) {
            alert('الرجاء تحديد منافسة واحدة على الأقل');
            return;
        }
        
        if (checkboxes.length > 10) {
            alert('يمكنك تحليل 10 منافسات كحد أقصى في المرة الواحدة');
            return;
        }
        
        if (!confirm(`هل تريد تحليل ${checkboxes.length} منافسة؟`)) {
            return;
        }
        
        const tenderIds = Array.from(checkboxes).map(cb => cb.getAttribute('data-tender-id'));
        
        const btn = document.getElementById('batchAnalyzeBtn');
        btn.disabled = true;
        btn.textContent = '⏳ جاري التحليل...';
        
        try {
            const response = await fetch('/api/batch-analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tender_ids: tenderIds })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(`✅ ${data.message}\nتم بدء: ${data.started.length}\nفشل: ${data.failed.length}`);
                // Reload downloads to show progress
                setTimeout(() => loadDownloads(), 2000);
            } else {
                alert(`❌ فشل: ${data.error}`);
            }
            
        } catch (error) {
            alert(`❌ خطأ: ${error.message}`);
        } finally {
            btn.disabled = false;
            btn.textContent = '🤖 تحليل المحددة';
        }
    }
    
    // ===========================
    // Phase 5: Cost Tracking
    // ===========================
    
    async function loadCostSummary() {
        try {
            // Load monthly summary
            const summaryResponse = await fetch('/api/costs/summary');
            const summaryData = await summaryResponse.json();
            
            if (summaryData.success) {
                displayCostSummary(summaryData.summary);
            }
            
            // Load recent analyses
            const recentResponse = await fetch('/api/costs/recent?limit=10');
            const recentData = await recentResponse.json();
            
            if (recentData.success) {
                displayRecentCosts(recentData.analyses);
            }
            
            // Load cache stats
            const cacheResponse = await fetch('/api/cache/stats');
            const cacheData = await cacheResponse.json();
            
            if (cacheData.success) {
                displayCacheStats(cacheData.stats);
            }
            
        } catch (error) {
            console.error('Failed to load cost summary:', error);
        }
    }
    
    function displayCostSummary(summary) {
        const container = document.getElementById('monthlyCostSummary');
        if (!container) return;
        
        const current = summary.current_month || summary;
        const percentage = current.percentage_used || 0;
        const status = current.status || 'OK';
        
        let statusClass = 'success';
        if (status === 'WARNING') statusClass = 'warning';
        if (status === 'EXCEEDED') statusClass = 'danger';
        
        container.innerHTML = `
            <div class="cost-stat">
                <span class="cost-label">التكلفة الإجمالية</span>
                <span class="cost-value ${statusClass}">$${current.total_cost || 0}</span>
            </div>
            <div class="cost-stat">
                <span class="cost-label">حد الميزانية</span>
                <span class="cost-value">$${current.budget_limit || 100}</span>
            </div>
            <div class="cost-stat">
                <span class="cost-label">عدد التحليلات</span>
                <span class="cost-value">${current.num_analyses || 0}</span>
            </div>
            <div class="cost-stat">
                <span class="cost-label">متوسط التكلفة</span>
                <span class="cost-value">$${(current.avg_cost_per_analysis || 0).toFixed(4)}</span>
            </div>
            <div class="cost-stat">
                <span class="cost-label">المتبقي</span>
                <span class="cost-value success">$${current.budget_remaining || 0}</span>
            </div>
            
            <div class="budget-progress">
                <div class="budget-bar">
                    <div class="budget-bar-fill ${statusClass}" style="width: ${Math.min(percentage, 100)}%">
                        ${percentage.toFixed(1)}%
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #f8fafc; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0; color: #1e293b;">التفصيل:</h4>
                <div class="cost-stat">
                    <span class="cost-label">Anthropic Claude</span>
                    <span class="cost-value">$${current.breakdown?.anthropic || 0}</span>
                </div>
                <div class="cost-stat">
                    <span class="cost-label">Tavily Search</span>
                    <span class="cost-value">$${current.breakdown?.tavily || 0}</span>
                </div>
            </div>
        `;
    }
    
    function displayRecentCosts(analyses) {
        const container = document.getElementById('recentAnalysesCosts');
        if (!container) return;
        
        if (!analyses || analyses.length === 0) {
            container.innerHTML = '<p style="color: #64748b; text-align: center;">لا توجد تحليلات حديثة</p>';
            return;
        }
        
        container.innerHTML = analyses.map(analysis => `
            <div class="recent-analysis-item">
                <div class="recent-analysis-header">
                    <span class="recent-analysis-id">${analysis.tender_id}</span>
                    <span class="recent-analysis-cost">$${analysis.costs.total.toFixed(4)}</span>
                </div>
                <div class="recent-analysis-date">${new Date(analysis.timestamp).toLocaleString('ar-SA')}</div>
            </div>
        `).join('');
    }
    
    function displayCacheStats(stats) {
        const container = document.getElementById('cacheStats');
        if (!container) return;
        
        container.innerHTML = `
            <div class="cost-stat">
                <span class="cost-label">المستندات المخزنة</span>
                <span class="cost-value">${stats.documents_cached || 0}</span>
            </div>
            <div class="cost-stat">
                <span class="cost-label">عمليات البحث المخزنة</span>
                <span class="cost-value">${stats.searches_cached || 0}</span>
            </div>
            <div class="cost-stat">
                <span class="cost-label">التحليلات المخزنة</span>
                <span class="cost-value">${stats.analyses_cached || 0}</span>
            </div>
            <div class="cost-stat">
                <span class="cost-label">الحجم الإجمالي</span>
                <span class="cost-value">${stats.total_cache_size_mb || 0} MB</span>
            </div>
        `;
    }
    
    // Wire up budget setting
    const setBudgetBtn = document.getElementById('setBudgetBtn');
    if (setBudgetBtn) {
        setBudgetBtn.addEventListener('click', async () => {
            const input = document.getElementById('budgetLimit');
            const limit = parseFloat(input.value);
            
            if (!limit || limit <= 0) {
                alert('الرجاء إدخال قيمة صالحة');
                return;
            }
            
            try {
                const response = await fetch('/api/costs/budget', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ limit })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    loadCostSummary(); // Reload
                } else {
                    alert(`فشل: ${data.error}`);
                }
            } catch (error) {
                alert(`خطأ: ${error.message}`);
            }
        });
    }
    
    // Wire up cache clear buttons
    document.querySelectorAll('.btn-clear-cache').forEach(btn => {
        btn.addEventListener('click', async () => {
            const cacheType = btn.getAttribute('data-type');
            
            if (!confirm(`هل تريد مسح ${cacheType} cache؟`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/cache/clear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cache_type: cacheType })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    loadCostSummary(); // Reload stats
                } else {
                    alert(`فشل: ${data.error}`);
                }
            } catch (error) {
                alert(`خطأ: ${error.message}`);
            }
        });
    });
    
    const clearAllBtn = document.querySelector('.btn-clear-cache-all');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', async () => {
            if (!confirm('هل تريد مسح جميع الذاكرة المؤقتة؟\nهذا سيبطئ التحليلات التالية.')) {
                return;
            }
            
            try {
                const response = await fetch('/api/cache/clear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cache_type: 'all' })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    loadCostSummary(); // Reload stats
                } else {
                    alert(`فشل: ${data.error}`);
                }
            } catch (error) {
                alert(`خطأ: ${error.message}`);
            }
        });
    }
});




