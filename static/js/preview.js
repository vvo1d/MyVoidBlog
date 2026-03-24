/**
 * Editor: tab switching, live preview, toolbar, cover upload, image drag-and-drop.
 * All text insertions use insertText() to preserve browser undo (Ctrl+Z).
 */
(function () {
    const textarea = document.getElementById('body_md');
    const preview = document.getElementById('preview');
    if (!textarea) return;

    // --- Undo-safe text insertion ---
    function insertText(text) {
        textarea.focus();
        document.execCommand('insertText', false, text);
        updatePreview();
    }

    function replaceRange(start, end, text) {
        textarea.focus();
        textarea.setSelectionRange(start, end);
        document.execCommand('insertText', false, text);
        updatePreview();
    }

    // --- Marked config ---
    if (typeof marked !== 'undefined') {
        marked.setOptions({ breaks: true, gfm: true });
    }

    function updatePreview() {
        if (preview && typeof marked !== 'undefined') {
            preview.innerHTML = marked.parse(textarea.value);
        }
    }

    textarea.addEventListener('input', updatePreview);

    // --- Tab switching ---
    const tabs = document.querySelectorAll('.editor-tab');
    const paneWrite = document.getElementById('pane-write');
    const panePreview = document.getElementById('pane-preview');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            if (tab.dataset.tab === 'preview') {
                updatePreview();
                paneWrite.classList.remove('active');
                panePreview.classList.add('active');
            } else {
                panePreview.classList.remove('active');
                paneWrite.classList.add('active');
                textarea.focus();
            }
        });
    });

    // --- Cover image upload ---
    const coverUpload = document.getElementById('cover-upload');
    const coverDropzone = document.getElementById('cover-dropzone');
    const coverPreview = document.getElementById('cover-preview');
    const coverImg = document.getElementById('cover-img');
    const coverInput = document.getElementById('cover-file');
    const coverHidden = document.getElementById('cover_image');
    const coverRemove = document.getElementById('cover-remove');

    if (coverDropzone) {
        coverDropzone.addEventListener('click', () => coverInput.click());

        coverDropzone.addEventListener('dragover', e => {
            e.preventDefault();
            coverDropzone.classList.add('drag-over');
        });
        coverDropzone.addEventListener('dragleave', () => coverDropzone.classList.remove('drag-over'));
        coverDropzone.addEventListener('drop', e => {
            e.preventDefault();
            coverDropzone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) uploadCover(e.dataTransfer.files[0]);
        });

        coverInput.addEventListener('change', () => {
            if (coverInput.files.length) uploadCover(coverInput.files[0]);
        });

        coverRemove.addEventListener('click', () => {
            coverHidden.value = '';
            coverImg.src = '';
            coverImg.style.display = 'none';
            coverPreview.style.display = 'none';
            coverDropzone.style.display = '';
        });
    }

    function uploadCover(file) {
        if (!file.type.startsWith('image/')) return;
        const fd = new FormData();
        fd.append('file', file);
        coverDropzone.innerHTML = '<span>Загрузка...</span>';

        fetch('/admin/upload', { method: 'POST', body: fd })
            .then(r => r.json())
            .then(data => {
                if (data.url) {
                    coverHidden.value = data.url;
                    coverImg.src = data.url;
                    coverImg.style.display = 'block';
                    coverPreview.style.display = 'block';
                    coverDropzone.style.display = 'none';
                }
                coverDropzone.innerHTML = '<span>Перетащите изображение или нажмите</span>';
            })
            .catch(() => {
                coverDropzone.innerHTML = '<span>Ошибка загрузки. Попробуйте снова</span>';
            });
    }

    // --- Drag-and-drop images into textarea ---
    textarea.addEventListener('dragover', e => {
        if (e.dataTransfer.types.includes('Files')) {
            e.preventDefault();
            textarea.classList.add('drag-over');
        }
    });
    textarea.addEventListener('dragleave', () => textarea.classList.remove('drag-over'));
    textarea.addEventListener('drop', e => {
        const files = e.dataTransfer.files;
        if (files.length && files[0].type.startsWith('image/')) {
            e.preventDefault();
            textarea.classList.remove('drag-over');
            uploadAndInsert(files[0]);
        }
    });

    function uploadAndInsert(file) {
        const fd = new FormData();
        fd.append('file', file);

        fetch('/admin/upload', { method: 'POST', body: fd })
            .then(r => r.json())
            .then(data => {
                if (data.url) {
                    var md = '\n![' + file.name + '](' + data.url + ')\n';
                    textarea.setSelectionRange(textarea.selectionStart, textarea.selectionStart);
                    insertText(md);
                }
            });
    }

    // --- Toolbar ---
    window.insertBold = function () { wrapSelection('**', '**'); };
    window.insertItalic = function () { wrapSelection('*', '*'); };
    window.insertCode = function () { wrapSelection('```\n', '\n```'); };
    window.insertHeading = function () { insertAtLineStart('## '); };
    window.insertList = function () { insertAtLineStart('- '); };
    window.insertQuote = function () { insertAtLineStart('> '); };

    window.insertImage = function () {
        var url = prompt('URL изображения:');
        if (url) {
            insertText('![](' + url + ')');
        }
    };

    window.insertLink = function () {
        var url = prompt('Введите URL:');
        if (url) wrapSelection('[', '](' + url + ')');
    };

    function wrapSelection(before, after) {
        var start = textarea.selectionStart;
        var end = textarea.selectionEnd;
        var selected = textarea.value.slice(start, end) || 'text';
        var replacement = before + selected + after;
        replaceRange(start, end, replacement);
        textarea.setSelectionRange(start + before.length, start + before.length + selected.length);
    }

    function insertAtLineStart(prefix) {
        var start = textarea.selectionStart;
        var lineStart = textarea.value.lastIndexOf('\n', start - 1) + 1;
        replaceRange(lineStart, lineStart, prefix);
        textarea.setSelectionRange(start + prefix.length, start + prefix.length);
    }

    // --- Keyboard shortcuts ---
    textarea.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') { e.preventDefault(); insertBold(); }
        if ((e.ctrlKey || e.metaKey) && e.key === 'i') { e.preventDefault(); insertItalic(); }
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); insertLink(); }
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            document.getElementById('editor-form').submit();
        }
        // Tab inserts spaces
        if (e.key === 'Tab') {
            e.preventDefault();
            insertText('    ');
        }
    });
})();
