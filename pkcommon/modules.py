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
        """List OATH accounts and return labels."""
        # INS 0xA1: List
        apdu = [0x00, 0xA1, 0x00, 0x00]
        data, sw1, sw2 = self.transport.transmit(apdu)
        
        accounts = []
        if sw1 == 0x90:
            i = 0
            while i < len(data):
                tag = data[i]
                length = data[i+1]
                value = data[i+2 : i+2+length]
                
                if tag == 0x71: # Name/Label
                    label = "".join(chr(c) for c in value)
                    accounts.append(label)
                    
                i += 2 + length
        return accounts

class FIDOModule:
    """Abstraction for FIDO (U2F/FIDO2) functionality via APDU."""
    
    AID_FIDO = [0xA0, 0x00, 0x00, 0x06, 0x47, 0x2F, 0x00, 0x01]
    
    def __init__(self, transport: APDUTransport):
        self.transport = transport

    def select(self):
        """Select FIDO applet."""
        apdu = [0x00, 0xA4, 0x04, 0x00, len(self.AID_FIDO)] + self.AID_FIDO
        data, sw1, sw2 = self.transport.transmit(apdu)
        return sw1 == 0x90 and sw2 == 0x00

class RescueModule:
    """Abstraction for Vendor/Rescue interface functionality."""
    
    def __init__(self, transport):
        self.transport = transport # VendorTransport

    def ping(self):
        """Send a ping to the rescue interface."""
        try:
            # Pol Henarejos firmware often uses 0x00 or something similar
            # This is experimental.
            self.transport.send([0x00])
            return True
        except:
            return False






