import wfdb
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks

# ── 1. Download data (it will download automatically on the first run).──────────────────────
record = wfdb.rdrecord('mitdb/100', pn_dir='mitdb')
signal = record.p_signal[:, 0]   
fs = record.fs                   
print(f"Sampling rate: {fs} Hz, signal length: {len(signal)} sampling points")

# ── 2. Bandpass filtering (preserves 5–15 Hz, removes baseline drift and high-frequency noise)──────
def bandpass_filter(sig, fs, lowcut=5.0, highcut=15.0, order=3):
    nyq = fs / 2
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype='band')
    return filtfilt(b, a, sig)

filtered = bandpass_filter(signal, fs)

# ── 3. Detecting the R-wave peak ───────────────────────────────────────────
# distance=0.6*fs This indicates that there is at least a 0.6-second interval between the two peaks (maximum 100 BPM).
peaks, _ = find_peaks(filtered, height=0.3, distance=int(0.6 * fs))
print(f"R-wave peak detected：{len(peaks)} ")

# ── 4. Calculate heart rate (BPM)────────────────────────────────────────
rr_intervals = np.diff(peaks) / fs          # R-R interval, in seconds.
heart_rates = 60 / rr_intervals             # Convert to BPM
avg_hr = np.mean(heart_rates)
print(f"average heart rate: {avg_hr:.1f} BPM")

# ── 5. drawing ───────────────────────────────────────────────────
duration = 10   # The first 10 seconds are displayed.
samples = duration * fs
t = np.arange(samples) / fs

fig, axes = plt.subplots(3, 1, figsize=(12, 8))
fig.suptitle(f'ECG Heart Rate Detection  |  Avg HR: {avg_hr:.1f} BPM', fontsize=14)

# Original signal
axes[0].plot(t, signal[:samples], color='steelblue', linewidth=0.8)
axes[0].set_title('Raw ECG Signal')
axes[0].set_ylabel('Amplitude (mV)')

# After filtering, +R peak marker
axes[1].plot(t, filtered[:samples], color='teal', linewidth=0.8)
visible_peaks = peaks[peaks < samples]
axes[1].plot(visible_peaks / fs, filtered[visible_peaks],
             'rv', markersize=8, label='R-peaks')
axes[1].set_title('Filtered Signal + R-Peak Detection')
axes[1].set_ylabel('Amplitude')
axes[1].legend()

# Heart rate change trend
axes[2].plot(heart_rates[:50], color='coral', marker='o',
             markersize=3, linewidth=1)
axes[2].axhline(avg_hr, color='red', linestyle='--',
                label=f'Mean {avg_hr:.1f} BPM')
axes[2].set_title('Beat-by-Beat Heart Rate')
axes[2].set_ylabel('Heart Rate (BPM))')
axes[2].set_xlabel('Beat index')
axes[2].legend()

plt.tight_layout()
plt.savefig('ecg_result.png', dpi=150)
plt.show()
print("Saved as ecg_result.png")