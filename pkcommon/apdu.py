from smartcard.System import readers
from smartcard.util import toHexString, toBytes
from smartcard.Exceptions import NoCardException
from typing import List, Optional
from .core import PicoKeyDevice

class SmartcardDiscovery:
    """Discovery and communication using PC/SC Smartcard interface."""
    
    @staticmethod
    def find_all_picokeys() -> List[PicoKeyDevice]:
        devices = []
        try:
            from .discovery import USBDiscovery
            for reader in readers():
                # We filter by reader name which often contains the product name
                if any(s in reader.name for s in USBDiscovery.SUBSTRINGS):
                    atr = ""
                    try:
                        conn = reader.createConnection()
                        conn.connect()
                        from smartcard.util import toHexString
                        atr = toHexString(conn.getATR())
                        conn.disconnect()
                    except:
                        pass
                        
                    devices.append(PicoKeyDevice(
                        vendor_id=0,
                        product_id=0,
                        product_name=reader.name,
                        path=str(reader),
                        atr=atr
                    ))
        except Exception:
            pass
        return devices

class APDUTransport:
    """Handles sending and receiving APDUs."""
    
    def __init__(self, reader_name: str, verbose: bool = False):
        self.reader_name = reader_name
        self.connection = None
        self.verbose = verbose

    def connect(self):
        for reader in readers():
            if reader.name == self.reader_name:
                self.connection = reader.createConnection()
                self.connection.connect()
                return
        raise Exception(f"Reader {self.reader_name} not found")

    def disconnect(self):
        if self.connection:
            self.connection.disconnect()

    def transmit(self, apdu: List[int]) -> (List[int], int, int):
        """Send APDU and return (data, sw1, sw2)."""
        if not self.connection:
            self.connect()
        
        from smartcard.util import toHexString
        if self.verbose:
            print(f"  [APDU] > {toHexString(apdu)}")
            
        data, sw1, sw2 = self.connection.transmit(apdu)
        
        if self.verbose:
            print(f"  [APDU] < {toHexString(data)} SW={sw1:02x}{sw2:02x}")
            
        return data, sw1, sw2
