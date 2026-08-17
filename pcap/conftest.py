# conftest.py — pytest path configuration
#
# The PCAP/ folder IS the 'pcap' Python package.
# For "from pcap.processor import process_pcap" to work, Python needs
# the PARENT of PCAP/ (i.e. sih/) on sys.path.
#
# This file is auto-discovered by pytest at test collection time.

import sys
from pathlib import Path

# conftest.py lives at: .../sih/PCAP/conftest.py
# .parent       = .../sih/PCAP/   ← the package itself
# .parent.parent = .../sih/       ← must be on sys.path
_sih_dir = Path(__file__).resolve().parent.parent
if str(_sih_dir) not in sys.path:
    sys.path.insert(0, str(_sih_dir))
