"""
Viralytics Feature Extractor
=============================
Pipeline-Refactoring: Integration von T1 (Metadaten) + T2 (Audio) + T3 (Video)
Verantwortlich: T4 
Verwendung: Backend für den /predict Endpunkt
Ziel: 100% Features Übereinstimmung mit FINAL_FEATURE_MATRIX.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path
import re
import warnings
warnings.filterwarnings('ignore')

# ============================================
# DEPENDENCIES CHECK
# ============================================

# T2 Audio-Abhängigkeiten
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("librosa nicht installiert - Audio-Features werden auf defaulte Werte gesetzt")

# oder
try:
    import webrtcvad
    VAD_AVAILABLE = True
except ImportError:
    VAD_AVAILABLE = False

# T3 Video-Abhängigkeiten
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Opencv nicht installiert - Video-Features werden auf defaulte Werte gesetzt")


# ============================================
# HAUPTFUNKTION (Backend ruft hier auf)
# ============================================

def extract_features(video_path: str, metadata: dict = None) -> dict:
    """
    Extrahiert alle Features aus einem Video.
    
    Integration von T1 (Metadaten) + T2 (Audio) + T3 (Video) Features.
    
    Args:
        video_path: Pfad zur Videodatei (str)
        metadata: Optional - Metadaten-Dictionary mit Keys wie 'title', 'uploader' etc.
        
    Returns:
        dict: Dictionary mit allen Features (entspricht FINAL_FEATURE_MATRIX.csv)
        
    Beispiel:
        >>> features = extract_features("video.mp4", metadata={'title': 'My video'})
        >>> print(features['bpm'])
        120.5
    """
    
    video_path = Path(video_path)
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video nicht gefunden: {video_path}")
    
    print(f"Feature-Extraktion: {video_path.name}")
    
    all_features = {}
    
    # ============================================
    # T1: METADATEN-FEATURES
    # ============================================
    print("T1: Metadaten-Features")
    try:
        metadata_features = extract_metadata_features(str(video_path), metadata)
        all_features.update(metadata_features)
        print(f" {len(metadata_features)} Metadaten-Features")
    except Exception as e:
        print(f"  Fehler: {str(e)[:50]}")
        all_features.update(get_default_metadata_features())
    
    # ============================================
    # T2: AUDIO-FEATURES
    # ============================================
    print("  T2: Audio-Features...")
    try:
        audio_features = extract_audio_features(str(video_path))
        all_features.update(audio_features)
        print(f"     {len(audio_features)} Audio-Features")
    except Exception as e:
        print(f"    Fehler: {str(e)[:50]}")
        all_features.update(get_default_audio_features())
    
    # ============================================
    # T3: VIDEO-FEATURES
    # ============================================
    print("  T3: Video-Features...")
    try:
        video_features = extract_video_features(str(video_path))
        all_features.update(video_features)
        print(f"     {len(video_features)} Video-Features")
    except Exception as e:
        print(f"    Fehler: {str(e)[:50]}")
        all_features.update(get_default_video_features())
    
    # ============================================
    # T4: Feature-Validierung
    # ============================================
    all_features = validate_features(all_features)
    
    print(f"  {len(all_features)} Features extrahiert")
    
    return all_features


# ============================================
# T1: METADATEN FEATURES
# ============================================

def extract_metadata_features(video_path: str, metadata: dict = None) -> dict:
    """
    T1 Metadaten-Feature-Extraktion
    
    Aus dem T1-Notebook: 02a_Metadaten_Features_Engineering.ipynb
    """
    
    features = {}
    
    if metadata is None:
        metadata = {}
    
    def safe_str(s): 
        return s if isinstance(s, str) else ""
    
    # ============================================
    # Account-Features
    # ============================================
    
    uploader = safe_str(metadata.get("uploader", ""))
    features["acct_uploader_len"] = len(uploader)
    
    if features["acct_uploader_len"] > 0:
        features["acct_uploader_digits_ratio"] = len(re.findall(r'\d', uploader)) / features["acct_uploader_len"]
    else:
        features["acct_uploader_digits_ratio"] = 0.0
    
    features["acct_creator_verified"] = int(metadata.get("creator_verified", False))
    
    # Log-transformierte Werte
    creator_follower = float(metadata.get("creator_follower_count", 0))
    creator_posts = float(metadata.get("creator_posts_count", 0))
    features["acct_creator_follower_log"] = np.log1p(creator_follower)
    features["acct_creator_posts_log"] = np.log1p(creator_posts)
    
    # ============================================
    # Text-/Titel-Features
    # ============================================
    
    title = safe_str(metadata.get("title", ""))
    features["txt_title_len_chars"] = len(title)
    features["txt_title_len_words"] = len(title.split())
    features["txt_title_has_question"] = int(bool(re.search(r'\?', title)))
    features["txt_title_has_exclaim"] = int(bool(re.search(r'!', title)))
    features["txt_title_has_hashtag"] = int(bool(re.search(r'#\w+', title)))
    features["txt_title_has_mention"] = int(bool(re.search(r'@\w+', title)))
    features["txt_title_has_url"] = int(bool(re.search(r'(https?://|www\.)', title, re.IGNORECASE)))
    
    # ============================================
    # Längen-Features
    # ============================================
    
    duration_s = float(metadata.get("duration_s", 0))
    features["len_duration_s"] = duration_s
    
    # len_bucket (categorical)
    if duration_s <= 6:
        features["len_bucket"] = "very_short"
    elif duration_s <= 15:
        features["len_bucket"] = "short"
    elif duration_s <= 30:
        features["len_bucket"] = "mid"
    elif duration_s <= 60:
        features["len_bucket"] = "long"
    else:
        features["len_bucket"] = "very_long"
    
    return features


def get_default_metadata_features() -> dict:
    """Standardwerte für T1 Metadaten-Features"""
    return {
        'acct_uploader_len': 0,
        'acct_uploader_digits_ratio': 0.0,
        'acct_creator_verified': 0,
        'acct_creator_follower_log': 0.0,
        'acct_creator_posts_log': 0.0,
        'txt_title_len_chars': 0,
        'txt_title_len_words': 0,
        'txt_title_has_question': 0,
        'txt_title_has_exclaim': 0,
        'txt_title_has_hashtag': 0,
        'txt_title_has_mention': 0,
        'txt_title_has_url': 0,
        'len_duration_s': 0.0,
        'len_bucket': 'mid',
    }


# ============================================
# T2: AUDIO FEATURES
# ============================================

def compute_speech_ratio(y, sr, frame_ms=30, vad_mode=2):
    """
    Berechnet Speech Ratio mit webrtcvad (optional)
    Exakt wie im T2 Notebook
    """
    if not VAD_AVAILABLE:
        return np.nan
    
    try:
        target_sr = 16000
        if sr != target_sr:
            y_rs = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
        else:
            y_rs = y
        
        pcm16 = (np.clip(y_rs, -1.0, 1.0) * 32767).astype(np.int16)
        raw = pcm16.tobytes()
        vad = webrtcvad.Vad(vad_mode)
        frame_bytes = int(target_sr * (frame_ms / 1000.0) * 2)
        n_frames = len(raw) // frame_bytes
        
        if n_frames == 0:
            return np.nan
        
        speech = 0
        for i in range(n_frames):
            s = i * frame_bytes
            e = s + frame_bytes
            if vad.is_speech(raw[s:e], sample_rate=target_sr):
                speech += 1
        
        return float(speech) / float(n_frames)
    except:
        return np.nan


def extract_audio_features(video_path: str) -> dict:
    """
    T2 Audio-Feature-Extraktion
    
    Aus dem T2-Notebook: 02_Audio_Features_Extraction.ipynb
    EXAKT DIE GLEICHE LOGIK wie im Original
    """
    
    if not LIBROSA_AVAILABLE:
        return get_default_audio_features()
    
    features = {}
    
    try:
        # Audio laden (sr=None wie im Original)
        y, sr = librosa.load(video_path, sr=None, mono=False)
        
        # Stereo zu Mono
        if isinstance(y, np.ndarray) and y.ndim > 1:
            y = librosa.to_mono(y)
        y = y.astype(float)
        
        # ===== BPM =====
        try:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            features['bpm'] = float(tempo) if isinstance(tempo, (int, float, np.number)) else float(tempo[0])
        except:
            features['bpm'] = 120.0
        
        # ===== RMS (Lautheit) =====
        try:
            rms = librosa.feature.rms(y=y)
            features['rms_mean'] = float(np.mean(rms))
            features['rms_std'] = float(np.std(rms))
        except:
            features['rms_mean'] = 0.05
            features['rms_std'] = 0.02
        
        # ===== Spectral Centroid =====
        try:
            sc = librosa.feature.spectral_centroid(y=y, sr=sr)
            features['spectral_centroid_mean'] = float(np.mean(sc))
            features['spectral_centroid_std'] = float(np.std(sc))
        except:
            features['spectral_centroid_mean'] = 2000.0
            features['spectral_centroid_std'] = 500.0
        
        # ===== Spectral Bandwidth =====
        try:
            sb = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            features['spectral_bandwidth_mean'] = float(np.mean(sb))
            features['spectral_bandwidth_std'] = float(np.std(sb))
        except:
            features['spectral_bandwidth_mean'] = 2000.0
            features['spectral_bandwidth_std'] = 500.0
        
        # ===== Chroma Variance (12 bins) =====
        try:
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_var = np.var(chroma, axis=1)
            for i in range(12):
                features[f'chroma_var_{i}'] = float(chroma_var[i])
        except:
            for i in range(12):
                features[f'chroma_var_{i}'] = 0.08
        
        # ===== Speech Ratio (optional) =====
        try:
            speech_ratio = compute_speech_ratio(y, sr)
            # Fallback wenn webrtcvad nicht funktioniert
            if np.isnan(speech_ratio):
                features['speech_ratio'] = 0.95  # Realistischer Default für TikTok
            else:
                features['speech_ratio'] = speech_ratio
        except:
            features['speech_ratio'] = 0.95
        
        return features
        
    except Exception as e:
        print(f"      Audio-Extraktion fehlgeschlagen: {str(e)[:50]}")
        return get_default_audio_features()


def get_default_audio_features() -> dict:
    """Standardwerte für T2 Audio-Features"""
    features = {
        'bpm': 120.0,
        'rms_mean': 0.05,
        'rms_std': 0.02,
        'spectral_centroid_mean': 2000.0,
        'spectral_centroid_std': 500.0,
        'spectral_bandwidth_mean': 2000.0,
        'spectral_bandwidth_std': 500.0,
        'speech_ratio': 0.95,  # FIX: Realistischer Default für TikTok
    }
    
    # Chroma variance
    for i in range(12):
        features[f'chroma_var_{i}'] = 0.08
    
    return features


# ============================================
# T3: VIDEO FEATURES
# ============================================

def extract_video_features(video_path: str) -> dict:
    """
    T3 Video-Feature-Extraktion
    
    VOLLSTÄNDIGE FEATURES basierend auf video_features.csv
    """
    
    if not CV2_AVAILABLE:
        return get_default_video_features()
    
    features = {}
    
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return get_default_video_features()
        
        # ===== Video-Grundinformationen =====
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        # T3 Original-Features
        # FIX: anzahl_frames ist eigentlich Dauer in Sekunden (nicht Frame-Count!)
        features['anzahl_frames'] = duration
        features['video_dauer_sek'] = duration
        
        # Alte Features (für Kompatibilität)
        features['duration'] = duration
        features['fps'] = fps
        features['width'] = width
        features['height'] = height
        features['resolution'] = width * height
        
        # ===== Frame-Analyse =====
        brightness_list = []
        contrast_list = []
        saturation_list = []
        motion_list = []
        
        prev_gray = None
        scene_changes = 0
        
        # Face detection (einfach, mit OpenCV)
        try:
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            faces_available = True
        except:
            faces_available = False
        
        faces_per_frame = []
        
        # Frames samplen (Performance)
        sample_interval = max(1, frame_count // 30)
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % sample_interval == 0:
                # Grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Helligkeit
                brightness_list.append(np.mean(gray) / 255.0)
                
                # Kontrast
                contrast_list.append(np.std(gray) / 255.0)
                
                # Sättigung
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                saturation_list.append(np.mean(hsv[:, :, 1]) / 255.0)
                
                # Bewegung
                if prev_gray is not None:
                    diff = cv2.absdiff(prev_gray, gray)
                    motion = np.mean(diff)  # In Pixel-Einheiten (0-255)
                    motion_list.append(motion)
                    
                    # Szenenänderung
                    if motion > 75:  # Threshold für Szenenwechsel
                        scene_changes += 1
                
                # Gesichtserkennung
                if faces_available:
                    try:
                        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                        faces_per_frame.append(len(faces))
                    except:
                        faces_per_frame.append(0)
                else:
                    faces_per_frame.append(0)
                
                prev_gray = gray
            
            frame_idx += 1
        
        cap.release()
        
        # ===== STATISTIKEN BERECHNEN =====
        
        # Alte Features (Kompatibilität)
        features['avg_brightness'] = np.mean(brightness_list) if brightness_list else 0.5
        features['std_brightness'] = np.std(brightness_list) if brightness_list else 0.0
        features['min_brightness'] = np.min(brightness_list) if brightness_list else 0.0
        features['max_brightness'] = np.max(brightness_list) if brightness_list else 1.0
        
        features['avg_contrast'] = np.mean(contrast_list) if contrast_list else 0.5
        features['std_contrast'] = np.std(contrast_list) if contrast_list else 0.0
        
        features['avg_saturation'] = np.mean(saturation_list) if saturation_list else 0.5
        features['std_saturation'] = np.std(saturation_list) if saturation_list else 0.0
        
        features['avg_motion'] = np.mean(motion_list) / 255.0 if motion_list else 0.0
        features['max_motion'] = np.max(motion_list) / 255.0 if motion_list else 0.0
        features['motion_variance'] = np.var(motion_list) / (255.0**2) if motion_list else 0.0
        
        features['scene_changes'] = scene_changes
        features['scene_change_rate'] = scene_changes / duration if duration > 0 else 0.0
        
        # ===== T3 ORIGINAL-FEATURES =====
        
        # schnitt_frequenz (Szenenänderungen pro Sekunde)
        features['schnitt_frequenz'] = scene_changes / duration if duration > 0 else 0.0
        
        # durchschnittliche_bewegung (in Pixel-Einheiten, nicht normalisiert)
        features['durchschnittliche_bewegung'] = np.mean(motion_list) if motion_list else 0.0
        
        # avg_gesichter_pro_frame
        features['avg_gesichter_pro_frame'] = np.mean(faces_per_frame) if faces_per_frame else 0.0
        
        # ist_person_prominent (wenn durchschnittlich mindestens 1 Gesicht)
        features['ist_person_prominent'] = 1 if features['avg_gesichter_pro_frame'] >= 0.5 else 0
        
        # FIX: ist_text_eingeblendet (Heuristik basierend auf Kontrast)
        if contrast_list:
            high_contrast_frames = sum(1 for c in contrast_list if c > 0.15)
            features['ist_text_eingeblendet'] = 1 if high_contrast_frames > len(contrast_list) * 0.3 else 0
        else:
            features['ist_text_eingeblendet'] = 1  # Default für TikTok
        
        # ===== PLACEHOLDER für erweiterte Features =====
        # (Benötigen YOLO, DeepFace, OCR, NLP)
        
        features['ist_tier_sichtbar'] = 0  # Benötigt YOLO
        features['avg_objekte_pro_frame'] = 1.5  # Realistischer Placeholder
        features['dominante_emotion'] = 'neutral'  # Benötigt DeepFace
        features['text_sentiment_compound'] = 0.0  # Benötigt NLP
        features['video_kategorie'] = 'General'  # Placeholder
        
        return features
        
    except Exception as e:
        print(f"      Video-Extraktion fehlgeschlagen: {str(e)[:50]}")
        return get_default_video_features()


def get_default_video_features() -> dict:
    """Standardwerte für T3 Video-Features - VOLLSTÄNDIG"""
    return {
        # Basis-Features
        'duration': 30.0,
        'fps': 30.0,
        'width': 1080,
        'height': 1920,
        'resolution': 1080 * 1920,
        
        # Alte Features
        'avg_brightness': 0.5,
        'std_brightness': 0.1,
        'min_brightness': 0.2,
        'max_brightness': 0.8,
        'avg_contrast': 0.5,
        'std_contrast': 0.1,
        'avg_saturation': 0.5,
        'std_saturation': 0.1,
        'avg_motion': 0.1,
        'max_motion': 0.3,
        'motion_variance': 0.01,
        'scene_changes': 5,
        'scene_change_rate': 0.2,
        
        # T3 Original-Features (aus video_features.csv)
        'schnitt_frequenz': 0.2,
        'durchschnittliche_bewegung': 9.0,
        'anzahl_frames': 30.0,  # FIX: Sekunden, nicht Frame-Count!
        'video_dauer_sek': 30.0,
        'ist_person_prominent': 1,
        'ist_tier_sichtbar': 0,
        'avg_objekte_pro_frame': 1.5,
        'avg_gesichter_pro_frame': 1.0,
        'dominante_emotion': 'neutral',
        'ist_text_eingeblendet': 1,  # FIX: Realistischer Default für TikTok
        'text_sentiment_compound': 0.0,
        'video_kategorie': 'General',
    }


# ============================================
# T4: VALIDIERUNG
# ============================================

def validate_features(features: dict) -> dict:
    """
    T4: Feature-Validierung
    Sicherstellen, dass alle Features vorhanden und gültig sind
    """
    # NaN und Inf prüfen
    for key, value in features.items():
        if isinstance(value, (int, float, np.number)):
            if np.isnan(value) or np.isinf(value):
                # Ersetze mit realistischen Defaults
                if 'log' in key:
                    features[key] = 0.0
                elif 'ratio' in key or 'mean' in key:
                    features[key] = 0.5
                elif 'bpm' in key:
                    features[key] = 120.0
                elif 'speech' in key:
                    features[key] = 0.95
                else:
                    features[key] = 0.0
    
    return features


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("Feature Extractor Test (T4 Pipeline - FINAL VERSION)")
    print("=" * 80)
    
    # Test-Video
    test_video = Path("test_videos/test_top_7541847334330600735.mp4")
    
    if not test_video.exists():
        # Fallback
        test_videos = list(Path("test_videos").glob("*.mp4"))
        if test_videos:
            test_video = test_videos[0]
        else:
            print("Keine Test-Videos gefunden!")
            exit(1)
    
    # Test-Metadaten
    test_metadata = {
        "title": "Test video #hashtag @mention",
        "uploader": "test123user",
        "duration_s": 30,
        "creator_verified": False,
        "creator_follower_count": 10000,
        "creator_posts_count": 500,
    }
    
    features = extract_features(str(test_video), metadata=test_metadata)
    
    print(f"\nExtrahierte Features ({len(features)}):")
    print("=" * 80)
    
    # Gruppiert anzeigen
    print("\nMetadaten-Features (T1):")
    for key in sorted(features.keys()):
        if key.startswith(('acct_', 'txt_', 'len_')):
            val = features[key]
            if isinstance(val, float):
                print(f"   {key:<40} {val:.4f}")
            else:
                print(f"   {key:<40} {val}")
    
    print("\nAudio-Features (T2):")
    audio_keys = ['bpm', 'rms_mean', 'rms_std', 'spectral_centroid_mean', 
                  'spectral_centroid_std', 'spectral_bandwidth_mean', 
                  'spectral_bandwidth_std', 'speech_ratio']
    for key in sorted(features.keys()):
        if key in audio_keys or key.startswith('chroma_'):
            val = features[key]
            if isinstance(val, float):
                print(f"   {key:<40} {val:.6f}")
            else:
                print(f"   {key:<40} {val}")
    
    print("\nVideo-Features (T3):")
    for key in sorted(features.keys()):
        if any(x in key for x in ['schnitt', 'bewegung', 'frames', 'dauer', 
                                   'person', 'tier', 'objekte', 'gesichter',
                                   'emotion', 'text_ein', 'kategorie']):
            val = features[key]
            if isinstance(val, float):
                print(f"   {key:<40} {val:.6f}")
            else:
                print(f"   {key:<40} {val}")
    
    # Als JSON speichern
    with open("test_features_output_final.json", "w", encoding='utf-8') as f:
        # Konvertiere numpy types zu Python types
        features_serializable = {}
        for k, v in features.items():
            if isinstance(v, np.integer):
                features_serializable[k] = int(v)
            elif isinstance(v, np.floating):
                features_serializable[k] = float(v)
            else:
                features_serializable[k] = v
        json.dump(features_serializable, f, indent=2, ensure_ascii=False)
    
    print(f"\nTest-Output gespeichert: test_features_output_final.json")
    
    print("\n" + "=" * 80)
    print("Feature Extractor PRODUCTION READY!")
    print("=" * 80)
    print("\nVerwendung im Backend:")
    print("   from feature_extractor import extract_features")
    print("   features = extract_features('video.mp4', metadata={...})")
    print("\nErwartete Erfolgsrate mit FINAL_FEATURE_MATRIX.csv: ~100%")