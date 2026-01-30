from .apdu import APDUTransport
from typing import List

class HSMModule:
    """Abstraction for Pico HSM functionality."""
    
    def __init__(self, transport: APDUTransport):
        self.transport = transport

    def get_info(self) -> List[int]:
        """Example: Get HSM info APDU (placeholder)."""
        # Command: CLA=0x80, INS=0x01, P1=0x00, P2=0x00
        apdu = [0x80, 0x01, 0x00, 0x00]
        data, sw1, sw2 = self.transport.transmit(apdu)
        return data

class OpenPGPModule:
    """Abstraction for Pico OpenPGP functionality."""
    
    def __init__(self, transport: APDUTransport):
        self.transport = transport

    def select_applet(self):
        """Select OpenPGP applet."""
        # AID for OpenPGP: D2 76 00 01 24 01
        apdu = [0x00, 0xA4, 0x04, 0x00, 0x06, 0xD2, 0x76, 0x00, 0x01, 0x24, 0x01]
        data, sw1, sw2 = self.transport.transmit(apdu)
        return sw1 == 0x90 and sw2 == 0x00
