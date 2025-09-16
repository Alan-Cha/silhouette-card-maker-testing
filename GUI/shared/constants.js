const path = require('path');

// Directory paths
const GAME_DIR = path.join(__dirname, '../../game');
const FRONT_DIR = path.join(GAME_DIR, 'front');
const BACK_DIR = path.join(GAME_DIR, 'back');
const OUTPUT_DIR = path.join(GAME_DIR, 'output');
const DECKLIST_DIR = path.join(GAME_DIR, 'decklist');
const DOUBLE_SIDED_DIR = path.join(GAME_DIR, 'double_sided');

module.exports = {
    GAME_DIR,
    FRONT_DIR,
    BACK_DIR,
    OUTPUT_DIR,
    DECKLIST_DIR,
    DOUBLE_SIDED_DIR,
};