import sys
from pkcommon.core import PicoKeyDiscovery
from pkcommon.apdu import APDUTransport
from pkcommon.modules import HSMModule, OpenPGPModule

def main():
    discovery = PicoKeyDiscovery()
    devices = discovery.list_devices()
    
    smartcard_devices = [d for d in devices if d.path.startswith("Reader") or "Reader" in d.product_name]
    
    if not smartcard_devices:
        print("No PicoKey Smartcard readers found.")
        return

    reader = smartcard_devices[0]
    print(f"Connecting to {reader.product_name}...")
    
    transport = APDUTransport(reader.product_name)
    try:
        hsm = HSMModule(transport)
        pgp = OpenPGPModule(transport)
        
        print("Attempting to select OpenPGP applet...")
        if pgp.select_applet():
            print("Successfully selected OpenPGP applet.")
        else:
            print("Failed to select OpenPGP applet.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        transport.disconnect()

if __name__ == "__main__":
    main()
