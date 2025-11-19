#!/usr/bin/env python3

"""
Viralytics Feature Extractor
=============================
Pipeline-Refactoring: Integration von T1-T4 Code

Verantwortlich: ML von A
Verwendung: Backend (B) für den /predict Endpunkt
"""

import numpy as np
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# T2 Audio-Abhängigkeiten
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("librosa nicht installiert")

# T3 Video-Abhängigkeiten
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("opencv nicht installiert")


# ============================================
# HAUPTFUNKTION (Backend ruft diese auf)
# ============================================

def extract_features(video_path: str) -> dict:
    """
    Extrahiert alle Features aus einem Video.
    
    Integration von T1 (Metadaten) + T2 (Audio) + T3 (Video) Features.
    
    Args:
        video_path: Pfad zur Videodatei (str)
        
    Returns:
        dict: Dictionary mit allen Features (entspricht den Trainings-Spalten)
        
    Beispiel:
        >>> features = extract_features("video.mp4")
        >>> print(features['avg_brightness'])
        0.65
    """
    
    video_path = Path(video_path)
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video nicht gefunden: {video_path}")
    
    print(f"Feature-Extraktion: {video_path.name}")
    
    all_features = {}
    
    # ============================================
    # T2: Audio-Features
    # ============================================
    print("    T2: Audio-Features...")
    try:
        audio_features = extract_audio_features(str(video_path))
        all_features.update(audio_features)
        print(f"     {len(audio_features)} Audio-Features")
    except Exception as e:
        print(f"      Fehler: {str(e)[:50]}")
        all_features.update(get_default_audio_features())
    
    # ============================================
    # T3: Video-Features
    # ============================================
    print("   T3: Video-Features...")
    try:
        video_features = extract_video_features(str(video_path))
        all_features.update(video_features)
        print(f"      {len(video_features)} Video-Features")
    except Exception as e:
        print(f"       Fehler: {str(e)[:50]}")
        all_features.update(get_default_video_features())
    
    # ============================================
    # T4: Feature-Validierung
    # ============================================
    all_features = validate_features(all_features)
    
    print(f"   Gesamt: {len(all_features)} Features extrahiert")
    
    return all_features


# ============================================
# T2: AUDIO FEATURES
# ============================================

def extract_audio_features(video_path: str) -> dict:
    """
    T2 Audio-Feature-Extraktion
    
    Aus dem T2-Notebook integriert
    """
    
    if not LIBROSA_AVAILABLE:
        return get_default_audio_features()
    
    features = {}
    
    # Audio laden
    y, sr = librosa.load(video_path, sr=22050, mono=True)
    
    if len(y) == 0:
        return get_default_audio_features()
    
    # ----- MFCCs (Mel-Frequency Cepstral Coefficients) -----
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    for i in range(13):
        features[f'mfcc_{i+1}_mean'] = float(np.mean(mfccs[i]))
        features[f'mfcc_{i+1}_std'] = float(np.std(mfccs[i]))
    
    # ----- Spektrale Features -----
    # Spectral Centroid
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    features['spectral_centroid_mean'] = float(np.mean(spec_cent))
    features['spectral_centroid_std'] = float(np.std(spec_cent))
    
    # Spectral Bandwidth
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    features['spectral_bandwidth_mean'] = float(np.mean(spec_bw))
    features['spectral_bandwidth_std'] = float(np.std(spec_bw))
    
    # Spectral Rolloff
    spec_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    features['spectral_rolloff_mean'] = float(np.mean(spec_rolloff))
    features['spectral_rolloff_std'] = float(np.std(spec_rolloff))
    
    # ----- Rhythmus-Features -----
    # Zero Crossing Rate
    zcr = librosa.feature.zero_crossing_rate(y)
    features['zcr_mean'] = float(np.mean(zcr))
    features['zcr_std'] = float(np.std(zcr))
    
    # RMS Energy
    rms = librosa.feature.rms(y=y)
    features['rms_mean'] = float(np.mean(rms))
    features['rms_std'] = float(np.std(rms))
    
    # Tempo (BPM)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    features['tempo'] = float(tempo)
    
    # ----- Chroma-Features -----
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    features['chroma_mean'] = float(np.mean(chroma))
    features['chroma_std'] = float(np.std(chroma))
    
    return features


# ============================================
# T3: VIDEO FEATURES
# ============================================

