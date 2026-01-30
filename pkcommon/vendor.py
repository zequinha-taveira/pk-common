import usb.core
import usb.util
from typing import List, Optional

class VendorTransport:
    """Handles raw communication with the PicoKey Vendor interface (Class 255)."""
    
    def __init__(self, vendor_id: int, product_id: int, backend=None):
        self.vid = vendor_id
        self.pid = product_id
        self.backend = backend
        self.device = None
        self.ep_out = None
        self.ep_in = None

    def connect(self):
        self.device = usb.core.find(idVendor=self.vid, idProduct=self.pid, backend=self.backend)
        if not self.device:
            raise Exception("Device not found")
            
        # Find vendor interface (Class 255)
        cfg = self.device.get_active_configuration()
        intf = None
        for i in cfg:
            if i.bInterfaceClass == 255:
                intf = i
                break
        
        if not intf:
            raise Exception("Vendor interface not found")

        # Detach kernel driver if necessary (mostly non-windows, but good practice)
        try:
            if self.device.is_kernel_driver_active(intf.bInterfaceNumber):
                self.device.detach_kernel_driver(intf.bInterfaceNumber)
        except:
            pass

        # Find endpoints
        for ep in intf:
            if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                self.ep_out = ep
            else:
                self.ep_in = ep

    def send(self, data: List[int]):
        if not self.ep_out:
            self.connect()
        self.ep_out.write(data)

    def receive(self, length: int = 64, timeout: int = 1000) -> List[int]:
        if not self.ep_in:
            self.connect()
        return self.ep_in.read(length, timeout)

    def exchange(self, data: List[int], response_len: int = 64) -> List[int]:
        self.send(data)
        return self.receive(response_len)
