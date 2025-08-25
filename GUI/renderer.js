let cardNames = [];
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

    document.getElementById('longForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        const text = document.getElementById('longText').value;
        console.log('Raw input:', text);
        // Parse each line for quantity, card name, set code, and set number
        text.split(/\r?\n/).map(line => line.trim()).filter(line => line.length > 0).forEach(line => {
            // Flexible parsing for any combination
            let qty = 1;
            let name = '';
            let setCode = undefined;
            let setNumber = undefined;
            // Extract quantity (e.g., "2x", "2 x", "2 ")
            let qtyMatch = line.match(/^(\d+)\s*x?\s*/i);
            if (qtyMatch) {
                qty = parseInt(qtyMatch[1], 10);
                line = line.slice(qtyMatch[0].length).trim();
            }
            // Extract set code in parentheses (e.g., "(eoc)")
            let setCodeMatch = line.match(/\(([^")]+)\)/);
            if (setCodeMatch) {
                setCode = setCodeMatch[1].trim();
                line = line.replace(/\([^")]+\)/, '').trim();
            }
            // Extract set number (last number in line)
            let setNumberMatch = line.match(/(\d+)$/);
            if (setNumberMatch) {
                setNumber = setNumberMatch[1].trim();
                line = line.replace(/(\d+)$/, '').trim();
            }
            // Remaining is the card name
            name = line.trim();
            for (let i = 0; i < qty; i++) {
                let cardObj = { name };
                if (setCode) cardObj.setCode = setCode;
                if (setNumber) cardObj.setNumber = setNumber;
                cardObj.qty = qty;
                parsedCards.push(cardObj);
            }
        });
        console.log('Parsed cards:', parsedCards);
        cardData = [];
        document.getElementById('output').innerText = 'Loading...';
        for (const card of parsedCards) {
            // Use fetchCardData for all cases
            const json = await fetchCardData(card.name, card.setCode, card.setNumber);
            cardData.push(json);
            card.setCode = json.set ? json.set.toUpperCase() : card.setCode;
            card.setNumber = json.collector_number || card.setNumber;
        }
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
