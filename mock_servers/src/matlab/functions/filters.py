import numpy as np
from scipy import signal
from typing import List, Dict, Any

class FilterFunctions:
    def lowpass(
        self, 
        signal_data: List[float], 
        cutoff_freq: float, 
        sampling_rate: float
    ) -> List[float]:
        """低通滤波器实现"""
        nyquist = sampling_rate / 2
        normalized_cutoff = cutoff_freq / nyquist
        b, a = signal.butter(4, normalized_cutoff, btype='low')
        filtered = signal.filtfilt(b, a, signal_data)
        return filtered.tolist()
    
    def highpass(
        self, 
        signal_data: List[float], 
        cutoff_freq: float, 
        sampling_rate: float
    ) -> List[float]:
        """高通滤波器实现"""
        nyquist = sampling_rate / 2
        normalized_cutoff = cutoff_freq / nyquist
        b, a = signal.butter(4, normalized_cutoff, btype='high')
        filtered = signal.filtfilt(b, a, signal_data)
        return filtered.tolist()
    
    def bandpass(
        self, 
        signal_data: List[float], 
        low_cutoff: float, 
        high_cutoff: float, 
        sampling_rate: float
    ) -> List[float]:
        """带通滤波器实现"""
        nyquist = sampling_rate / 2
        low = low_cutoff / nyquist
        high = high_cutoff / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, signal_data)
        return filtered.tolist() 