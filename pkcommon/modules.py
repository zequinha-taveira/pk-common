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

    def calculate_totp(self, label: str, timestamp: int = None):
        """Calculate TOTP code for a given account label."""
        import time
        if timestamp is None:
            timestamp = int(time.time() // 30)
            
        challenge = timestamp.to_bytes(8, "big")
        label_bytes = label.encode()
        
        # Tag 0x71: Label, Tag 0x74: Challenge
        data = [0x71, len(label_bytes)] + list(label_bytes) + [0x74, 8] + list(challenge)
        # INS 0xA2: Calculate
        apdu = [0x00, 0xA2, 0x00, 0x01, len(data)] + data
        resp, sw1, sw2 = self.transport.transmit(apdu)
        
        if sw1 == 0x90 and len(resp) >= 2:
            # Response Tag 0x76: Code
            if resp[0] == 0x76:
                digits = resp[1] - 1 # First byte of value is digits
                code_data = resp[2 : 2+digits]
                # Actually YubiKey returns truncated int
                val = int.from_bytes(resp[2:], "big") & 0x7FFFFFFF
                return f"{val % (10**6):06d}"
        return None

    def calculate_all(self, timestamp: int = None):
        """Calculate codes for all accounts."""
        import time
        if timestamp is None:
            timestamp = int(time.time() // 30)
        challenge = timestamp.to_bytes(8, "big")
        data = [0x74, 8] + list(challenge)
        # INS 0xA4: Calculate All
        apdu = [0x00, 0xA4, 0x00, 0x01, len(data)] + data
        resp, sw1, sw2 = self.transport.transmit(apdu)
        
        results = {}
        if sw1 == 0x90:
            # Returns sequence of (0x71 label, 0x76 code)
            i = 0
            current_label = None
            while i < len(resp):
                tag = resp[i]
                length = resp[i+1]
                value = resp[i+2 : i+2+length]
                if tag == 0x71:
                    current_label = "".join(chr(c) for c in value)
                elif tag == 0x76:
                    val = int.from_bytes(value[1:], "big") & 0x7FFFFFFF
                    code = f"{val % (10**6):06d}"
                    if current_label:
                        results[current_label] = code
                i += 2 + length
        return results

    def put_account(self, label: str, secret_b32: str, alg: int = 0x01, digits: int = 6):
        """Add an OATH account. secret_b32 is the Base32 encoded secret."""
        import base64
        # Clean secret and add padding if missing
        secret_b32 = secret_b32.strip().upper().replace(" ", "")
        secret_b32 += "=" * ((8 - len(secret_b32) % 8) % 8)
        try:
            secret = base64.b32decode(secret_b32)
        except Exception as e:
            raise ValueError(f"Invalid Base32 secret: {e}")
            
        label_bytes = label.encode()
        # Tags: 0x71 (Label), 0x73 (Secret), 0x74 (Type), 0x75 (Algorithm)
        data = [0x71, len(label_bytes)] + list(label_bytes)
        data += [0x74, 1, 0x20 | digits]
        data += [0x75, 1, alg]
        data += [0x73, len(secret)] + list(secret)
        
        # INS 0x01: Put
        apdu = [0x00, 0x01, 0x00, 0x00, len(data)] + data
        resp, sw1, sw2 = self.transport.transmit(apdu)
        return sw1 == 0x90

    def delete_account(self, label: str):
        """Delete an OATH account."""
        label_bytes = label.encode()
        data = [0x71, len(label_bytes)] + list(label_bytes)
        # INS 0x02: Delete
        apdu = [0x00, 0x02, 0x00, 0x00, len(data)] + data
        resp, sw1, sw2 = self.transport.transmit(apdu)
        return sw1 == 0x90

    def reset(self):
        """Factory reset OATH applet (destroys all accounts)."""
        # INS 0x05: Reset
        apdu = [0x00, 0x05, 0xDE, 0xAD] # Standard Yubico OATH reset parameters
        resp, sw1, sw2 = self.transport.transmit(apdu)
        return sw1 == 0x90



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






