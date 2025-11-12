#!/usr/bin/env python3
"""
RC Car Frequency Scanner and Transmitter for Raspberry Pi
Requires: RTL-SDR dongle (for receiving) and HackRF/LimeSDR (for transmitting)
Install: pip install pyrtlsdr numpy scipy
"""

import numpy as np
from rtlsdr import RtlSdr
import time
import json
from datetime import datetime

# Common RC car frequency bands (in Hz)
RC_FREQUENCY_BANDS = {
    '27MHz': (26.995e6, 27.255e6),  # 27 MHz band
    '40MHz': (40.66e6, 40.70e6),     # 40 MHz band  
    '49MHz': (49.82e6, 49.90e6),     # 49 MHz band
    '2.4GHz': (2.400e9, 2.483e9)     # 2.4 GHz band (requires different hardware)
}

class RCFrequencyScanner:
    def __init__(self, center_freq=27.145e6, sample_rate=2.4e6):
        """Initialize the SDR scanner"""
        self.sdr = RtlSdr()
        self.sdr.sample_rate = sample_rate
        self.sdr.center_freq = center_freq
        self.sdr.gain = 'auto'
        self.detected_signals = []
        
    def scan_frequency_range(self, start_freq, end_freq, step=100e3, duration=0.5):
        """Scan a frequency range for active signals"""
        print(f"\nScanning from {start_freq/1e6:.3f} MHz to {end_freq/1e6:.3f} MHz...")
        detected = []
        
        freq = start_freq
        while freq <= end_freq:
            self.sdr.center_freq = freq
            time.sleep(0.1)  # Allow SDR to settle
            
            # Capture samples
            samples = self.sdr.read_samples(int(self.sdr.sample_rate * duration))
            
            # Calculate power spectrum
            power = np.abs(np.fft.fft(samples))**2
            avg_power = np.mean(power)
            max_power = np.max(power)
            
            # Detect signal if power exceeds threshold
            if max_power > avg_power * 10:  # Adjust threshold as needed
                signal_info = {
                    'frequency': freq,
                    'power_db': 10 * np.log10(max_power),
                    'timestamp': datetime.now().isoformat()
                }
                detected.append(signal_info)
                print(f"✓ Signal detected at {freq/1e6:.3f} MHz (Power: {signal_info['power_db']:.1f} dB)")
            
            freq += step
            
        return detected
    
    def capture_signal(self, frequency, duration=2.0):
        """Capture a signal at specific frequency for later transmission"""
        print(f"\nCapturing signal at {frequency/1e6:.3f} MHz for {duration}s...")
        self.sdr.center_freq = frequency
        time.sleep(0.2)
        
        samples = self.sdr.read_samples(int(self.sdr.sample_rate * duration))
        
        signal_data = {
            'frequency': frequency,
            'sample_rate': self.sdr.sample_rate,
            'samples': samples.tolist(),  # Convert to list for JSON serialization
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to file
        filename = f"rc_signal_{frequency/1e6:.3f}MHz_{int(time.time())}.json"
        with open(filename, 'w') as f:
            # Save metadata (samples would be too large for JSON in practice)
            metadata = {k: v for k, v in signal_data.items() if k != 'samples'}
            json.dump(metadata, f, indent=2)
        
        # Save raw samples separately
        np.save(filename.replace('.json', '.npy'), samples)
        print(f"Signal saved to {filename} and .npy file")
        
        return signal_data
    
    def analyze_modulation(self, samples):
        """Analyze the modulation scheme of captured samples"""
        # Calculate instantaneous frequency (FM detection)
        analytic_signal = np.abs(samples)
        phase = np.unwrap(np.angle(samples))
        inst_freq = np.diff(phase) / (2.0 * np.pi) * self.sdr.sample_rate
        
        # Simple modulation detection
        am_variance = np.var(analytic_signal)
        fm_variance = np.var(inst_freq)
        
        if am_variance > fm_variance * 2:
            return "Likely AM (Amplitude Modulation)"
        else:
            return "Likely FM (Frequency Modulation)"
    
    def close(self):
        """Close SDR connection"""
        self.sdr.close()


class RCTransmitter:
    """
    Transmitter class - requires HackRF or similar TX-capable SDR
    Note: Transmitting on RC frequencies may require a license in your region
    """
    def __init__(self):
        print("WARNING: Transmitting requires appropriate hardware (HackRF/LimeSDR)")
        print("WARNING: Ensure you have legal authorization to transmit on these frequencies")
        
    def transmit_signal(self, frequency, samples, sample_rate):
        """
        Transmit captured signal
        This is a placeholder - actual implementation requires:
        - HackRF library (pip install hackrf)
        - or GNU Radio
        - or LimeSDR library
        """
        print(f"\n[SIMULATION] Transmitting on {frequency/1e6:.3f} MHz...")
        print("Actual transmission requires TX-capable hardware and proper libraries")
        print("Example: Use GNU Radio Companion or HackRF Python bindings")
        
        # Placeholder for actual transmission code
        # In reality, you'd use something like:
        # from hackrf import HackRF
        # hackrf = HackRF()
        # hackrf.set_freq(frequency)
        # hackrf.transmit(samples)


def main():
    print("=" * 60)
    print("RC Car Frequency Scanner & Transmitter")
    print("=" * 60)
    print("\nWARNING: This tool is for educational purposes only.")
    print("Ensure you comply with local radio regulations.")
    print("=" * 60)
    
    try:
        scanner = RCFrequencyScanner()
        
        # Menu
        while True:
            print("\n\nOptions:")
            print("1. Scan 27 MHz band")
            print("2. Scan 40 MHz band")
            print("3. Scan 49 MHz band")
            print("4. Scan custom frequency range")
            print("5. Capture signal at specific frequency")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                signals = scanner.scan_frequency_range(*RC_FREQUENCY_BANDS['27MHz'])
            elif choice == '2':
                signals = scanner.scan_frequency_range(*RC_FREQUENCY_BANDS['40MHz'])
            elif choice == '3':
                signals = scanner.scan_frequency_range(*RC_FREQUENCY_BANDS['49MHz'])
            elif choice == '4':
                start = float(input("Start frequency (MHz): ")) * 1e6
                end = float(input("End frequency (MHz): ")) * 1e6
                signals = scanner.scan_frequency_range(start, end)
            elif choice == '5':
                freq = float(input("Frequency to capture (MHz): ")) * 1e6
                duration = float(input("Capture duration (seconds): "))
                signal_data = scanner.capture_signal(freq, duration)
                
                # Analyze the captured signal
                samples = np.array(signal_data['samples'])
                modulation = scanner.analyze_modulation(samples)
                print(f"Modulation type: {modulation}")
                
                # Ask about transmission
                tx = input("\nSimulate transmission? (y/n): ").lower()
                if tx == 'y':
                    transmitter = RCTransmitter()
                    transmitter.transmit_signal(freq, samples, signal_data['sample_rate'])
            elif choice == '6':
                break
            else:
                print("Invalid option")
        
        scanner.close()
        print("\nScanner closed. Goodbye!")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you have:")
        print("1. RTL-SDR dongle connected")
        print("2. Installed pyrtlsdr: pip install pyrtlsdr")
        print("3. Proper USB permissions (may need sudo on Linux)")


if __name__ == "__main__":
    main()
