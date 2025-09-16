const { FRONT_DIR } = require('../shared/constants');
let cardData = [];
let parsedCards = []; // Array of { name, setCode, setNumber, qty }

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
window.onload = function () {
    // Export front images to ../game/front using Node.js fs (Electron only)
    document.getElementById('exportImagesFSBtn').addEventListener('click', async function () {
        const fs = window.require ? window.require('fs') : require('fs');
        const path = window.require ? window.require('path') : require('path');
        if (!fs.existsSync(FRONT_DIR)) {
            fs.mkdirSync(FRONT_DIR, { recursive: true });
        }
        let imgCount = 1;
        for (let i = 0; i < cardData.length; i++) {
            const data = cardData[i];
            if (data.error) continue;
            // Handle double-faced cards
            if (data.card_faces && Array.isArray(data.card_faces) && data.card_faces.length > 1) {
                for (let f = 0; f < data.card_faces.length; f++) {
                    let imgUrl = data.card_faces[f].image_uris ? data.card_faces[f].image_uris.png : null;
                    if (!imgUrl) continue;
                    let faceName = data.card_faces[f].name.replace(/[^a-zA-Z0-9]/g, ' ');
                    faceName = faceName.split(' ').map((w, idx) => idx === 0 ? w.toLowerCase() : w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join('');
                    faceName = faceName.replace(/\s+/g, '');
                    let filename = path.join(FRONT_DIR, `${imgCount}${faceName}1.png`);
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
                let filename = path.join(FRONT_DIR, `${imgCount}${cardName}1.png`);
                const response = await fetch(imgUrl);
                const buffer = Buffer.from(await response.arrayBuffer());
                fs.writeFileSync(filename, buffer);
                imgCount++;
            }
        }
        alert('Images exported to ../../game/front');
    });
    // Export front images as ZIP button logic
    document.getElementById('exportImagesZipBtn').addEventListener('click', async function () {
        if (typeof JSZip === 'undefined') {
            alert('JSZip library is required for ZIP export. Please add JSZip to your project.');
            return;
        }
        const zip = new JSZip();
        for (let i = 0; i < cardData.length; i++) {
            const data = cardData[i];
            if (data.error) continue;
            let imgUrl = data.image_uris ? data.image_uris.png : (data.card_faces && data.card_faces[0].image_uris ? data.card_faces[0].image_uris.png : null);
            if (!imgUrl) continue;
            let cardName = data.name.replace(/[^a-zA-Z0-9]/g, ' ');
            cardName = cardName.split(' ').map((w, idx) => idx === 0 ? w.toLowerCase() : w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join('');
            cardName = cardName.replace(/\s+/g, '');
            let filename = `front/${i+1}${cardName}1.png`;
            const response = await fetch(imgUrl);
            const blob = await response.blob();
            const arrayBuffer = await blob.arrayBuffer();
            zip.file(filename, arrayBuffer);
        }
        const zipBlob = await zip.generateAsync({ type: 'blob' });
        const url = URL.createObjectURL(zipBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'front_images.zip';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
    
    // Export decklist button logic
    document.getElementById('exportBtn').addEventListener('click', function () {
        // Export parsedCards as text
        let exportLines = parsedCards.map(card => {
            let line = '';
            let qty = card.qty || 1;
            if (qty > 1) {
                line += qty + 'x ';
            }
            line += card.name;
            if (card.setCode) {
                line += ` (${card.setCode})`;
            }
            if (card.setNumber) {
                line += ` ${card.setNumber}`;
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
    function regenerateTextboxFromCardData() {
        const longText = document.getElementById('longText');
        let newLines = parsedCards.map(card => {
            console.log('Regenerating card:', card);
            let line = '';
            let qty = card.qty || 1;
            if (qty > 1) {
                line += qty + 'x ';
            }
            line += card.name;
            if (card.setCode) {
                line += ` (${card.setCode})`;
            }
            if (card.setNumber) {
                line += ` ${card.setNumber}`;
            }
            return line;
        });
        longText.value = newLines.join('\n');
    }

    // Clear arrays when input field is manually changed
    document.getElementById('longText').addEventListener('input', function () {
        parsedCards = [];
        cardData = [];
        cardNames = [];
    });

    document.getElementById('longForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        const text = document.getElementById('longText').value;
        console.log('Raw input:', text);
        // Parse each line for quantity, card name, set code, and set number
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
                parsedCards.push({ name, setCode, setNumber, qty });
            }
        });
        console.log('Parsed cards:', parsedCards);
        cardData = [];
        document.getElementById('output').innerText = 'Loading...';
        // Parallelize fetchCardData calls
        const fetchPromises = parsedCards.map(card => fetchCardData(card.name, card.setCode, card.setNumber));
        const results = await Promise.all(fetchPromises);
        results.forEach((json, i) => {
            cardData.push(json);
            parsedCards[i].setCode = json.set ? json.set.toUpperCase() : parsedCards[i].setCode;
            parsedCards[i].setNumber = json.collector_number || parsedCards[i].setNumber;
        });
        regenerateTextboxFromCardData();
        let html = '<h3>Results:</h3><div id="card-results-flex">';
        for (let i = 0; i < cardData.length; i++) {
            const data = cardData[i];
            const card = parsedCards[i];
            if (data.error) {
                html += `<div class="card-li" id="card-li-${i}"><strong>${card ? card.name : 'Unknown'}</strong>: ${data.error}</div>`;
            } else {
                let imgUrl = data.image_uris ? data.image_uris.png : (data.card_faces && data.card_faces[0].image_uris ? data.card_faces[0].image_uris.png : null);
                let setCode = data.set ? data.set.toUpperCase() : '';
                let availableSets = (data.prints_search_uri ? data.prints_search_uri : null);
                html += `<div class="card-li" id="card-li-${i}">
        ${imgUrl ? `<img id="card-img-${i}" src="${imgUrl}" alt="${data.name}" class="card-img" />` : '<em>No image available</em>'}
  <div><strong>${data.name}</strong> <span id="setcode-dropdown-wrap-${i}"><strong id="card-set-${i}" class="card-set" >[${setCode}]</strong></span><span id="set-dropdown-container-${i}" style="display:none;"></span></div>
      </div>`;
            }
        }
        html += '</div>';
        document.getElementById('output').innerHTML = html;

        // For each card, fetch available sets and create dropdown
        for (let i = 0; i < cardData.length; i++) {
            const data = cardData[i];
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
                            if (setCode.toUpperCase() === (data.set ? data.set.toUpperCase() : '')) {
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

                            // Update parsedCards with the new set code and number
                            parsedCards[i].setCode = newSetCode;
                            parsedCards[i].setNumber = newData.collector_number ? newData.collector_number : parsedCards[i].setNumber;
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
                        setCodeElem.addEventListener('click', function () {
                            setDropdownContainer.style.display = 'inline';
                            document.getElementById(`setcode-dropdown-wrap-${i}`).style.display = 'none';
                            // Hide the card name instead of removing it
                            const cardLi = document.getElementById(`card-li-${i}`);
                            const cardNameElem = cardLi.querySelector('strong');
                            if (cardNameElem) {
                                cardNameElem.style.display = 'none';
                            }
                            dropdown.focus();
                            // Open the dropdown immediately
                            if (typeof dropdown.showDropdown === 'function') {
                                dropdown.showDropdown();
                            } else {
                                // For most browsers, dispatching a click event will open the dropdown
                                const event = new MouseEvent('mousedown', { bubbles: true });
                                dropdown.dispatchEvent(event);
                            }
                        });
                        dropdown.addEventListener('blur', function () {
                            setDropdownContainer.style.display = 'none';
                            document.getElementById(`setcode-dropdown-wrap-${i}`).style.display = 'inline';
                            const cardLi = document.getElementById(`card-li-${i}`);
                            const cardNameElem = cardLi.querySelector('strong');
                            if (cardNameElem) {
                                cardNameElem.style.display = 'inline';
                            }
                        });
                        dropdown.addEventListener('change', async function () {
                            const newSet = this.value;
                            const newData = await fetchCardData(data.name, newSet);
                            let newImgUrl = newData.image_uris ? newData.image_uris.png : (newData.card_faces && newData.card_faces[0].image_uris ? newData.card_faces[0].image_uris.png : null);
                            let newSetCode = newData.set ? newData.set.toUpperCase() : '';
                        });
                    });
            }
        }
    });
}
