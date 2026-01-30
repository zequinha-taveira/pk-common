import usb.core
import usb.util
import usb.backend.libusb1
from typing import List
from .core import PicoKeyDevice

# Try to use bundled libusb DLL for the backend on Windows
_backend = None
try:
    import libusb as _libusb_pkg
    # Get the path to the bundled libusb DLL
    _dll_path = str(_libusb_pkg.dll._name)
    _backend = usb.backend.libusb1.get_backend(find_library=lambda x: _dll_path)
except (ImportError, AttributeError):
    # Fallback: try libusb_package
    try:
        import libusb_package
        _backend = usb.backend.libusb1.get_backend(find_library=libusb_package.find_library)
    except ImportError:
        pass

class USBDiscovery:
    """Low-level USB discovery using pyusb."""
    
    @staticmethod
    def find_all_picokeys() -> List[PicoKeyDevice]:
        # This is a generic implementation. PicoKey might use specific VIDs/PIDs.
        # For now, let's look for known patterns or descriptive strings.
        devices = []
        
        # We can iterate over all devices and filter by manufacturer/product name
        # if the VIDs are shared or unknown.
        all_usb = usb.core.find(find_all=True, backend=_backend)
        
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
