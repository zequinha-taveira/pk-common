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
    
    AID_PGP = [0xD2, 0x76, 0x00, 0x01, 0x24, 0x01]
    
    def __init__(self, transport: APDUTransport):
        self.transport = transport

    def select(self):
        """Select OpenPGP applet."""
        apdu = [0x00, 0xA4, 0x04, 0x00, len(self.AID_PGP)] + self.AID_PGP
        data, sw1, sw2 = self.transport.transmit(apdu)
        return sw1 == 0x90 and sw2 == 0x00

class YubicoModule:
    """Abstraction for Yubico-compatible functionality (OTP)."""
    
    AID_OTP = [0xA0, 0x00, 0x00, 0x05, 0x27, 0x20, 0x01, 0x01]
    
    def __init__(self, transport: APDUTransport):
        self.transport = transport

    def select(self):
        """Select Yubico OTP applet."""
        apdu = [0x00, 0xA4, 0x04, 0x00, len(self.AID_OTP)] + self.AID_OTP
        data, sw1, sw2 = self.transport.transmit(apdu)
        return sw1 == 0x90 and sw2 == 0x00

class ManagementModule:
    """Abstraction for Yubico Management functionality."""
    
    AID_MGMT = [0xA0, 0x00, 0x00, 0x05, 0x27, 0x47, 0x11, 0x17]
    
    def __init__(self, transport: APDUTransport):
        self.transport = transport

    def select(self):
        """Select Management applet."""
        apdu = [0x00, 0xA4, 0x04, 0x00, len(self.AID_MGMT)] + self.AID_MGMT
        data, sw1, sw2 = self.transport.transmit(apdu)
        if sw1 == 0x90:
            return "".join(chr(c) for c in data)
        return None

class OATHModule:
    """Abstraction for OATH (TOTP/HOTP) functionality."""
    
    AID_OATH = [0xA0, 0x00, 0x00, 0x05, 0x27, 0x21, 0x01]
    
    def __init__(self, transport: APDUTransport):
        self.transport = transport

    def select(self):
        """Select OATH applet."""
        apdu = [0x00, 0xA4, 0x04, 0x00, len(self.AID_OATH)] + self.AID_OATH
        data, sw1, sw2 = self.transport.transmit(apdu)
        return sw1 == 0x90 and sw2 == 0x00

    def list_accounts(self):
        """List OATH accounts."""
        # INS 0xA1: List
        apdu = [0x00, 0xA1, 0x00, 0x00]
        data, sw1, sw2 = self.transport.transmit(apdu)
        if sw1 == 0x90:
            return data
        return []




