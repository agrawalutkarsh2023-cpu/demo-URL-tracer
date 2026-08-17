"""Quick smoke test — runs process_pcap on the demo PCAP and prints results."""
import sys
from pathlib import Path

# Ensure sih/ is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pcap.processor import process_pcap

r = process_pcap("demo/demo_attacks.pcap")

sep = "=" * 55
print(sep)
print("  PCAP MODULE -- END-TO-END SMOKE TEST")
print(sep)
print("  status              :", r["status"])
print("  filename            :", r["filename"])
print("  packets_processed   :", r["packets_processed"])
print("  http_requests       :", r["http_requests"])
print("  inspectable_requests:", r["inspectable_requests"])
print("  uninspectable (TLS) :", r["uninspectable"])
print("  records returned    :", len(r["records"]))
print("  error               :", r["error"])
print()
print("  Sample records (first 3):")
for i, rec in enumerate(r["records"][:3]):
    print(f"  [{i+1}] {rec['method']:7}  {rec['url']}")
print("  ...")
print()
print("  Backend import:")
print("  from pcap.processor import process_pcap  --> OK")
print(sep)