def extract_video_features(video_path: str) -> dict:
    """
    T3 Video-Feature-Extraktion
    
    Aus dem T3 integriert
    """
    
    if not CV2_AVAILABLE:
        return get_default_video_features()
    
    features = {}
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return get_default_video_features()
    
    # ----- Video-Grundinformationen -----
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0
    
    features['duration'] = duration
    features['fps'] = fps
    features['width'] = width
    features['height'] = height
    features['resolution'] = width * height
    
    # ----- Frame-Analyse -----
    brightness_list = []
    contrast_list = []
    saturation_list = []
    motion_list = []
    
    prev_gray = None
    scene_changes = 0
    
    # Frames samplen (Performance-Optimierung)
    sample_interval = max(1, frame_count // 30)
    
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx % sample_interval == 0:
            # Graustufenbild
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Helligkeit
            brightness_list.append(np.mean(gray) / 255.0)
            
            # Kontrast
            contrast_list.append(np.std(gray) / 255.0)
            
            # Sättigung
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            saturation_list.append(np.mean(hsv[:, :, 1]) / 255.0)
            
            # Bewegung (Frame-Differenz)
            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                motion = np.mean(diff) / 255.0
                motion_list.append(motion)
                
                # Szenenwechsel-Erkennung
                if motion > 0.3:
                    scene_changes += 1
            
            prev_gray = gray
        
        frame_idx += 1
    
    cap.release()
    
    # ----- Statistische Features -----
    features['avg_brightness'] = np.mean(brightness_list) if brightness_list else 0.5
    features['std_brightness'] = np.std(brightness_list) if brightness_list else 0.0
    features['min_brightness'] = np.min(brightness_list) if brightness_list else 0.0
    features['max_brightness'] = np.max(brightness_list) if brightness_list else 1.0
    
    features['avg_contrast'] = np.mean(contrast_list) if contrast_list else 0.5
    features['std_contrast'] = np.std(contrast_list) if contrast_list else 0.0
    
    features['avg_saturation'] = np.mean(saturation_list) if saturation_list else 0.5
    features['std_saturation'] = np.std(saturation_list) if saturation_list else 0.0
    
    features['avg_motion'] = np.mean(motion_list) if motion_list else 0.0
    features['max_motion'] = np.max(motion_list) if motion_list else 0.0
    features['motion_variance'] = np.var(motion_list) if motion_list else 0.0
    
    features['scene_changes'] = scene_changes
    features['scene_change_rate'] = scene_changes / duration if duration > 0 else 0.0
    
    return features


# ============================================
# T4: STANDARDWERTE (Fehlerbehandlung)
# ============================================

def get_default_audio_features() -> dict:
    """Standardwerte für T2 Audio-Features"""
    features = {}
    
    # MFCCs
    for i in range(13):
        features[f'mfcc_{i+1}_mean'] = 0.0
        features[f'mfcc_{i+1}_std'] = 0.0
    
    # Spektrale Features
    features['spectral_centroid_mean'] = 0.0
    features['spectral_centroid_std'] = 0.0
    features['spectral_bandwidth_mean'] = 0.0
    features['spectral_bandwidth_std'] = 0.0
    features['spectral_rolloff_mean'] = 0.0
    features['spectral_rolloff_std'] = 0.0
    
    # Rhythmus-Features
    features['zcr_mean'] = 0.0
    features['zcr_std'] = 0.0
    features['rms_mean'] = 0.0
    features['rms_std'] = 0.0
    features['tempo'] = 120.0
    
    # Chroma-Features
    features['chroma_mean'] = 0.0
    features['chroma_std'] = 0.0
    
    return features


def get_default_video_features() -> dict:
    """Standardwerte für T3 Video-Features"""
    return {
        'duration': 0.0,
        'fps': 30.0,
        'width': 1080,
        'height': 1920,
        'resolution': 1080 * 1920,
        'avg_brightness': 0.5,
        'std_brightness': 0.0,
        'min_brightness': 0.0,
        'max_brightness': 1.0,
        'avg_contrast': 0.5,
        'std_contrast': 0.0,
        'avg_saturation': 0.5,
        'std_saturation': 0.0,
        'avg_motion': 0.0,
        'max_motion': 0.0,
        'motion_variance': 0.0,
        'scene_changes': 0,
        'scene_change_rate': 0.0,
    }


def validate_features(features: dict) -> dict:
    """
    T4: Feature-Validierung Sicherstellen, dass alle Features vorhanden und gültig sind
    """
    # NaN und Inf prüfen
    for key, value in features.items():
        if isinstance(value, (int, float)):
            if np.isnan(value) or np.isinf(value):
                features[key] = 0.0
    
    return features


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print(" Feature Extractor Test (T4 Pipeline)")
    print("=" * 60)
    
    # Test-Video geben
    test_video = Path("test_videos/test_normal_7544548353590250758.mp4")
    
    if test_video.exists():
        features = extract_features(str(test_video))
        
        print(f"\n Extrahierte Features ({len(features)}):")
        print("-" * 60)
        
        # Erste 10 anzeigen
        for i, (key, value) in enumerate(sorted(features.items())):
            if i < 10:
                if isinstance(value, float):
                    print(f"   {key:<30} {value:.6f}")
                else:
                    print(f"   {key:<30} {value}")
        
        print(f"   ... und {len(features) - 10} weitere")
        
        # Als JSON speichern (für Backend-Tests)
        import json
        with open("test_features_output.json", "w") as f:
            json.dump(features, f, indent=2)
        
        print(f"\n Test-Output gespeichert: test_features_output.json")
        
    else:
        print(f" Test-Video nicht gefunden: {test_video}")
        print("\n Verfügbare Videos:")
        for f in Path("test_videos").glob("*.mp4"):
            print(f"   • {f.name}")
    
    print("\n" + "=" * 60)
    print(" Feature Extractor bereit für Backend-Integration!")
    print("=" * 60)
    print("\nVerwendung im Backend:")
    print("   from feature_extractor import extract_features")
    print("   features = extract_features('video.mp4')")
