class Navbar extends HTMLElement {
    constructor() {
        super();
    }

    static get observedAttributes() {
        return ['current-step'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'current-step') {
            this.updateContent();
        }
    }

    connectedCallback() {
        this.updateContent();
        // Update active state based on current URL
        this.updateActiveState();
        // Listen for navigation events
        window.addEventListener('popstate', () => this.updateActiveState());
    }

    updateActiveState() {
        const currentPath = window.location.pathname;
        if (currentPath.includes('/Home/')) {
            this.setAttribute('current-step', '1');
        } else if (currentPath.includes('/MagicTheGathering/')) {
            this.setAttribute('current-step', '2');
        } else if (currentPath.includes('/CreatePDF/')) {
            this.setAttribute('current-step', '3');
        }
    }

    updateContent() {
        const currentStep = parseInt(this.getAttribute('current-step')) || 1;
        this.innerHTML = `
            <nav class="fixed top-0 left-0 right-0 paper-surface backdrop-blur-sm z-10">
                <div class="w-full flex justify-center px-8 py-4">
                    <div class="w-[600px] flex items-center justify-center">
                        <div class="flex items-center justify-between w-full max-w-[500px]">
                            ${this.renderStep(1, 'Choose Game', '../Home/home.html', currentStep)}
                            <div class="w-16 h-0.5 bg-content-light/30">&nbsp;</div>
                            ${this.renderStep(2, 'Card List', '../MagicTheGathering/decklist.html', currentStep)}
                            <div class="w-16 h-0.5 bg-content-light/30">&nbsp;</div>
                            ${this.renderStep(3, 'Create PDF', '../CreatePDF/create.html', currentStep)}
                        </div>
                    </div>
                </div>
            </nav>
        `;
    }

    renderStep(step, label, href, currentStep) {
        const isCurrent = step === currentStep;
        const linkClasses = 'flex-shrink-0 group relative flex justify-center ' + 
            (isCurrent ? '' : 'opacity-70 hover:opacity-100 transition-opacity');
        
        const containerClasses = 'flex items-center transition-all duration-200 rounded-full border-2 border-dashed border-content-light overflow-hidden whitespace-nowrap ' +
            (isCurrent ? 'w-full px-4 bg-content-light text-surface font-medium' : 'w-8 h-8 group-hover:w-full group-hover:px-4 bg-surface-light text-content');

        const numberClasses = 'w-8 h-8 flex items-center justify-center absolute left-0';
        const labelClasses = 'pl-4 transition-all duration-200 overflow-hidden ' +
            (isCurrent ? 'opacity-100 w-auto' : 'opacity-0 w-0 group-hover:w-auto group-hover:opacity-100');

        return `
            <a href="${href}" class="${linkClasses}">
                <div class="${containerClasses}">
                    <div class="${numberClasses}">${step}</div>
                    <div class="${labelClasses}">${label}</div>
                </div>
            </a>
        `;r();
        }
}

customElements.define('nav-bar', Navbar);