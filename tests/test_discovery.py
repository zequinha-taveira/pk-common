from pkcommon.core import PicoKeyDiscovery

def main():
    print("Searching for PicoKey devices...")
    discovery = PicoKeyDiscovery()
    devices = discovery.list_devices()
    
    if not devices:
        print("No PicoKey devices found.")
    else:
        print(f"Found {len(devices)} device(s):")
        for dev in devices:
            print(f" - {dev}")

if __name__ == "__main__":
    main()
