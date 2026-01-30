import argparse
import json
import sys
from dataclasses import asdict
from pkcommon.core import PicoKeyDiscovery

def main():
    parser = argparse.ArgumentParser(description="PicoKey SDK CLI Tool")
    parser.add_argument("--list", action="store_true", help="List all connected PicoKey devices")
    parser.add_argument("--inspect", action="store_true", help="Deeply inspect connected devices and applets")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    args = parser.parse_args()
    
    if args.list or args.inspect:
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
                    
                    if args.inspect and (d.atr or (d.path and "CCID" in d.path)):
                        from pkcommon.apdu import APDUTransport
                        from pkcommon.modules import ManagementModule, YubicoModule, OATHModule, OpenPGPModule
                        
                        transport = APDUTransport(d.path if d.path else d.product_name)
                        try:
                            transport.connect()
                            
                            # Check Management
                            mgmt = ManagementModule(transport)
                            ver = mgmt.select()
                            if ver:
                                print(f"   [+] Management: Version {ver}")
                            
                            # Check OTP
                            otp = YubicoModule(transport)
                            if otp.select():
                                print(f"   [+] OTP: Present")
                                
                            # Check OATH
                            oath = OATHModule(transport)
                            if oath.select():
                                print(f"   [+] OATH: Present")
                                
                            # Check OpenPGP
                            pgp = OpenPGPModule(transport)
                            if pgp.select():
                                print(f"   [+] OpenPGP: Present")
                                
                            transport.disconnect()
                        except Exception as e:
                            print(f"   [!] Inspection failed: {e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
