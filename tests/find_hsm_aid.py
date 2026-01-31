from pkcommon.apdu import APDUTransport
from smartcard.System import readers
from smartcard.util import toHexString

def probe():
    r_list = readers()
    if not r_list:
        print("No readers found.")
        return
        
    reader = r_list[0]
    transport = APDUTransport(reader.name, verbose=False)
    
    print(f"--- Probing for Hidden Applets on {reader.name} ---")
    
    try:
        transport.connect()
        # 1. Try to select EF.DIR (0x2F00) to find registered AIDs
        print("[*] Attempting to select EF.DIR (2F 00)...")
        data, sw1, sw2 = transport.transmit([0x00, 0xA4, 0x00, 0x00, 0x02, 0x2F, 0x00])
        if sw1 == 0x90:
            print("[+] EF.DIR found! Reading contents...")
            # Read Binary
            data, sw1, sw2 = transport.transmit([0x00, 0xB0, 0x00, 0x00, 0x00])
            print(f"    Data: {toHexString(data)}")
        else:
            print(f"[-] EF.DIR not found (SW={sw1:02x}{sw2:02x})")
            
        # 2. Try common AID prefixes and known HSM variations
        CANDIDATES = {
            "PIV (Standard)": [0xA0, 0x00, 0x00, 0x03, 0x08],
            "OpenPGP (Standard)": [0xD2, 0x76, 0x00, 0x01, 0x24, 0x01],
            "Pico HSM (Candidate 1)": [0xD2, 0x76, 0x00, 0x01, 0x24, 0x01, 0x02],
            "Pico HSM (Candidate 3)": [0xD2, 0x76, 0x00, 0x01, 0x24, 0x01, 0x03],
            "Pico HSM (Variant)": [0xD2, 0x76, 0x00, 0x01, 0x68, 0x53, 0x4D],
            "NDEF (NFC)": [0xD2, 0x76, 0x00, 0x00, 0x85, 0x01, 0x01],
            "HSM (NIST)": [0xA0, 0x00, 0x00, 0x03, 0x08, 0x00, 0x00, 0x10, 0x00, 0x01, 0x00],
            "Pico Custom RID": [0xD0, 0x70, 0x49, 0x43, 0x4F, 0x4B, 0x45, 0x59],
        }
        
        for name, aid in CANDIDATES.items():
            apdu = [0x00, 0xA4, 0x04, 0x00, len(aid)] + aid
            try:
                data, sw1, sw2 = transport.transmit(apdu)
                if sw1 == 0x90 or sw1 == 0x61:
                    print(f"[+] Found potential match: {name} (AID={toHexString(aid)})")
                elif sw1 == 0x6a and sw2 == 0x82:
                    pass
                else:
                    print(f"[?] Interesting result for {name}: SW={sw1:02x}{sw2:02x}")
            except:
                pass
                
        transport.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe()
