# RC Car Frequency Scanner & Transmitter

A Python-based tool for Raspberry Pi to detect, analyze, and transmit RC car radio frequencies using Software Defined Radio (SDR) hardware.

## ⚠️ Legal Disclaimer

**READ THIS BEFORE USE:**

- This tool is for **educational and research purposes only**
- Transmitting on radio frequencies without proper authorization may be **illegal** in your jurisdiction
- Interfering with RC vehicles you don't own may violate laws regarding radio interference
- Always comply with local radio regulations (FCC in USA, Ofcom in UK, etc.)
- Use responsibly and ethically
- The authors assume no liability for misuse of this software

## 📋 Table of Contents

- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Frequency Bands](#frequency-bands)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Legal Considerations](#legal-considerations)
- [Contributing](#contributing)

## ✨ Features

- **Frequency Scanning**: Automatically scan common RC car frequency bands (27/40/49 MHz)
- **Signal Detection**: Identify active RC transmissions with power measurements
- **Signal Capture**: Record and save RF signals for analysis
- **Modulation Analysis**: Detect AM vs FM modulation schemes
- **Custom Frequency Scanning**: Scan any frequency range you specify
- **Signal Replay**: Framework for retransmitting captured signals (simulation mode)

## 🔧 Hardware Requirements

### For Receiving/Scanning (Required)
- **Raspberry Pi** (Any model: 3, 4, 5, or Zero 2 W recommended)
- **RTL-SDR Dongle** (~$25-40)
  - RTL2832U-based USB dongle
  - Recommended: RTL-SDR Blog V3 or NooElec NESDR Smart
  - Frequency range: 24 MHz - 1.7 GHz

### For Transmitting (Optional)
- **HackRF One** (~$300) - 1 MHz to 6 GHz TX/RX
- **LimeSDR Mini** (~$160) - 10 MHz to 3.5 GHz TX/RX
- **BladeRF** (~$420) - 300 MHz to 3.8 GHz TX/RX

### Antennas
- Telescopic antenna (usually included with RTL-SDR)
- For better results: Quarter-wave antenna tuned to your target frequency
  - 27 MHz: ~2.78m length
  - 49 MHz: ~1.53m length

## 💻 Software Requirements

- **Python 3.7+**
- **Operating System**: Raspberry Pi OS (Debian-based) or Ubuntu

## 📦 Installation

### 1. Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install System Dependencies
```bash
sudo apt install -y python3-pip git libusb-1.0-0-dev cmake build-essential
```

### 3. Install RTL-SDR Drivers
```bash
sudo apt install -y rtl-sdr librtlsdr-dev
```

### 4. Blacklist DVB-T Drivers (Prevents Conflicts)
```bash
echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/blacklist-rtl.conf
sudo rmmod dvb_usb_rtl28xxu  # Unload if currently loaded
```

### 5. Set USB Permissions
```bash
sudo usermod -a -G plugdev $USER
# Create udev rule
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", MODE="0666"' | sudo tee /etc/udev/rules.d/20-rtlsdr.rules
sudo udevadm control --reload-rules
```

### 6. Install Python Dependencies
```bash
pip3 install pyrtlsdr numpy scipy
```

### 7. Download the Script
```bash
git clone <your-repo-url>
cd rc-frequency-scanner
chmod +x rc_scanner.py
```

### 8. Test RTL-SDR
```bash
rtl_test -t
# Should show: "No errors" if working correctly
```

## 🚀 Usage

### Basic Usage
```bash
python3 rc_scanner.py
```

### Menu Options

1. **Scan 27 MHz band** - Most common toy-grade RC cars
2. **Scan 40 MHz band** - Older RC vehicles
3. **Scan 49 MHz band** - Alternative RC frequency
4. **Scan custom frequency range** - Specify your own range
5. **Capture signal at specific frequency** - Record a signal
6. **Exit** - Close the program

### Example Session

```
Select option (1-6): 1

Scanning from 26.995 MHz to 27.255 MHz...
✓ Signal detected at 27.145 MHz (Power: 45.3 dB)

Select option (1-6): 5
Frequency to capture (MHz): 27.145
Capture duration (seconds): 3

Capturing signal at 27.145 MHz for 3s...
Signal saved to rc_signal_27.145MHz_1699123456.json and .npy file
Modulation type: Likely AM (Amplitude Modulation)
```

## 📡 Frequency Bands

### Common RC Car Frequencies

| Band | Frequency Range | Common Use |
|------|----------------|------------|
| **27 MHz** | 26.995 - 27.255 MHz | Toy-grade RC cars, very common |
| **40 MHz** | 40.66 - 40.70 MHz | Older RC planes and cars |
| **49 MHz** | 49.82 - 49.90 MHz | Baby monitors, older RC vehicles |
| **75 MHz** | 75.41 - 75.99 MHz | RC aircraft (varies by region) |
| **2.4 GHz** | 2.400 - 2.483 GHz | Modern hobby-grade RC (requires different hardware) |

### Regional Differences
- **USA**: 27 MHz, 49 MHz, 72 MHz (aircraft), 75 MHz (surface)
- **Europe**: 27 MHz, 35 MHz, 40 MHz
- **Australia**: 27 MHz, 29 MHz, 36 MHz

## 🔬 How It Works

### Signal Detection
1. **SDR Tuning**: The RTL-SDR tunes to specific frequencies
2. **Sample Collection**: IQ samples are captured from the radio spectrum
3. **Power Analysis**: FFT (Fast Fourier Transform) calculates signal power
4. **Threshold Detection**: Signals exceeding noise floor are flagged

### Signal Capture
1. **Precise Tuning**: Centers on detected frequency
2. **Extended Recording**: Captures samples over specified duration
3. **Data Storage**: Saves both metadata (JSON) and raw samples (NumPy array)

### Modulation Analysis
- **AM Detection**: Analyzes amplitude variations
- **FM Detection**: Analyzes phase/frequency variations
- Compares variance to determine likely modulation type

### Transmission (Simulation)
- Currently simulated - requires TX-capable SDR
- Would use captured samples to reconstruct original signal
- Replay at same frequency with appropriate power levels

## 🐛 Troubleshooting

### "No devices found" Error
```bash
# Check if RTL-SDR is detected
lsusb | grep Realtek
# Should show: "Realtek Semiconductor Corp. RTL2838 DVB-T"

# Try with sudo
sudo python3 rc_scanner.py
```

### Permission Denied
```bash
# Add user to plugdev group
sudo usermod -a -G plugdev $USER
# Log out and back in, or reboot
```

### Poor Signal Reception
- Ensure antenna is properly connected
- Try different antenna orientations
- Move away from electronic noise sources
- Use an external antenna for better range
- Adjust the gain settings in code (try 40-50 instead of 'auto')

### Python Library Issues
```bash
# Reinstall dependencies
pip3 uninstall pyrtlsdr
pip3 install --no-cache-dir pyrtlsdr
```

### SDR Frequency Offset
RTL-SDR dongles can have frequency errors (PPM - Parts Per Million):
```python
# Add to scanner initialization
self.sdr.freq_correction = 60  # Adjust based on your dongle
```

## ⚖️ Legal Considerations

### United States (FCC)
- **Part 15**: Low-power devices under 27 MHz may be legal without license
- **Intentional interference**: Illegal under 47 USC § 333
- **Scanning/receiving**: Generally legal
- **Transmitting**: May require license depending on frequency and power

### European Union
- **RED Directive**: Regulates radio equipment
- **Short Range Devices**: 27 MHz typically allowed at low power
- Check national regulations as they vary by country

### General Rules
1. **Never interfere with emergency services**
2. **Don't disrupt other people's RC vehicles without permission**
3. **Respect privacy - don't intercept private communications**
4. **Follow local RF emission regulations**
5. **When in doubt, consult local radio authority**

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🔗 Resources

- [RTL-SDR Blog](https://www.rtl-sdr.com/)
- [FCC Frequency Allocations](https://www.fcc.gov/engineering-technology/policy-and-rules-division/general/radio-spectrum-allocation)
- [GNU Radio](https://www.gnuradio.org/) - Advanced SDR framework
- [SDR Sharp](https://airspy.com/download/) - Windows SDR software

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Remember: With great power comes great responsibility. Use this tool ethically and legally.**
