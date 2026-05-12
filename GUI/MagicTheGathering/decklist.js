const { getFrontDir } = require('../shared/constants');
// Unified card structure: each card contains user input + fetched data + selected set
let cards = []; // Array of { name, qty, requestedSetCode, requestedSetNumber, cardData, selectedSetCode, selectedSetNumber }

async function fetchCardData(name, setCode = null, setNumber = null) {
    let url;
    if (setCode && setNumber) {
        url = `https://api.scryfall.com/cards/${setCode.toLowerCase()}/${setNumber}`;
    } else if (setCode) {
        url = `https://api.scryfall.com/cards/named?fuzzy=${encodeURIComponent(name)}&set=${setCode.toLowerCase()}`;
    } else {
        url = `https://api.scryfall.com/cards/named?fuzzy=${encodeURIComponent(name)}`;
    }
    console.log('Fetching card:', name, 'Set:', setCode, 'Number:', setNumber);
    try {
        const response = await fetch(url);
        if (response.ok) {
            const json = await response.json();
            console.log('Received data for', name, json);
            return json;
        } else {
            console.error('Error fetching', name, response.status);
            return { error: `Card not found: ${name}` };
        }
    } catch (err) {
        console.error('Error fetching', name, err);
        return { error: `Error fetching: ${name}` };
    }
}

function regenerateTextboxFromCardData() {
    const longText = document.getElementById('longText');
    if (!longText) return;

    const newLines = cards.map(card => {
        let line = '';
        const qty = card.qty || 1;
        if (qty > 1) {
            line += qty + 'x ';
        }
        line += card.name;
        if (card.selectedSetCode) {
            line += ` (${card.selectedSetCode})`;
        }
        if (card.selectedSetNumber) {
            line += ` ${card.selectedSetNumber}`;
        }
        return line;
    });

    longText.value = newLines.join('\n');
    if (longText.value) {
        sessionStorage.setItem('mtg-decklist', longText.value);
    }
}

