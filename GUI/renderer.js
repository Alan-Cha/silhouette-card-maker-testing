let cardNames = [];
let cardData = [];

async function fetchCardData(name, setCode = null) {
    let url = setCode
        ? `https://api.scryfall.com/cards/named?fuzzy=${encodeURIComponent(name)}&set=${setCode}`
        : `https://api.scryfall.com/cards/named?fuzzy=${encodeURIComponent(name)}`;
    console.log('Fetching card:', name, 'Set:', setCode);
    const response = await fetch(url);
    if (response.ok) {
        const json = await response.json();
        console.log('Received data for', name, json);
        return json;
    } else {
        console.error('Error fetching', name, response.status);
        return { error: `Card not found: ${name}` };
    }
}
window.onload = function () {
    document.getElementById('longForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        const text = document.getElementById('longText').value;
        console.log('Raw input:', text);
        cardNames = text.split(/\r?\n/).map(line => line.trim()).filter(line => line.length > 0);
        console.log('Parsed card names:', cardNames);
        cardData = [];
        document.getElementById('output').innerText = 'Loading...';
        for (const name of cardNames) {
            const data = await fetchCardData(name);
            cardData.push(data);
        }
        console.log('All card data:', cardData);
        let html = '<h3>Results:</h3><ul style="list-style:none;padding:0;">';
        for (let i = 0; i < cardNames.length; i++) {
            const data = cardData[i];
            if (data.error) {
                html += `<li><strong>${cardNames[i]}</strong>: ${data.error}</li>`;
            } else {
                let imgUrl = data.image_uris ? data.image_uris.png : (data.card_faces && data.card_faces[0].image_uris ? data.card_faces[0].image_uris.png : null);
                let setCode = data.set ? data.set.toUpperCase() : '';
                let availableSets = (data.prints_search_uri ? data.prints_search_uri : null);
                html += `<li style="margin-bottom:30px;" id="card-li-${i}">
        ${imgUrl ? `<img id="card-img-${i}" src="${imgUrl}" alt="${data.name}" style="max-width:300px;display:block;margin:10px auto;" />` : '<em>No image available</em>'}
  <div><strong>${data.name}</strong> <span id="setcode-dropdown-wrap-${i}"><strong id="card-set-${i}" style="color:#888;cursor:pointer;">[${setCode}]</strong></span><span id="set-dropdown-container-${i}" style="display:none;"></span></div>
      </li>`;
            }
        }
        html += '</ul>';
        document.getElementById('output').innerHTML = html;

        // For each card, fetch available sets and create dropdown
        for (let i = 0; i < cardNames.length; i++) {
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
                        });
                        const setDropdownContainer = document.getElementById(`set-dropdown-container-${i}`);
                        setDropdownContainer.innerHTML = '';
                        setDropdownContainer.appendChild(dropdown);
                        const setCodeElem = document.getElementById(`card-set-${i}`);
                        setCodeElem.addEventListener('click', function () {
                            setDropdownContainer.style.display = 'inline';
                            document.getElementById(`setcode-dropdown-wrap-${i}`).style.display = 'none';
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
