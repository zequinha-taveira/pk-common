from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PicoKeyDevice:
    """Represents a discovered PicoKey device."""
    vendor_id: int
    product_id: int
    serial_number: Optional[str] = None
    product_name: Optional[str] = None
    firmware_version: Optional[str] = None
    manufacturer: Optional[str] = None
    path: Optional[str] = None

    def __repr__(self) -> str:
        return f"PicoKeyDevice(name='{self.product_name}', sn='{self.serial_number}', fw='{self.firmware_version}')"

class PicoKeyDiscovery:
    """Handles discovery of PicoKey devices across different backends."""
    
    # Official PicoKey Vendor ID (Example: 0x20a0 for Nitrokey/OpenPGP-like, or custom)
    # We should define a list of known VIDs/PIDs or use a registry.
    PICOKEY_VIDS = [0x20a0, 0x1d50, 0x10c4] # placeholder VIDs for now

    def __init__(self):
        pass

    def list_devices(self) -> List[PicoKeyDevice]:
        """List and merge all connected PicoKey devices."""
        from .discovery import USBDiscovery
        from .apdu import SmartcardDiscovery
        from .ctap import CTAPDiscovery
        
        raw_usb = USBDiscovery.find_all_picokeys()
        raw_sc = SmartcardDiscovery.find_all_picokeys()
        raw_ctap = CTAPDiscovery.find_all_picokeys()
        
        merged = {}
        
        # Start with USB devices as the base (reliable VID/PID)
        for dev in raw_usb:
            key = (dev.vendor_id, dev.product_id, dev.serial_number)
            merged[key] = dev
            
        # Merge Smartcard info
        for sc_dev in raw_sc:
            # Try to find a matching USB device
            match_found = False
            for key, usb_dev in merged.items():
                if usb_dev.product_name and "Pico" in sc_dev.product_name:
                    # In a real tool, we might check reader indices vs USB ports
                    # For now, if we have one USB Pico and one SC Pico, they are likely the same
                    usb_dev.path = sc_dev.path # Store the reader path
                    match_found = True
                    break
            
            if not match_found:
                key = (0, 0, sc_dev.product_name)
                merged[key] = sc_dev

        return list(merged.values())


    def _discover_hid(self) -> List[PicoKeyDevice]:
        """Discover devices using HID backend (FIDO/CTAP)."""
        # Implementation using pyusb or hidapi
        return []

    def _discover_scard(self) -> List[PicoKeyDevice]:
        """Discover devices using Smartcard backend (HSM/OpenPGP)."""
        # Implementation using pyscard
        return []
