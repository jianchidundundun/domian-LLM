from typing import List, Dict, Any
import numpy as np
from scipy import signal

class SignalProcessing:
    def fft(self, data: List[float]) -> Dict[str, List[float]]:
        """执行傅里叶变换"""
        fft_result = np.fft.fft(data)
        return {
            "magnitude": np.abs(fft_result).tolist(),
            "phase": np.angle(fft_result).tolist()
        }
        
    def ifft(self, data: List[complex]) -> List[float]:
        """执行逆傅里叶变换"""
        return np.fft.ifft(data).real.tolist()

class FilterFunctions:
    def lowpass(
        self, 
        signal_data: List[float], 
        cutoff_freq: float, 
        sampling_rate: float
    ) -> Dict[str, List[float]]:
        """低通滤波器"""
        nyquist = sampling_rate / 2
        normalized_cutoff = cutoff_freq / nyquist
        b, a = signal.butter(4, normalized_cutoff, btype='low')
        filtered = signal.filtfilt(b, a, signal_data)
        return {
            "filtered_signal": filtered.tolist(),
            "b": b.tolist(),
            "a": a.tolist()
        }
        
    def highpass(
        self, 
        signal_data: List[float], 
        cutoff_freq: float, 
        sampling_rate: float
    ) -> Dict[str, List[float]]:
        """高通滤波器"""
        nyquist = sampling_rate / 2
        normalized_cutoff = cutoff_freq / nyquist
        b, a = signal.butter(4, normalized_cutoff, btype='high')
        filtered = signal.filtfilt(b, a, signal_data)
        return {
            "filtered_signal": filtered.tolist(),
            "b": b.tolist(),
            "a": a.tolist()
        }
        
    def bandpass(
        self, 
        signal_data: List[float], 
        low_cutoff: float, 
        high_cutoff: float, 
        sampling_rate: float
    ) -> Dict[str, List[float]]:
        """带通滤波器"""
        nyquist = sampling_rate / 2
        low = low_cutoff / nyquist
        high = high_cutoff / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, signal_data)
        return {
            "filtered_signal": filtered.tolist(),
            "b": b.tolist(),
            "a": a.tolist()
        } 