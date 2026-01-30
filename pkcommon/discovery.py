import usb.core
import usb.util
from typing import List
from .core import PicoKeyDevice

class USBDiscovery:
    """Low-level USB discovery using pyusb."""
    
    @staticmethod
    def find_all_picokeys() -> List[PicoKeyDevice]:
        # This is a generic implementation. PicoKey might use specific VIDs/PIDs.
        # For now, let's look for known patterns or descriptive strings.
        devices = []
        
        # We can iterate over all devices and filter by manufacturer/product name
        # if the VIDs are shared or unknown.
        all_usb = usb.core.find(find_all=True)
        
        for dev in all_usb:
            try:
                manufacturer = usb.util.get_string(dev, dev.iManufacturer)
                product = usb.util.get_string(dev, dev.iProduct)
                serial = usb.util.get_string(dev, dev.iSerialNumber)
                
                if manufacturer and "PicoKey" in manufacturer:
                    devices.append(PicoKeyDevice(
                        vendor_id=dev.idVendor,
                        product_id=dev.idProduct,
                        serial_number=serial,
                        product_name=product,
                        manufacturer=manufacturer
                    ))
            except Exception:
                # Some devices might be permission-restricted
                continue
                
        return devices
