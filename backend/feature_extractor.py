"""
Viralytics Feature Extractor 
=======================================================
Kombiniert:
- Audio-Analyse (Librosa) 
- Video-Analyse (OpenCV) 
- MAPPING -> Exakt auf FINAL_FEATURE_MATRIX.csv angepasst
"""

import numpy as np
from pathlib import Path
import warnings
import math

warnings.filterwarnings('ignore')

# --- AUDIO IMPORTS ---
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("WARNING: librosa nicht installiert.")

# --- VIDEO, YOLO & TEXT IMPORTS ---
try:
    import cv2
    import pytesseract
    import nltk
    from ultralytics import YOLO
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    
    # NLTK Daten laden (VADER Lexikon)
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
        
    CV2_AVAILABLE = True
    sia = SentimentIntensityAnalyzer()
    
    # YOLO laden (automatischer Download beim ersten Start)
    print("Lade YOLOv8 Modell (Nano)...")
    yolo_model = YOLO('yolov8n.pt')
    print("YOLOv8 bereit.")
    
except ImportError:
    CV2_AVAILABLE = False
    yolo_model = None
    print("WARNING: opencv, ultralytics, pytesseract oder nltk fehlen.")


def extract_features(video_path: str) -> dict:
    """
    Hauptfunktion: Extrahiert Audio, Video, Objekte, Text und Sentiment.
    Passt die Keys exakt an FINAL_FEATURE_MATRIX.csv an.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video nicht gefunden: {video_path}")
    
    print(f"Starte Analyse für: {video_path.name}")
    
    # 1. Rohdaten extrahieren
    raw_audio = extract_audio_raw(str(video_path))
    raw_video = extract_video_complex(str(video_path)) # Enthält jetzt YOLO + OCR
    
    # 2. MAPPING auf Modell-Spalten (FINAL_FEATURE_MATRIX)
    final_features = {}

    # --- VIDEO & KI MAPPING ---
    final_features['video_dauer_sek'] = raw_video.get('duration', 0.0)
    final_features['anzahl_frames'] = raw_video.get('frame_count', 0.0)
    
    # Metrik: Schnittfrequenz (Schnitte pro Sekunde)
    final_features['schnitt_frequenz'] = raw_video.get('scene_change_rate', 0.0)
    
    final_features['durchschnittliche_bewegung'] = raw_video.get('avg_motion', 0.0)
    
    # YOLO Features (Dynamische Werte statt statischer 0.0)
    # ist_person_prominent: 1.0 wenn Person erkannt, sonst 0.0
    final_features['ist_person_prominent'] = 1.0 if raw_video.get('person_detected', False) else 0.0
    
    # ist_tier_sichtbar: 1.0 wenn Tier erkannt, sonst 0.0
    final_features['ist_tier_sichtbar'] = 1.0 if raw_video.get('animal_detected', False) else 0.0
    
    # avg_objekte_pro_frame: Echter Durchschnittswert aus YOLO
    final_features['avg_objekte_pro_frame'] = raw_video.get('avg_objects', 0.0)
    
    # avg_gesichter_pro_frame: Wir nutzen "Personenanzahl" als Näherungswert
    final_features['avg_gesichter_pro_frame'] = raw_video.get('avg_persons', 0.0)
    
    # Text & Sentiment Features (OCR + VADER)
    final_features['ist_text_eingeblendet'] = 1.0 if raw_video.get('has_text', False) else 0.0
    final_features['text_sentiment_compound'] = raw_video.get('sentiment_compound', 0.0)
    
    # --- AUDIO MAPPING ---
    final_features['bpm'] = raw_audio.get('tempo', 0.0)
    final_features['rms_mean'] = raw_audio.get('rms_mean', 0.0)
    final_features['rms_std'] = raw_audio.get('rms_std', 0.0)
    final_features['spectral_centroid_mean'] = raw_audio.get('spectral_centroid_mean', 0.0)
    final_features['spectral_centroid_std'] = raw_audio.get('spectral_centroid_std', 0.0)
    final_features['spectral_bandwidth_mean'] = raw_audio.get('spectral_bandwidth_mean', 0.0)
    final_features['spectral_bandwidth_std'] = raw_audio.get('spectral_bandwidth_std', 0.0)
    
    # Speech Ratio Proxy via ZCR
    zcr = raw_audio.get('zcr_mean', 0.0)
    final_features['speech_ratio'] = min(1.0, zcr * 5)
    
    # Chroma Varianzen (Mapping auf chroma_var_0 bis 11)
    c_std = raw_audio.get('chroma_std', 0.0)
    for i in range(12):
        final_features[f'chroma_var_{i}'] = c_std

    # --- PLATZHALTER (Limits der Pipeline) ---
    # Diese Werte können wir ohne Metadaten oder Spezial-Modelle nicht berechnen.
    final_features['video_kategorie'] = 'unknown' 
    final_features['dominante_emotion'] = 'neutral'
    final_features['txt_title_has_mention'] = 0.0
    final_features['txt_title_has_question'] = 0.0
    final_features['txt_title_has_hashtag'] = 0.0

    # NaN Cleanup
    for k, v in final_features.items():
        if isinstance(v, (float, int)) and (np.isnan(v) or np.isinf(v)):
            final_features[k] = 0.0

    return final_features


# ============================================
# EXTRAKTION: AUDIO (Librosa)
# ============================================
def extract_audio_raw(video_path):
    if not LIBROSA_AVAILABLE: return {}
    try:
        y, sr = librosa.load(video_path, sr=22050, mono=True, duration=60)
        if len(y) == 0: return {}
        feats = {}
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        feats['tempo'] = float(tempo)
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        feats['spectral_centroid_mean'] = float(np.mean(cent))
        feats['spectral_centroid_std'] = float(np.std(cent))
        bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        feats['spectral_bandwidth_mean'] = float(np.mean(bw))
        feats['spectral_bandwidth_std'] = float(np.std(bw))
        feats['rms_mean'] = float(np.mean(librosa.feature.rms(y=y)))
        feats['rms_std'] = float(np.std(librosa.feature.rms(y=y)))
        feats['zcr_mean'] = float(np.mean(librosa.feature.zero_crossing_rate(y)))
        feats['chroma_std'] = float(np.std(librosa.feature.chroma_stft(y=y, sr=sr)))
        return feats
    except Exception as e:
        print(f"⚠️ Audio Fehler: {e}")
        return {}


# ============================================
# EXTRAKTION: VIDEO + YOLO + OCR (Dynamisch)
# ============================================
def extract_video_complex(video_path):
    if not CV2_AVAILABLE or yolo_model is None: return {}
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened(): return {}
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        feats = {
            'duration': duration, 
            'frame_count': frame_count,
            'avg_motion': 0.0,
            'scene_change_rate': 0.0,
            'avg_brightness': 0.0,
            # YOLO Features
            'person_detected': False,
            'animal_detected': False,
            'avg_objects': 0.0,
            'avg_persons': 0.0,
            # TEXT Features
            'has_text': False,
            'sentiment_compound': 0.0
        }
        
        prev_gray = None
        motion_vals = []
        brightness_vals = []
        scene_changes = 0
        detected_text_content = ""
        
        total_objects = 0
        total_persons = 0
        analyzed_frames = 0
        
        # Performance: Max 20 Frames analysieren (Sampling)
        step = max(1, int(frame_count / 20)) 
        
        # YOLO Klassen für Tiere (COCO Dataset IDs)
        ANIMAL_IDS = [15, 16, 17, 18, 19, 20, 21, 22, 23] 

        for i in range(0, frame_count, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret: break
            
            analyzed_frames += 1
            
            # 1. Bildverarbeitung (Graustufen für Helligkeit/Bewegung)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness_vals.append(np.mean(gray) / 255.0)
            
            # Bewegung
            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                score = np.mean(diff) / 255.0
                motion_vals.append(score)
                # Wenn sich mehr als 30% des Bildes ändert -> Schnitt
                if score > 0.3: scene_changes += 1
            prev_gray = gray
            
            # 2. YOLO Analyse (Objekterkennung)
            results = yolo_model(frame, verbose=False)
            frame_objects = 0
            frame_persons = 0
            
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    frame_objects += 1
                    
                    if cls_id == 0: # 0 ist 'person' in COCO
                        frame_persons += 1
                        feats['person_detected'] = True
                    
                    if cls_id in ANIMAL_IDS:
                        feats['animal_detected'] = True
            
            total_objects += frame_objects
            total_persons += frame_persons
            
            # 3. OCR (Text) - Nur wenn Tesseract verfügbar ist
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                text = pytesseract.image_to_string(rgb_frame)
                if text.strip():
                    detected_text_content += " " + text.strip()
            except: pass
            
        cap.release()
        
        # Aggregation der gesammelten Werte
        if analyzed_frames > 0:
            feats['avg_objects'] = total_objects / analyzed_frames
            feats['avg_persons'] = total_persons / analyzed_frames
            
        feats['avg_motion'] = np.mean(motion_vals) if motion_vals else 0.0
        feats['avg_brightness'] = np.mean(brightness_vals) if brightness_vals else 0.5
        feats['scene_change_rate'] = scene_changes / duration if duration > 0 else 0.0
        
        # Sentiment-Analyse des erkannten Textes
        if len(detected_text_content) > 5:
            feats['has_text'] = True
            scores = sia.polarity_scores(detected_text_content)
            feats['sentiment_compound'] = scores['compound']
        
        return feats
        
    except Exception as e:
        print(f" Video Analyse Fehler: {e}")
        return {}