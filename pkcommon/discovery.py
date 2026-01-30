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
    
    # Known PicoKey VID/PID combinations
    # VID 0x2e8a = Raspberry Pi (used by Pico-based devices)
    KNOWN_PICOKEY_DEVICES = {
        (0x2e8a, 0x10fe): "Pico Key",
        (0x2e8a, 0xcccc): "Pico HSM",
        (0x2e8a, 0xcafe): "Pico FIDO",
        # Add more VID/PID pairs as needed
    }
    
    @staticmethod
    def find_all_picokeys() -> List[PicoKeyDevice]:
        """Find all PicoKey devices by VID/PID or manufacturer string."""
        devices = []
        
        all_usb = usb.core.find(find_all=True, backend=_backend)
        if all_usb is None:
            return devices
        
        for dev in all_usb:
            vid_pid = (dev.idVendor, dev.idProduct)
            
            # Check if this is a known PicoKey device by VID/PID
            if vid_pid in USBDiscovery.KNOWN_PICOKEY_DEVICES:
                product_name = USBDiscovery.KNOWN_PICOKEY_DEVICES[vid_pid]
                manufacturer = "PicoKey"
                serial = None
                
                # Try to get actual strings from device
                try:
                    if dev.iManufacturer:
                        manufacturer = usb.util.get_string(dev, dev.iManufacturer) or manufacturer
                    if dev.iProduct:
                        product_name = usb.util.get_string(dev, dev.iProduct) or product_name
                    if dev.iSerialNumber:
                        serial = usb.util.get_string(dev, dev.iSerialNumber)
                except Exception:
                    pass  # Use defaults if access denied
                
                devices.append(PicoKeyDevice(
                    vendor_id=dev.idVendor,
                    product_id=dev.idProduct,
                    serial_number=serial,
                    product_name=product_name,
                    manufacturer=manufacturer
                ))
                continue
            
            # Fallback: check manufacturer string for "PicoKey"
            try:
                if dev.iManufacturer:
                    manufacturer = usb.util.get_string(dev, dev.iManufacturer)
                    if manufacturer and "PicoKey" in manufacturer:
                        product = usb.util.get_string(dev, dev.iProduct) if dev.iProduct else "Unknown"
                        serial = usb.util.get_string(dev, dev.iSerialNumber) if dev.iSerialNumber else None
                        
                        devices.append(PicoKeyDevice(
                            vendor_id=dev.idVendor,
                            product_id=dev.idProduct,
                            serial_number=serial,
                            product_name=product,
                            manufacturer=manufacturer
                        ))
            except Exception:
                continue
                
        return devices

