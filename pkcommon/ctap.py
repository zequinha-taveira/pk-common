from fido2.hid import CtapHidDevice
from fido2.ctap2 import Ctap2
from typing import List, Optional
from .core import PicoKeyDevice

class CTAPDiscovery:
    """Discovery for FIDO/CTAP devices."""
    
    @staticmethod
    def find_all_picokeys() -> List[PicoKeyDevice]:
        devices = []
        for dev in CtapHidDevice.list_devices():
            # Filter by PicoKey descriptor if available
            # For now, we take all CTAP HID devices that might be PicoKeys
            # A more robust check would involve the descriptor info.
            devices.append(PicoKeyDevice(
                vendor_id=dev.descriptor.vendor_id,
                product_id=dev.descriptor.product_id,
                serial_number=dev.descriptor.serial_number,
                product_name="PicoKey FIDO",
                path=dev.descriptor.path
            ))
        return devices

class CTAPModule:
    """Abstraction for CTAP2 functionality."""
    
    def __init__(self, device: CtapHidDevice):
        self.device = device
        self.ctap2 = Ctap2(device)

    def get_info(self):
        """Get CTAP2 Info."""
        return self.ctap2.get_info()

    def get_capabilities(self):
        """Get FIDO capabilities."""
        info = self.get_info()
        return {
            "rk": info.options.get("rk"),
            "up": info.options.get("up"),
            "uv": info.options.get("uv"),
            "plat": info.options.get("plat"),
            "versions": info.versions,
            "extensions": info.extensions
        }
