# pk-common

Open-source, neutral, and stable API for PicoKey devices (HSM, FIDO, OpenPGP).

## Overview

The PicoKey SDK provides low-level, vendor-neutral infrastructure for interacting with PicoKey devices. It is designed for developers and community tools, focusing on technical transparency and stability.

## Features

- **Device Discovery**: Detect and identify PicoKey devices.
- **Low-level Communication**: Send/receive APDUs for HSM and OpenPGP.
- **FIDO2/CTAP Support**: Interact with FIDO capabilities.
- **Vendor Neutral**: Independence from proprietary backends.

## Installation

```bash
pip install pk-common
```

## Quick Start

### Library Usage
```python
from pkcommon import PicoKeyDiscovery

discovery = PicoKeyDiscovery()
devices = discovery.list_devices()

for device in devices:
    print(f"Device: {device.product_name}")
    print(f"ATR: {device.atr}")
```

### CLI Usage
- **List devices**: `python -m pkcommon.cli --list`
- **Deep Inspection**: `python -m pkcommon.cli --inspect`
- **APDU Shell**: `python -m pkcommon.cli --shell`
- **Device Monitor**: `python -m pkcommon.cli --monitor`
- **OATH Gestão**:
  - Listar: `python -m pkcommon.cli --oath-list`
  - Adicionar: `python -m pkcommon.cli --oath-add "Label" "SECRET"`
  - Deletar: `python -m pkcommon.cli --oath-delete "Label"`
  - Reset: `python -m pkcommon.cli --oath-reset`
- **FIDO2 Info**: `python -m pkcommon.cli --fido-info`
- **JSON Output**: `python -m pkcommon.cli --inspect --json`
- **Verbose Mode**: `python -m pkcommon.cli --inspect --verbose`



## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
