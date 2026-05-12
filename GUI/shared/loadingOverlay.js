(function () {
    function ensureOverlay() {
        let overlay = document.getElementById('sharedLoadingOverlay');
        if (overlay) {
            return overlay;
        }

        overlay = document.createElement('div');
        overlay.id = 'sharedLoadingOverlay';
        overlay.className = 'fixed inset-0 bg-surface-dark/95 flex-col items-center justify-center z-50 hidden';
        overlay.innerHTML = `
            <div class="paper-element p-8 flex flex-col items-center gap-8">
                <div class="flex items-center justify-center gap-8">
                    <div class="relative w-32 h-44">
                        <div class="absolute inset-0 bg-surface-light border-2 border-content/10 rounded-lg shadow-lg"></div>
                        <div class="absolute inset-0 bg-surface-light border-2 border-content/10 rounded-lg shadow-lg animate-card-slide-1"></div>
                        <div class="absolute inset-0 bg-surface-light border-2 border-content/10 rounded-lg shadow-lg animate-card-slide-2"></div>
                        <div class="absolute inset-0 bg-surface-light border-2 border-content/10 rounded-lg shadow-lg animate-card-slide-3"></div>
                    </div>
                </div>
                <div class="text-content text-center">
                    <h3 id="sharedLoadingOverlayTitle" class="text-lg font-medium mb-2">Creating PDF</h3>
                    <p id="sharedLoadingOverlayMessage" class="text-content-light">Processing card images...</p>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        return overlay;
    }

    function showLoadingOverlay(options = {}) {
        const overlay = ensureOverlay();
        const titleElement = document.getElementById('sharedLoadingOverlayTitle');
        const messageElement = document.getElementById('sharedLoadingOverlayMessage');

        titleElement.textContent = options.title || 'Creating PDF';
        messageElement.textContent = options.message || 'Processing card images...';

        overlay.classList.remove('hidden');
        overlay.classList.add('flex');
    }

    function hideLoadingOverlay() {
        const overlay = document.getElementById('sharedLoadingOverlay');
        if (!overlay) {
            return;
        }

        overlay.classList.remove('flex');
        overlay.classList.add('hidden');
    }

    window.showLoadingOverlay = showLoadingOverlay;
    window.hideLoadingOverlay = hideLoadingOverlay;
})();
