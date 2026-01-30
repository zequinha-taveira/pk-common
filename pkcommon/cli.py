import argparse
import json
import sys
from dataclasses import asdict
from pkcommon.core import PicoKeyDiscovery

def main():
    parser = argparse.ArgumentParser(description="PicoKey SDK CLI Tool")
    parser.add_argument("--list", action="store_true", help="List all connected PicoKey devices")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    args = parser.parse_args()
    
    if args.list:
        discovery = PicoKeyDiscovery()
        devices = discovery.list_devices()
        
        if args.json:
            print(json.dumps([asdict(d) for d in devices], indent=2))
        else:
            if not devices:
                print("No PicoKey devices found.")
            else:
                print(f"Found {len(devices)} device(s):")
                for d in devices:
                    vid_pid = f"{d.vendor_id:04x}:{d.product_id:04x}"
                    sn = d.serial_number or "N/A"
                    print(f" - [{d.product_name}] VID:PID={vid_pid} SN={sn}")
                    if d.atr:
                        print(f"   ATR: {d.atr}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
