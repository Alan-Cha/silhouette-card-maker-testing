import re

# Moxfield format pattern
# Examples:
#   1 Sol Ring (SLD) 123★
#   4x Lightning Bolt (2XM) 117
#   1 Some Card (SET) 123-456
MOXFIELD_PATTERN = re.compile(r'(\d+)x?\s+(.+?)\s+\((\w+)\)\s+([^\s]+)')

# Deckstats format pattern
# Examples:
#   1 [SLD#1494★] Sol Ring
#   1 [2XM#310] Ash Barrens
#   1 Blinkmoth Nexus
DECKSTATS_PATTERN = re.compile(r'^(\d+)\s+(?:\[(\w+)?#([^\]]+)\]\s+)?(.+)$')
