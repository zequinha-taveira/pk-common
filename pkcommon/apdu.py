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
            for reader in readers():
                # We filter by reader name which often contains the product name
                if "PicoKey" in reader.name or "Pico Key" in reader.name:
                    devices.append(PicoKeyDevice(
                        vendor_id=0, # Not directly accessible via PC/SC easily
                        product_id=0,
                        product_name=reader.name,
                        path=str(reader)
                    ))
        except Exception:
            pass
        return devices

class APDUTransport:
    """Handles sending and receiving APDUs."""
    
    def __init__(self, reader_name: str):
        self.reader_name = reader_name
        self.connection = None

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
        
        data, sw1, sw2 = self.connection.transmit(apdu)
        return data, sw1, sw2
