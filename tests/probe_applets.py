from pkcommon.apdu import APDUTransport
from smartcard.System import readers

# Common AIDs to probe
AIDS = {
    "Yubico OTP": [0xA0, 0x00, 0x00, 0x05, 0x27, 0x20, 0x01, 0x01],
    "OpenPGP": [0xD2, 0x76, 0x00, 0x01, 0x24, 0x01],
    "FIDO2": [0xA0, 0x00, 0x00, 0x06, 0x47, 0x2F, 0x00, 0x01],
    "PIV": [0xA0, 0x00, 0x00, 0x03, 0x08],
}

def probe():
    r_list = readers()
    if not r_list:
        print("No smartcard readers found.")
        return

    for reader in r_list:
        print(f"\n--- Probing Reader: {reader.name} ---")
        
        for name, aid in AIDS.items():
            transport = APDUTransport(reader.name)
            try:
                transport.connect()
                # Select Applet APDU: 00 A4 04 00 [Lc] [AID]
                apdu = [0x00, 0xA4, 0x04, 0x00, len(aid)] + aid
                data, sw1, sw2 = transport.transmit(apdu)
                
                if sw1 == 0x90 and sw2 == 0x00:
                    print(f"[+] FOUND: {name}")
                elif sw1 == 0x61: # More data available
                    print(f"[+] FOUND: {name} (SW=61{sw2:02x})")
                else:
                    print(f"[-] Missing: {name} (SW={sw1:02x}{sw2:02x})")
                transport.disconnect()
            except Exception as e:
                print(f"Error probing {name}: {e}")


if __name__ == "__main__":
    probe()
