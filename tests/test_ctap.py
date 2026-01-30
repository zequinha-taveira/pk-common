from fido2.hid import CtapHidDevice
from pkcommon.ctap import CTAPModule
from pkcommon.core import PicoKeyDiscovery

def main():
    discovery = PicoKeyDiscovery()
    devices = discovery.list_devices()
    
    # Filter for FIDO devices (normally via path or product name)
    fido_devices = [d for d in devices if "FIDO" in d.product_name]
    
    if not fido_devices:
        print("No PicoKey FIDO devices found.")
        return

    # In practice, find the actual CtapHidDevice from the path
    # Here we just show the logic
    for dev_info in fido_devices:
        print(f"Found FIDO device at {dev_info.path}")
        # For a real test, we'd need to map back PicoKeyDevice.path to CtapHidDevice.list_devices()
        # For brevity, this example assumes we have a way to get the CTAP device.
        
    print("CTAP Module initialized (simulation).")

if __name__ == "__main__":
    main()
