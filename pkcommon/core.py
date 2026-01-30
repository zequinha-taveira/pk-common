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
        """List all connected PicoKey devices."""
        from .discovery import USBDiscovery
        from .apdu import SmartcardDiscovery
        from .ctap import CTAPDiscovery
        
        devices = []
        devices.extend(USBDiscovery.find_all_picokeys())
        devices.extend(SmartcardDiscovery.find_all_picokeys())
        devices.extend(CTAPDiscovery.find_all_picokeys())
        
        return devices

    def _discover_hid(self) -> List[PicoKeyDevice]:
        """Discover devices using HID backend (FIDO/CTAP)."""
        # Implementation using pyusb or hidapi
        return []

    def _discover_scard(self) -> List[PicoKeyDevice]:
        """Discover devices using Smartcard backend (HSM/OpenPGP)."""
        # Implementation using pyscard
        return []
