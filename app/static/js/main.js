// Client-side scripting for healthcare portal interface

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch(e) {
                // Fallback if bootstrap object is not fully initialized
                alert.style.display = 'none';
            }
        }, 5000);
    });

    // 2. Setup drag and drop for upload zone
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
                dropzoneText.innerHTML = `<i class="bi bi-file-check-fill text-success fs-3 d-block mb-2"></i><strong>Selected File:</strong> <span class="text-success">${name}</span><br><span class="text-muted text-sm">Click "Upload & Classify" to submit</span>`;
                // Add a visual state indicating a file is ready
                dropzone.style.borderColor = '#0d9488'; // Turn teal
                dropzone.style.backgroundColor = '#ccfbf1';
            }
        }
    }

    // 3. Simulated Upload Progress Indicator
    const uploadForm = document.getElementById('upload-form');
    const progressContainer = document.getElementById('progress-container');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressText = document.getElementById('progress-text');

    if (uploadForm && progressContainer && fileInput) {
        uploadForm.addEventListener('submit', function(e) {
            // Verify files actually selected
            if (fileInput.files.length === 0) return;

            e.preventDefault(); // Stop standard submit to show progress animation

            // Hide warnings and disable submit button to prevent double-submit
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Classifying...`;
            }

            progressContainer.style.display = 'block';

            let width = 0;
            const duration = 1200; // 1.2 seconds simulation
            const step = 40;
            const intervalTime = duration / (100 / step);

            const timer = setInterval(function() {
                width += step;
                if (width >= 100) {
                    progressBarFill.style.width = '100%';
                    progressText.textContent = '100%';
                    clearInterval(timer);
                    // Proactive submit
                    uploadForm.submit();
                } else {
                    progressBarFill.style.width = width + '%';
                    progressText.textContent = width + '%';
                }
            }, intervalTime);
        });
    }

    // 4. Dynamic Date display in dashboard
    const dateBadge = document.getElementById('current-date-badge');
    if (dateBadge) {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        dateBadge.innerHTML = `<i class="bi bi-clock me-1 text-primary"></i> Current Date: ${year}-${month}-${day}`;
    }

    // 5. Client-Side Search and Filtering
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
            const queryDate = filterDate.value; // YYYY-MM-DD

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

            // Update record count badge
            if (recordCount) {
                recordCount.textContent = `Showing ${visibleCount} records`;
            }

            // Toggle No Results Message
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

    // 6. Statistics Counter Animation for Landing Page
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
            const duration = 1000; // 1 second total
            const stepValue = Math.ceil(target / 40);
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

    // Execute counter animations
    animateCounters();

    // 7. Dashboard Quick Actions Helper Scripts
    const actionUpload = document.getElementById('action-upload-scroll');
    const actionDownloadFirst = document.getElementById('action-download-first');
    const actionQrFirst = document.getElementById('action-qr-first');

    if (actionUpload) {
        actionUpload.addEventListener('click', function(e) {
            e.preventDefault();
            const dropzoneEl = document.getElementById('upload-dropzone');
            if (dropzoneEl) {
                dropzoneEl.scrollIntoView({ behavior: 'smooth' });
                dropzoneEl.style.transform = 'scale(1.03)';
                setTimeout(() => {
                    dropzoneEl.style.transform = '';
                }, 250);
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
