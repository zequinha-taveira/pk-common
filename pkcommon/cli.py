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
    parser.add_argument("--monitor", action="store_true", help="Monitor for device connections/disconnections")
    parser.add_argument("--oath-add", nargs=2, metavar=("LABEL", "SECRET"), help="Add OATH TOTP account")
    parser.add_argument("--oath-delete", metavar="LABEL", help="Delete OATH account")
    parser.add_argument("--oath-list", action="store_true", help="List OATH account labels")
    parser.add_argument("--oath-reset", action="store_true", help="Factory reset OATH applet (destroys all data)")
    parser.add_argument("--fido-info", action="store_true", help="Show FIDO2/CTAP2 device information")
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

    if args.monitor:
        import time
        discovery = PicoKeyDiscovery()
        last_devs = {}
        print("Monitoring for PicoKey devices... (Press Ctrl+C to stop)")
        try:
            while True:
                devs = discovery.list_devices()
                current_keys = { (d.vendor_id, d.product_id, d.serial_number): d.product_name for d in devs }
                
                new_keys = set(current_keys.keys()) - set(last_devs.keys())
                removed_keys = set(last_devs.keys()) - set(current_keys.keys())
                
                for k in new_keys:
                    print(f"[+] Connected: {current_keys[k]} (VID:PID={k[0]:04x}:{k[1]:04x} SN={k[2] or 'N/A'})")
                for k in removed_keys:
                    print(f"[-] Disconnected: {last_devs[k]} (VID:PID={k[0]:04x}:{k[1]:04x} SN={k[2] or 'N/A'})")
                
                last_devs = current_keys
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
        return

    if args.oath_add or args.oath_delete or args.oath_list or args.oath_reset:
        discovery = PicoKeyDiscovery()
        devices = [d for d in discovery.list_devices() if d.path or d.atr]
        if not devices:
            print("No smartcard-capable devices found.")
            return
        
        dev = devices[0]
        from pkcommon.apdu import APDUTransport
        from pkcommon.modules import OATHModule
        transport = APDUTransport(dev.path if dev.path else dev.product_name, verbose=args.verbose)
        try:
            transport.connect()
            oath = OATHModule(transport)
            if not oath.select():
                print("Failed to select OATH applet.")
                return
            
            if args.oath_list:
                accounts = oath.list_accounts()
                print(f"OATH Accounts ({len(accounts)}):")
                for acc in accounts:
                    print(f" - {acc}")

            if args.oath_add:
                label, secret = args.oath_add
                if oath.put_account(label, secret):
                    print(f"Successfully added account: {label}")
                else:
                    print(f"Failed to add account: {label}")
            
            if args.oath_delete:
                label = args.oath_delete
                if oath.delete_account(label):
                    print(f"Successfully deleted account: {label}")
                else:
                    print(f"Failed to delete account: {label}")

            if args.oath_reset:
                confirm = input("Are you sure you want to reset the OATH applet? All accounts will be lost! [y/N]: ")
                if confirm.lower() == 'y':
                    if oath.reset():
                        print("Successfully reset OATH applet.")
                    else:
                        print("Failed to reset OATH applet.")
                    
            transport.disconnect()
        except Exception as e:
            print(f"OATH Operation failed: {e}")
        return

    if args.fido_info:
        from pkcommon.ctap import CTAPDiscovery, CTAPModule
        devices = CTAPDiscovery.find_all_picokeys()
        if not devices:
            print("No PicoKey FIDO devices found.")
            return
        
        # We need the actual CtapHidDevice for CTAPModule
        from fido2.hid import CtapHidDevice
        hid_devs = list(CtapHidDevice.list_devices())
        if not hid_devs:
            print("No HID devices accessible.")
            return
            
        print(f"FIDO2/CTAP2 Information for {len(hid_devs)} device(s):")
        for dev in hid_devs:
            try:
                mod = CTAPModule(dev)
                caps = mod.get_capabilities()
                print(f" - Device: {dev.descriptor.product_name} ({dev.descriptor.path})")
                print(f"   Versions: {', '.join(caps['versions'])}")
                print(f"   Extensions: {', '.join(caps['extensions'])}")
                print(f"   Options: rk={caps['rk']}, up={caps['up']}, uv={caps['uv']}, plat={caps['plat']}")
            except Exception as e:
                print(f"   [!] Failed to get info: {e}")
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
                        from pkcommon.modules import ManagementModule, YubicoModule, OATHModule, OpenPGPModule, FIDOModule
                        
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
                                codes = oath.calculate_all()
                                acc_str = f" ({len(codes)} accounts)" if codes else ""
                                print(f"   [+] OATH: Present ({t:.1f}ms){acc_str}")
                                for acc, code in codes.items():
                                    print(f"       - {acc}: {code}")

                                
                            # Check FIDO2 (APDU)
                            fido = FIDOModule(transport)
                            try:
                                ok, t = benchmark_select(fido)
                                if ok:
                                    print(f"   [+] FIDO2 (SC): Present ({t:.1f}ms)")
                            except Exception as e:
                                if "Acesso negado" in str(e):
                                    print(f"   [!] FIDO2 (SC): Active but blocked by OS")
                                
                            # Check OpenPGP
                            pgp = OpenPGPModule(transport)
                            ok, t = benchmark_select(pgp)
                            if ok:
                                print(f"   [+] OpenPGP: Present ({t:.1f}ms)")

                                
                            transport.disconnect()
                        except Exception as e:
                            print(f"   [!] Inspection failed: {e}")
                    
                    if d.has_vendor_interface:
                        print(f"   [*] Vendor Interface: Detected (Class 255)")

                    # Check for FIDO HID info if it's a FIDO-capable device
                    from fido2.hid import CtapHidDevice
                    for hid_dev in CtapHidDevice.list_devices():
                        if hid_dev.descriptor.vendor_id == d.vendor_id and hid_dev.descriptor.product_id == d.product_id:
                            try:
                                from pkcommon.ctap import CTAPModule
                                mod = CTAPModule(hid_dev)
                                caps = mod.get_capabilities()
                                print(f"   [+] FIDO2 (HID): Protocol {', '.join(caps['versions'])}")
                                print(f"       Options: rk={caps['rk']}, up={caps['up']}, uv={caps['uv']}, plat={caps['plat']}")
                                break # Found the matching HID side
                            except:
                                pass


    else:
        parser.print_help()


if __name__ == "__main__":
    main()