window.onload = function () {
    // Restore decklist from sessionStorage if available
    const savedDecklist = sessionStorage.getItem('mtg-decklist');
    if (savedDecklist) {
        document.getElementById('longText').value = savedDecklist;
    }
    
    // Restore cached cards from sessionStorage
    const savedCards = sessionStorage.getItem('mtg-cards');
    if (savedCards) {
        try {
            cards = JSON.parse(savedCards);
            // Render the cached card results
            renderCardResults();
        } catch (e) {
            console.error('Error restoring cached cards:', e);
        }
    }
    
    // Save decklist when Enter is pressed in the textarea
    document.getElementById('longText').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const decklistText = this.value;
            if (decklistText) {
                sessionStorage.setItem('mtg-decklist', decklistText);
            }
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        const dropdowns = document.querySelectorAll('[id^="set-dropdown-container-"]');
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target) && 
                !e.target.id?.includes('card-set-') && 
                !e.target.id?.includes('set-select-')) {
                dropdown.classList.add('hidden');
                dropdown.classList.remove('block');
            }
        });
    });
    // Next: Create PDF button - export images to folder then navigate
    document.getElementById('nextCreatePdfBtn').addEventListener('click', async function () {
        if (typeof window.showLoadingOverlay === 'function') {
            window.showLoadingOverlay({
                title: 'Preparing Cards',
                message: 'Exporting card images for PDF...'
            });
        }

        try {
            // Only export if we have cards
            if (cards.length > 0) {
                const fs = window.require ? window.require('fs') : require('fs');
                const path = window.require ? window.require('path') : require('path');
                const frontDir = getFrontDir();
                if (!fs.existsSync(frontDir)) {
                    fs.mkdirSync(frontDir, { recursive: true });
                }
                
                // Check if there are existing images in the front folder
                const existingFiles = fs.readdirSync(frontDir).filter(f => f.endsWith('.png') || f.endsWith('.jpg') || f.endsWith('.jpeg'));
                if (existingFiles.length > 0) {
                    const shouldClear = confirm(`There are ${existingFiles.length} image(s) already in the front folder. Would you like to clear them before adding new images?`);
                    if (shouldClear) {
                        // Clear existing images
                        for (const file of existingFiles) {
                            fs.unlinkSync(path.join(frontDir, file));
                        }
                    }
                }
                
                let imgCount = 1;
                for (let i = 0; i < cards.length; i++) {
                    const data = cards[i].cardData;
                    if (data.error) continue;
                    // Handle double-faced cards
                    if (data.card_faces && Array.isArray(data.card_faces) && data.card_faces.length > 1) {
                        for (let f = 0; f < data.card_faces.length; f++) {
                            let imgUrl = data.card_faces[f].image_uris ? data.card_faces[f].image_uris.png : null;
                            if (!imgUrl) continue;
                            let faceName = data.card_faces[f].name.replace(/[^a-zA-Z0-9]/g, ' ');
                            faceName = faceName.split(' ').map((w, idx) => idx === 0 ? w.toLowerCase() : w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join('');
                            faceName = faceName.replace(/\s+/g, '');
                            let filename = path.join(frontDir, `${imgCount}${faceName}1.png`);
                            const response = await fetch(imgUrl);
                            const buffer = Buffer.from(await response.arrayBuffer());
                            fs.writeFileSync(filename, buffer);
                            imgCount++;
                        }
                    } else {
                        let imgUrl = data.image_uris ? data.image_uris.png : (data.card_faces && data.card_faces[0].image_uris ? data.card_faces[0].image_uris.png : null);
                        if (!imgUrl) continue;
                        let cardName = data.name.replace(/[^a-zA-Z0-9]/g, ' ');
                        cardName = cardName.split(' ').map((w, idx) => idx === 0 ? w.toLowerCase() : w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join('');
                        cardName = cardName.replace(/\s+/g, '');
                        let filename = path.join(frontDir, `${imgCount}${cardName}1.png`);
                        const response = await fetch(imgUrl);
                        const buffer = Buffer.from(await response.arrayBuffer());
                        fs.writeFileSync(filename, buffer);
                        imgCount++;
                    }
                }
            }

            // Save decklist to sessionStorage before navigating
            const decklistText = document.getElementById('longText').value;
            if (decklistText) {
                sessionStorage.setItem('mtg-decklist', decklistText);
            }

            // Navigate to Create PDF page (no alert)
            location.href = '../CreatePDF/create.html';
        } catch (err) {
            if (typeof window.hideLoadingOverlay === 'function') {
                window.hideLoadingOverlay();
            }
            alert('Error preparing card images:\n' + err);
        }
    });
    // Export decklist button logic
    document.getElementById('exportBtn').addEventListener('click', function () {
        // Export cards as text
        let exportLines = cards.map(card => {
            let line = '';
            let qty = card.qty || 1;
            if (qty > 1) {
                line += qty + 'x ';
            }
            line += card.name;
            if (card.selectedSetCode) {
                line += ` (${card.selectedSetCode})`;
            }
            if (card.selectedSetNumber) {
                line += ` ${card.selectedSetNumber}`;
            }
            return line;
        });
        let blob = new Blob([exportLines.join('\n')], { type: 'text/plain' });
        let url = URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = url;
        a.download = 'card_export.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
    // Clear array when input field is manually changed
    document.getElementById('longText').addEventListener('input', function () {
        cards = [];
    });

    document.getElementById('longForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        const text = document.getElementById('longText').value;
        
        // Save decklist to sessionStorage
        if (text) {
            sessionStorage.setItem('mtg-decklist', text);
        }
        
        console.log('Raw input:', text);
        // Parse each line for quantity, card name, set code, and set number
        cards = [];
        text.split(/\r?\n/).map(line => line.trim()).filter(line => line.length > 0).forEach(line => {
            // Flexible parsing: always extract card name, optionally extract quantity, set code, set number, ignore category info
            // Examples:
            // "1x Ancient Copper Dragon (clb) 161 [Copy Target,Treasures]"
            // "Ancient Copper Dragon"
            let qty = 1;
            let name = '';
            let setCode = undefined;
            let setNumber = undefined;
            // Extract quantity
            const qtyMatch = line.match(/^(\d+)x?/);
            if (qtyMatch) {
                qty = parseInt(qtyMatch[1], 10);
                line = line.replace(/^(\d+)x?\s*/, '');
            }
            // Extract set code in parentheses
            const setCodeMatch = line.match(/\(([^)]+)\)/);
            if (setCodeMatch) {
                setCode = setCodeMatch[1].trim();
                line = line.replace(/\([^)]+\)/, '').trim();
            }
            // todo: there is bug here for card names like Celebr-8000. This will think it is a set number.
            // Extract set number (strict: POR-87 or just digits)
            // Match 'POR-87', 'CN2-30' (any number of uppercase letter, 0 or more digits, hyphen, any number of digits), or just digits
            let setNumberMatch = line.match(/\b([A-Z]+\d*-\d+)\b/);
            if (!setNumberMatch) {
                setNumberMatch = line.match(/\b(\d+)\b/);
            }
            if (setNumberMatch) {
                setNumber = setNumberMatch[1].trim();
                line = line.replace(setNumberMatch[0], '').trim();
            }
            // Extract card name (remaining text before any extra info)
            // todo: bug for boggart trawler // boggart bog (mdfc)
            name = line.split(/\s*\[/)[0].trim();
            for (let i = 0; i < qty; i++) {
                cards.push({ name, requestedSetCode: setCode, requestedSetNumber: setNumber, qty, cardData: null, selectedSetCode: setCode, selectedSetNumber: setNumber });
            }
        });
        console.log('Parsed cards:', cards);
        document.getElementById('output').innerText = 'Loading...';
        // Parallelize fetchCardData calls
        const fetchPromises = cards.map(card => fetchCardData(card.name, card.requestedSetCode, card.requestedSetNumber));
        const results = await Promise.all(fetchPromises);
        results.forEach((json, i) => {
            cards[i].cardData = json;
            cards[i].selectedSetCode = json.set ? json.set.toUpperCase() : cards[i].selectedSetCode;
            cards[i].selectedSetNumber = json.collector_number || cards[i].selectedSetNumber;
        });
        
        // Save cards to sessionStorage
        sessionStorage.setItem('mtg-cards', JSON.stringify(cards));
        
        regenerateTextboxFromCardData();
        renderCardResults();
    });
}

function renderCardResults() {
        let html = '<div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">';
        for (let i = 0; i < cards.length; i++) {
            const data = cards[i].cardData;
            const card = cards[i];
            if (data.error) {
                html += `
                    <div class="flex flex-col p-4 bg-red-50 border border-red-200 rounded-lg" id="card-li-${i}">
                        <strong class="text-red-500">${card ? card.name : 'Unknown'}</strong>
                        <p class="text-sm mt-2 text-red-400">${data.error}</p>
                    </div>`;
            } else {
                let imgUrl = data.image_uris ? data.image_uris.png : (data.card_faces && data.card_faces[0].image_uris ? data.card_faces[0].image_uris.png : null);
                let setCode = card.selectedSetCode || (data.set ? data.set.toUpperCase() : '');
                let availableSets = (data.prints_search_uri ? data.prints_search_uri : null);
                html += `
                    <div class="flex flex-col" id="card-li-${i}">
                        ${imgUrl ? `
                            <div class="relative">
                                <div class="aspect-[745/1040] rounded-lg overflow-hidden shadow transition-shadow duration-200 hover:shadow-md">
                                    <img id="card-img-${i}" src="${imgUrl}" alt="${data.name}" class="w-full h-full object-cover" loading="lazy" />
                                </div>
                                ${data.card_faces && data.card_faces.length > 1 ? `
                                    <button id="flip-btn-${i}" 
                                            class="absolute bottom-2 right-2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-colors"
                                            title="Flip card">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                        </svg>
                                    </button>
                                ` : ''}
                            </div>` : 
                            '<div class="aspect-[745/1040] bg-gray-100 flex items-center justify-center rounded-lg"><em>No image available</em></div>'}
                        <div class="mt-2">
                            <div class="flex items-start">
                                <div class="flex-grow">
                                    <strong class="text-sm text-content inline-flex items-start flex-wrap">
                                        <span class="break-all">${data.name}</span>
                                        <span id="setcode-dropdown-wrap-${i}" class="relative inline-flex items-center shrink-0">
                                            <span id="card-set-${i}" class="cursor-pointer hover:underline ml-1" title="Click to change set">[${setCode}]</span>
                                        </span>
                                    </strong>
                                    <div id="set-dropdown-container-${i}" class="hidden absolute z-50 bg-white shadow-lg rounded-md border border-gray-200" style="min-width: 200px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>`;
            }
        }
        html += '</div>';
        document.getElementById('output').innerHTML = html;

        // Set up flip buttons for double-faced cards
        for (let i = 0; i < cards.length; i++) {
            const data = cards[i].cardData;
            if (!data.error && data.card_faces && data.card_faces.length > 1) {
                const flipBtn = document.getElementById(`flip-btn-${i}`);
                if (flipBtn) {
                    let showingFront = true;
                    const frontImg = data.card_faces[0].image_uris?.png;
                    const backImg = data.card_faces[1].image_uris?.png;
                    
                    flipBtn.addEventListener('click', function(e) {
                        const imgElem = document.getElementById(`card-img-${i}`);
                        if (showingFront && backImg) {
                            imgElem.src = backImg;
                            showingFront = false;
                        } else if (frontImg) {
                            imgElem.src = frontImg;
                            showingFront = true;
                        }
                        e.stopPropagation();
                    });
                }
            }
        }

        // For each card, fetch available sets and create dropdown
        for (let i = 0; i < cards.length; i++) {
            const data = cards[i].cardData;
            const cardObj = cards[i];
            if (!data.error && data.prints_search_uri) {
                fetch(data.prints_search_uri)
                    .then(resp => resp.json())
                    .then(json => {
                        const sets = {};
                        json.data.forEach(card => {
                            if (card.set && card.set_name && card.image_uris) {
                                sets[card.set] = card.set_name;
                            }
                        });
                        const dropdown = document.createElement('select');
                        dropdown.id = `set-select-${i}`;
                        dropdown.className = 'card-set-dropdown';
                        // Sort set codes alphabetically by set name
                        const sortedSetCodes = Object.keys(sets).sort((a, b) => sets[a].localeCompare(sets[b]));
                        for (const setCode of sortedSetCodes) {
                            const option = document.createElement('option');
                            option.value = setCode;
                            option.text = `${sets[setCode]} [${setCode.toUpperCase()}]`;
                            if (setCode.toUpperCase() === cardObj.selectedSetCode) {
                                option.selected = true;
                            }
                            dropdown.appendChild(option);
                        }
                        dropdown.addEventListener('change', async function () {
                            const newSet = this.value;
                            const newData = await fetchCardData(data.name, newSet);
                            let newImgUrl = newData.image_uris ? newData.image_uris.png : (newData.card_faces && newData.card_faces[0].image_uris ? newData.card_faces[0].image_uris.png : null);
                            let newSetCode = newData.set ? newData.set.toUpperCase() : '';
                            document.getElementById(`card-img-${i}`).src = newImgUrl || '';
                            document.getElementById(`card-set-${i}`).textContent = `[${newSetCode}]`;

                            // Update the unified card object with new data and selected set
                            cardObj.cardData = newData;
                            cardObj.selectedSetCode = newSetCode;
                            cardObj.selectedSetNumber = newData.collector_number || cardObj.selectedSetNumber;
                            cardObj.requestedSetCode = newSetCode || cardObj.requestedSetCode;
                            cardObj.requestedSetNumber = newData.collector_number || cardObj.requestedSetNumber;
                            
                            // Save to sessionStorage and regenerate textbox
                            sessionStorage.setItem('mtg-cards', JSON.stringify(cards));
                            regenerateTextboxFromCardData();
                        });
                        const setDropdownContainer = document.getElementById(`set-dropdown-container-${i}`);
                        setDropdownContainer.innerHTML = '';
                        setDropdownContainer.appendChild(dropdown);
                        const setCodeElem = document.getElementById(`card-set-${i}`);
                        setCodeElem.style.cursor = 'pointer';
                        setCodeElem.title = 'Click to change set';
                        setCodeElem.addEventListener('mouseenter', function () {
                            setCodeElem.style.textDecoration = 'underline';
                        });
                        setCodeElem.addEventListener('mouseleave', function () {
                            setCodeElem.style.textDecoration = 'none';
                        });
                        setCodeElem.addEventListener('click', function (e) {
                            // Position the dropdown relative to the set code element
                            const rect = setCodeElem.getBoundingClientRect();
                            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                            const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
                            
                            setDropdownContainer.style.top = (rect.bottom + scrollTop) + 'px';
                            setDropdownContainer.style.left = (rect.left + scrollLeft) + 'px';
                            
                            setDropdownContainer.classList.remove('hidden');
                            setDropdownContainer.classList.add('block');
                            
                            dropdown.focus();
                            
                            // Open the dropdown immediately
                            if (typeof dropdown.showDropdown === 'function') {
                                dropdown.showDropdown();
                            } else {
                                const event = new MouseEvent('mousedown', { bubbles: true });
                                dropdown.dispatchEvent(event);
                            }
                            
                            // Prevent event bubbling
                            e.stopPropagation();
                        });
                        dropdown.addEventListener('blur', function () {
                            setDropdownContainer.classList.add('hidden');
                            setDropdownContainer.classList.remove('block');
                            document.getElementById(`setcode-dropdown-wrap-${i}`).classList.remove('hidden');
                        });
                    });
            }
        }
}
