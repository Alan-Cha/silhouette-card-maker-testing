### Run all tests
pytest test/

### Run only unit tests (no network)
pytest test/ -m unit

### Run a specific plugin's tests
pytest test/test_mtg_plugin.py

### Run with verbose output
pytest test/ -v