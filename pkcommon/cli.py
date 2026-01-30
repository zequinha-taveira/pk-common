import argparse
import json
import sys
from dataclasses import asdict
from pkcommon.core import PicoKeyDiscovery

def main():
    parser = argparse.ArgumentParser(description="PicoKey SDK CLI Tool")
    parser.add_argument("--list", action="store_true", help="List all connected PicoKey devices")
    parser.add_argument("--inspect", action="store_true", help="Deeply inspect connected devices and applets")
    parser.add_argument("--shell", action="store_true", help="Enter interactive APDU shell")
    parser.add_argument("--verbose", action="store_true", help="Show raw APDU communication")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    args = parser.parse_args()
    
    if args.shell:
        discovery = PicoKeyDiscovery()
        devices = [d for d in discovery.list_devices() if d.path or d.atr]
        if not devices:
            print("No smartcard-capable devices found.")
            return
        
        dev = devices[0]
        print(f"Entering shell for: {dev.product_name}")
        from pkcommon.apdu import APDUTransport
        transport = APDUTransport(dev.path if dev.path else dev.product_name, verbose=True)
        try:
            transport.connect()
            print("Type hex APDU (e.g., '00A4040008A000000527471117') or 'exit'.")
            while True:
                line = input("apdu> ").strip().replace(" ", "")
                if line.lower() in ["exit", "quit"]:
                    break
                if not line:
                    continue
                try:
                    apdu = [int(line[i:i+2], 16) for i in range(0, len(line), 2)]
                    transport.transmit(apdu)
                except ValueError:
                    print("Error: Invalid hex string.")
                except Exception as e:
                    print(f"Error: {e}")
            transport.disconnect()
        except Exception as e:
            print(f"Connection failed: {e}")
        return

    if args.list or args.inspect:

        discovery = PicoKeyDiscovery()
        devices = discovery.list_devices()
        
        if args.json:
            json_output = []
            from pkcommon.apdu import APDUTransport # Moved here for scope
            from pkcommon.modules import ManagementModule, YubicoModule, OATHModule, OpenPGPModule # Moved here for scope
            for d in devices:
                output = asdict(d)
                if args.inspect and (d.atr or (d.path and "CCID" in d.path)):
                    transport = APDUTransport(d.path if d.path else d.product_name, verbose=args.verbose)
                    try:
                        transport.connect()
                        output["applets"] = {
                            "management": ManagementModule(transport).select(),
                            "otp": YubicoModule(transport).select(),
                            "oath": OATHModule(transport).select(),
                            "openpgp": OpenPGPModule(transport).select(),
                        }
                        transport.disconnect()
                    except Exception: # Catch specific exceptions if possible, or log them
                        output["applets"] = None # Indicate inspection failed for applets
                json_output.append(output)
            print(json.dumps(json_output, indent=2))
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
                        
                        import time
                        transport = APDUTransport(d.path if d.path else d.product_name, verbose=args.verbose)
                        try:
                            transport.connect()
                            
                            def benchmark_select(mod):
                                start = time.time()
                                res = mod.select()
                                end = time.time()
                                return res, (end - start) * 1000

                            # Check Management
                            mgmt = ManagementModule(transport)
                            ver, t = benchmark_select(mgmt)
                            if ver:
                                print(f"   [+] Management: Version {ver} ({t:.1f}ms)")
                            
                            # Check OTP
                            otp = YubicoModule(transport)
                            ok, t = benchmark_select(otp)
                            if ok:
                                print(f"   [+] OTP: Present ({t:.1f}ms)")
                                
                            # Check OATH
                            oath = OATHModule(transport)
                            ok, t = benchmark_select(oath)
                            if ok:
                                accounts = oath.list_accounts()
                                acc_str = f" ({len(accounts)} accounts)" if accounts else ""
                                print(f"   [+] OATH: Present ({t:.1f}ms){acc_str}")
                                for acc in accounts:
                                    print(f"       - {acc}")
                                
                            # Check OpenPGP
                            pgp = OpenPGPModule(transport)
                            ok, t = benchmark_select(pgp)
                            if ok:
                                print(f"   [+] OpenPGP: Present ({t:.1f}ms)")

                                
                            transport.disconnect()
                        except Exception as e:
                            print(f"   [!] Inspection failed: {e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
