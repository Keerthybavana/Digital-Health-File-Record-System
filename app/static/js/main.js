// ==========================================================================
// ATLASSIAN CONFLUENCE INTERACTIVE JS CONTROLLER FOR HEALTHDOC ML
// ==========================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Navbar Scroll Elevation
    const navbar = document.querySelector('.atl-navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 20) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // 2. Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch(e) {
                alert.style.display = 'none';
            }
        }, 5000);
    });

    // 3. Confluence Interactive Tab Showcase Switcher
    const tabButtons = document.querySelectorAll('.confluence-tab-pill');
    const tabPanels = document.querySelectorAll('.confluence-tab-panel');

    if (tabButtons.length && tabPanels.length) {
        tabButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const targetTab = this.getAttribute('data-tab');

                // Remove active class from all buttons and panels
                tabButtons.forEach(b => b.classList.remove('active'));
                tabPanels.forEach(p => p.classList.remove('active'));

                // Activate current
                this.classList.add('active');
                const activePanel = document.getElementById(`panel-${targetTab}`);
                if (activePanel) {
                    activePanel.classList.add('active');
                }
            });
        });
    }

    // 4. Interactive "AI Classifier in Action" Playground Simulator
    const sampleButtons = document.querySelectorAll('.demo-sample-btn');
    const consoleOutput = document.getElementById('playground-console-output');
    const confidenceFill = document.getElementById('playground-confidence-fill');
    const confidenceText = document.getElementById('playground-confidence-text');
    const predictedBadge = document.getElementById('playground-predicted-badge');

    const sampleData = {
        'prescription': {
            category: 'Prescription',
            badgeClass: 'badge-cat-prescription',
            icon: 'bi-capsule',
            title: 'Amoxicillin 500mg Oral Capsule',
            keywords: ['Rx: Amoxicillin Trihydrate', 'Sig: 1 cap PO TID x 10d', 'Refills: 0', 'DEA: Dr. Mitchell MD'],
            confidence: 98.4,
            extractedText: 'CLINICAL PRESCRIPTION ORDER\nPatient: Emily Roberts\nRx: Amoxicillin 500mg\nDispense: #30 Capsules\nSig: Take 1 capsule orally every 8 hours with food.\nPhysician Signature Verified.'
        },
        'lab': {
            category: 'Lab Report',
            badgeClass: 'badge-cat-lab',
            icon: 'bi-file-earmark-medical',
            title: 'Comprehensive Metabolic & CBC Panel',
            keywords: ['Hemoglobin: 14.2 g/dL', 'WBC: 6.8 x10^3/uL', 'Serum Glucose: 92 mg/dL', 'Creatinine: 0.9 mg/dL'],
            confidence: 99.2,
            extractedText: 'HEMATOLOGY & CLINICAL BIOCHEMISTRY\nSpecimen: Whole Blood EDTA\nTest: Complete Blood Count\nWBC Count: 6.8 K/uL (Normal 4.5 - 11.0)\nPlatelets: 245 K/uL\nGlucose Fasting: 92 mg/dL (Normal < 100)'
        },
        'scan': {
            category: 'Scan Report',
            badgeClass: 'badge-cat-scan',
            icon: 'bi-activity',
            title: 'High-Resolution Chest CT Angiogram',
            keywords: ['Axial Slice Reconstruction', 'Bilateral Lung Parenchyma', 'Radiographic Attenuation: Normal', 'Contrast: Omnipaque 350'],
            confidence: 97.9,
            extractedText: 'DIAGNOSTIC RADIOLOGY REPORT\nProcedure: Multi-slice Thoracic CT with IV Contrast\nFindings: Lungs demonstrate clear aeration bilaterally.\nNo consolidation or pleural effusion.\nImpression: Normal diagnostic study without acute cardiopulmonary process.'
        },
        'discharge': {
            category: 'Discharge Summary',
            badgeClass: 'badge-cat-discharge',
            icon: 'bi-clipboard2-pulse',
            title: 'Inpatient Cardiology Discharge Summary',
            keywords: ['Admission Date: 08/20', 'Discharge Disposition: Home', 'Condition: Clinically Stable', 'Post-Op Follow-up: 14 Days'],
            confidence: 99.0,
            extractedText: 'POST-OPERATIVE DISCHARGE SUMMARY\nAdmission Diagnosis: Cardiac Observation\nCourse: Uneventful recovery post 48-hour monitoring.\nDischarge Instructions: Resume low-sodium diet, light activity as tolerated.\nFollow-up appointment booked in 2 weeks.'
        }
    };

    if (sampleButtons.length && consoleOutput && confidenceFill) {
        sampleButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const sampleType = this.getAttribute('data-sample');
                const data = sampleData[sampleType];
                if (!data) return;

                // Active button toggle
                sampleButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                // Simulate terminal processing
                consoleOutput.innerHTML = `
                    <div class="terminal-line text-muted small"><i class="bi bi-gear-fill me-1"></i> [1/3] Parsing document payload: <em>${data.title}</em>...</div>
                    <div class="terminal-line text-muted small"><i class="bi bi-cpu-fill me-1"></i> [2/3] Extracting TF-IDF n-grams: <code>${data.keywords.slice(0, 2).join(' | ')}</code></div>
                    <div class="terminal-line text-success small fw-semibold"><i class="bi bi-check2-circle me-1"></i> [3/3] Logistic Regression Match Completed!</div>
                    <div class="mt-3 p-2 bg-dark rounded border border-secondary">
                        <span class="text-white fw-bold d-block mb-1">Snippet Analysis:</span>
                        <div class="text-white-50" style="white-space: pre-line; font-size: 0.8rem;">${data.extractedText}</div>
                    </div>
                `;

                // Update Confidence bar
                confidenceFill.style.width = `${data.confidence}%`;
                if (confidenceText) {
                    confidenceText.textContent = `${data.confidence}% Confidence Match`;
                }

                // Update Badge
                if (predictedBadge) {
                    predictedBadge.className = `badge-cat ${data.badgeClass} px-3 py-1.5 fs-6`;
                    predictedBadge.innerHTML = `<i class="bi ${data.icon} me-1"></i> ${data.category}`;
                }
            });
        });
    }

    // 5. Setup drag and drop for upload zone
    const fileInput = document.getElementById('document-file');
    const dropzone = document.getElementById('upload-dropzone');
    const dropzoneText = document.getElementById('dropzone-text');

    if (fileInput && dropzone) {
        // Drag events
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, function(e) {
                e.preventDefault();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, function(e) {
                e.preventDefault();
                dropzone.classList.remove('dragover');
            }, false);
        });

        // Drop event
        dropzone.addEventListener('drop', function(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length) {
                fileInput.files = files;
                updateFilename(files[0].name);
            }
        }, false);

        // Input change event
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length) {
                updateFilename(fileInput.files[0].name);
            }
        });

        function updateFilename(name) {
            if (dropzoneText) {
                dropzoneText.innerHTML = `
                    <div class="d-inline-flex align-items-center justify-content-center bg-white text-success rounded-circle p-2 mb-2 shadow-sm" style="width: 44px; height: 44px;">
                        <i class="bi bi-file-earmark-check-fill fs-4"></i>
                    </div>
                    <div><strong class="text-dark">Selected File:</strong> <span class="text-primary fw-bold">${name}</span></div>
                    <div class="text-muted small mt-1">Ready for automated ML classification</div>
                `;
                dropzone.style.borderColor = '#00875a';
                dropzone.style.backgroundColor = '#e3fcef';
            }
        }
    }

    // 6. Simulated Upload Progress Indicator
    const uploadForm = document.getElementById('upload-form');
    const progressContainer = document.getElementById('progress-container');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressText = document.getElementById('progress-text');

    if (uploadForm && progressContainer && fileInput) {
        uploadForm.addEventListener('submit', function(e) {
            if (fileInput.files.length === 0) return;

            e.preventDefault();

            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Analyzing Clinical Content...`;
            }

            progressContainer.style.display = 'block';

            let width = 0;
            const duration = 1200;
            const step = 40;
            const intervalTime = duration / (100 / step);

            const timer = setInterval(function() {
                width += step;
                if (width >= 100) {
                    progressBarFill.style.width = '100%';
                    progressText.textContent = '100%';
                    clearInterval(timer);
                    uploadForm.submit();
                } else {
                    progressBarFill.style.width = width + '%';
                    progressText.textContent = width + '%';
                }
            }, intervalTime);
        });
    }

    // 7. Dynamic Date display in dashboard
    const dateBadge = document.getElementById('current-date-badge');
    if (dateBadge) {
        const now = new Date();
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        dateBadge.innerHTML = `<i class="bi bi-calendar3 me-1 text-primary"></i> ${now.toLocaleDateString('en-US', options)}`;
    }

    // 8. Client-Side Search and Filtering
    const searchName = document.getElementById('search-name');
    const filterCategory = document.getElementById('filter-category');
    const filterDate = document.getElementById('filter-date');
    const btnReset = document.getElementById('btn-reset-filters');
    const docTable = document.getElementById('documents-table');
    const noResults = document.getElementById('no-search-results');
    const recordCount = document.getElementById('table-record-count');

    if (searchName && docTable) {
        const rows = docTable.querySelectorAll('tbody tr');

        function filterRows() {
            const queryName = searchName.value.toLowerCase().trim();
            const queryCategory = filterCategory.value;
            const queryDate = filterDate.value;

            let visibleCount = 0;

            rows.forEach(row => {
                const filenameEl = row.querySelector('.doc-filename');
                const filename = filenameEl ? filenameEl.textContent.toLowerCase() : '';
                const category = row.getAttribute('data-category') || '';
                const date = row.getAttribute('data-date') || '';

                const matchesName = !queryName || filename.includes(queryName);
                const matchesCategory = !queryCategory || category === queryCategory;
                const matchesDate = !queryDate || date === queryDate;

                if (matchesName && matchesCategory && matchesDate) {
                    row.style.setProperty('display', '', 'important');
                    visibleCount++;
                } else {
                    row.style.setProperty('display', 'none', 'important');
                }
            });

            if (recordCount) {
                recordCount.textContent = `Showing ${visibleCount} records`;
            }

            if (noResults) {
                if (visibleCount === 0 && rows.length > 0) {
                    noResults.classList.remove('d-none');
                    docTable.querySelector('thead').style.display = 'none';
                } else {
                    noResults.classList.add('d-none');
                    if (rows.length > 0) {
                        docTable.querySelector('thead').style.display = '';
                    }
                }
            }
        }

        searchName.addEventListener('keyup', filterRows);
        filterCategory.addEventListener('change', filterRows);
        filterDate.addEventListener('change', filterRows);

        if (btnReset) {
            btnReset.addEventListener('click', function() {
                searchName.value = '';
                filterCategory.value = '';
                filterDate.value = '';
                filterRows();
            });
        }
    }

    // 9. Statistics Counter Animation for Landing Page
    function animateCounters() {
        const counters = [
            document.getElementById('stat-reports'),
            document.getElementById('stat-users'),
            document.getElementById('stat-accuracy'),
            document.getElementById('stat-processed')
        ];

        counters.forEach(counter => {
            if (!counter) return;

            const target = parseInt(counter.getAttribute('data-target'), 10);
            if (isNaN(target)) return;

            let current = 0;
            const duration = 1200;
            const stepValue = Math.max(1, Math.ceil(target / 40));
            const stepTime = duration / (target / stepValue);

            const timer = setInterval(function() {
                current += stepValue;
                if (current >= target) {
                    counter.textContent = target;
                    if (counter.id === 'stat-accuracy') {
                        counter.textContent += '%';
                    } else if (counter.id === 'stat-processed') {
                        counter.textContent += '+';
                    }
                    clearInterval(timer);
                } else {
                    counter.textContent = current;
                }
            }, stepTime || 25);
        });
    }

    animateCounters();

    // 10. Dashboard Quick Actions Helper Scripts
    const actionUpload = document.getElementById('action-upload-scroll');
    const actionDownloadFirst = document.getElementById('action-download-first');
    const actionQrFirst = document.getElementById('action-qr-first');

    if (actionUpload) {
        actionUpload.addEventListener('click', function(e) {
            e.preventDefault();
            const dropzoneEl = document.getElementById('upload-dropzone');
            if (dropzoneEl) {
                dropzoneEl.scrollIntoView({ behavior: 'smooth' });
                dropzoneEl.style.boxShadow = 'var(--elevation-glow)';
                setTimeout(() => {
                    dropzoneEl.style.boxShadow = '';
                }, 600);
            }
        });
    }

    if (actionDownloadFirst) {
        actionDownloadFirst.addEventListener('click', function(e) {
            e.preventDefault();
            const firstDownload = document.querySelector('#documents-table tbody tr a[title="Download"]');
            if (firstDownload) {
                firstDownload.click();
            } else {
                alert('No documents available in your portal to download.');
            }
        });
    }

    if (actionQrFirst) {
        actionQrFirst.addEventListener('click', function(e) {
            e.preventDefault();
            const firstDetails = document.querySelector('#documents-table tbody tr a[title="Details & QR"]');
            if (firstDetails) {
                firstDetails.click();
            } else {
                alert('No documents available in your portal to view.');
            }
        });
    }
});
