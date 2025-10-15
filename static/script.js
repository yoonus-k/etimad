document.addEventListener('DOMContentLoaded', function() {
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

    // Helper function to proxy Etimad URLs through our backend to avoid CORS
    function proxyEtimadUrl(etimadUrl) {
        return `/api/proxy/etimad?url=${encodeURIComponent(etimadUrl)}`;
    }

    // Wire cookie modal open
    if (updateCookiesBtn) updateCookiesBtn.addEventListener('click', openCookieModal);
    fetchBtn.addEventListener('click', () => fetchTenders(false));
    if (fetchQuickBtn) fetchQuickBtn.addEventListener('click', () => fetchTenders(true));
    if (checkClassificationBtn) checkClassificationBtn.addEventListener('click', checkAllClassifications);

    // ---- Cookie modal workflow ----
    function openCookieModal() {
        const modal = document.getElementById('cookieModal');
        if (!modal) return showError('نافذة الكوكيز غير متوفرة');
        modal.style.display = 'block';
    }

    function closeCookieModal() {
        const modal = document.getElementById('cookieModal');
        if (!modal) return;
        modal.style.display = 'none';
    }

    // Wire modal buttons
    const saveCookiesBtn = document.getElementById('saveCookiesBtn');
    const cancelCookiesBtn = document.getElementById('cancelCookiesBtn');
    const cookieInput = document.getElementById('cookieInput');

    if (cancelCookiesBtn) cancelCookiesBtn.addEventListener('click', closeCookieModal);

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
                showError(data.error || 'حدث خطأ أثناء جلب المنافسات');
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
        const downloadBtn = card.querySelector('.btn-download');
        const deleteBtn = card.querySelector('.btn-delete');

        if (classificationBtn) {
            classificationBtn.addEventListener('click', function () {
                const tenderIdStr = this.getAttribute('data-tender-id-str');
                fetchAndDisplayClassification(card, tenderIdStr, this);
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
});



