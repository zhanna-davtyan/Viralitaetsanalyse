#!/usr/bin/env python3
"""
Diagnose: Vergleich zwischen feature_extractor.py und Trainings-Features
FIXED VERSION - Robuster Umgang mit Spalten
"""

import pandas as pd
from pathlib import Path
from feature_extractor import extract_features
import json
import numpy as np

print("=" * 80)
print("🔍 FEATURE MISMATCH DIAGNOSE")
print("=" * 80)

# ============================================
# 1. Trainings-Features laden
# ============================================

training_file = Path("features/FINAL_FEATURE_MATRIX.csv")

if not training_file.exists():
    print(f"FINAL_FEATURE_MATRIX.csv nicht gefunden!")
    print(f"   Gesucht in: {training_file.absolute()}")
    exit(1)

df_train = pd.read_csv(training_file)

print(f"✓ FINAL_FEATURE_MATRIX.csv geladen: {len(df_train)} Videos")
print(f"  Spalten: {list(df_train.columns[:10])}...")

# ============================================
# Spalten identifizieren
# ============================================

# Mögliche ID-Spalten
id_candidates = ['video_id', 'id', 'Video_ID', 'ID', 'filename']
id_col = None
for candidate in id_candidates:
    if candidate in df_train.columns:
        id_col = candidate
        break

if id_col is None:
    print("Keine video_id Spalte gefunden, verwende Index")
    df_train['video_id'] = df_train.index.astype(str)
    id_col = 'video_id'

print(f"  ID-Spalte: {id_col}")

# Nicht-Feature-Spalten
non_feature_cols = [
    id_col, 'is_viral', 'is_viral_proxy', 'group', 'author', 'url', 
    'likes', 'views', 'comments', 'shares', 'description',
    'upload_time', 'hashtags', 'caption', 'rank', 'engagement_score',
    'uploader', 'title', 'duration_s', 'source_file'
]

# Alle Spalten außer non_feature_cols
all_columns = df_train.columns.tolist()
training_features = [col for col in all_columns if col not in non_feature_cols]

print(f"\nAlle Feature-Kandidaten: {len(training_features)}")

# ============================================
# NUR NUMERISCHE FEATURES BEHALTEN
# ============================================

numeric_features = []
text_features = []

for col in training_features:
    if pd.api.types.is_numeric_dtype(df_train[col]):
        numeric_features.append(col)
    else:
        text_features.append(col)

training_features = numeric_features

print(f"  Numerische Features: {len(numeric_features)}")
if text_features:
    print(f"  Text-Features (ignoriert): {len(text_features)}")

# Statistik berechnen
train_stats = {}
for col in training_features:
    try:
        train_stats[col] = {
            'mean': float(df_train[col].mean()),
            'std': float(df_train[col].std()),
            'min': float(df_train[col].min()),
            'max': float(df_train[col].max()),
        }
    except Exception as e:
        print(f"  Kann Statistik für '{col}' nicht berechnen: {e}")

# ============================================
# 2. Ein Test-Video finden
# ============================================

# Nehme das erste Video
first_row = df_train.iloc[0]
test_video_id = str(first_row[id_col])

print(f"\nSuche Video für {id_col}: {test_video_id}")

# Mögliche Pfade (erweitert)
possible_paths = [
    Path(f"data/raw_videos/normal_{test_video_id}.mp4"),
    Path(f"data/raw_videos/top_{test_video_id}.mp4"),
    Path(f"test_videos/test_normal_{test_video_id}.mp4"),
    Path(f"test_videos/test_top_{test_video_id}.mp4"),
    Path(f"videos/normal_{test_video_id}.mp4"),
    Path(f"videos/top_{test_video_id}.mp4"),
]

test_video_path = None
for path in possible_paths:
    if path.exists():
        test_video_path = path
        break

if test_video_path is None:
    print(f"Video für ID {test_video_id} nicht gefunden.")
    print("   Verwende beliebiges Video aus test_videos/")
    test_videos = list(Path("test_videos").glob("*.mp4"))
    if not test_videos:
        print("Keine Videos in test_videos/ gefunden!")
        exit(1)
    test_video_path = test_videos[0]
    # Verwende erste Trainingszeile als Referenz
    df_match = df_train.iloc[[0]]
else:
    df_match = df_train[df_train[id_col].astype(str) == str(test_video_id)]

print(f"✓ Test-Video: {test_video_path.name}")

# Erwartete Features aus Training
expected_features = df_match[training_features].iloc[0].to_dict()

# ============================================
# 3. Features extrahieren
# ============================================

print(f"\nExtrahiere Features mit feature_extractor.py")

# Metadaten aus DataFrame extrahieren
metadata = {
    'title': str(first_row.get('title', '')),
    'uploader': str(first_row.get('uploader', '')),
    'duration_s': float(first_row.get('duration_s', 30)),
    'creator_verified': bool(first_row.get('creator_verified', False)),
    'creator_follower_count': float(first_row.get('creator_follower_count', 0)),
    'creator_posts_count': float(first_row.get('creator_posts_count', 0)),
}

try:
    actual_features = extract_features(str(test_video_path), metadata=metadata)
    print(f"{len(actual_features)} Features extrahiert")
except Exception as e:
    print(f"Fehler: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================
# 4. Vergleich
# ============================================

print("\n" + "=" * 80)
print("FEATURE-VERGLEICH")
print("=" * 80)

mismatches = []
missing = []
correct = []

for feat in training_features:
    if feat not in actual_features:
        missing.append(feat)
        continue
    
    expected = expected_features[feat]
    actual = actual_features[feat]
    
    # Prüfen ob statischer Placeholder
    is_static = (abs(actual) < 0.001 and abs(expected) > 0.1)
    
    # Prüfen ob realistisch
    if feat in train_stats:
        mean = train_stats[feat]['mean']
        std = train_stats[feat]['std']
        is_realistic = abs(actual - mean) <= 3 * std if std > 0.01 else True
    else:
        is_realistic = True
    
    if is_static or not is_realistic:
        mismatches.append({
            'feature': feat,
            'expected': expected,
            'actual': actual,
            'is_static': is_static,
            'is_unrealistic': not is_realistic,
        })
    else:
        correct.append(feat)

# ============================================
# 5. Report
# ============================================

print(f"\nKorrekte Features: {len(correct)}/{len(training_features)}")
print(f"Fehlerhafte Features: {len(mismatches)}/{len(training_features)}")
print(f"Fehlende Features: {len(missing)}/{len(training_features)}")

if missing:
    print("\n" + "-" * 80)
    print("FEHLENDE FEATURES:")
    print("-" * 80)
    for feat in missing[:15]:
        print(f"   • {feat}")
    if len(missing) > 15:
        print(f"   ... und {len(missing) - 15} weitere")

if mismatches:
    print("\n" + "-" * 80)
    print("FEHLERHAFTE FEATURES:")
    print("-" * 80)
    
    static = [m for m in mismatches if m['is_static']]
    unrealistic = [m for m in mismatches if m['is_unrealistic'] and not m['is_static']]
    
    if static:
        print(f"\Statische Platzhalter (~0.0): {len(static)}")
        for m in static[:15]:
            print(f"   • {m['feature']:<35} Erwartet: {m['expected']:>10.4f}  →  Actual: {m['actual']:>10.4f}")
    
    if unrealistic:
        print(f"\nUnrealistische Werte: {len(unrealistic)}")
        for m in unrealistic[:15]:
            print(f"   • {m['feature']:<35} Erwartet: {m['expected']:>10.4f}  →  Actual: {m['actual']:>10.4f}")

# ============================================
# 6. Kategorisierung
# ============================================

print("\n" + "=" * 80)
print("KATEGORISIERUNG")
print("=" * 80)

audio_keywords = ['bpm', 'rms', 'spectral', 'chroma', 'speech']
video_keywords = ['brightness', 'contrast', 'saturation', 'motion', 'scene', 
                  'duration', 'fps', 'resolution', 'width', 'height']
metadata_keywords = ['acct_', 'txt_', 'len_']

audio_missing = [f for f in missing if any(kw in f.lower() for kw in audio_keywords)]
video_missing = [f for f in missing if any(kw in f.lower() for kw in video_keywords)]
metadata_missing = [f for f in missing if any(f.startswith(kw) for kw in metadata_keywords)]

print(f"\n📝 Metadaten-Features (T1): {len(metadata_missing)} fehlen")
print(f"🔊 Audio-Features (T2):     {len(audio_missing)} fehlen")
print(f"📹 Video-Features (T3):     {len(video_missing)} fehlen")

# ============================================
# 7. Zusammenfassung
# ============================================

print("\n" + "=" * 80)
print("ZUSAMMENFASSUNG")
print("=" * 80)

total_issues = len(missing) + len(mismatches)
success_rate = (len(correct) / len(training_features) * 100) if training_features else 0

print(f"\nErfolgsrate: {success_rate:.1f}%")
print(f"Probleme:    {total_issues} von {len(training_features)} Features")

if success_rate >= 95:
    print("\nSEHR GUT! Fast alle Features stimmen überein.")
elif success_rate >= 80:
    print("\nGUT, aber einige Features fehlen noch.")
else:
    print("\nViele Features stimmen nicht überein.")

print("\n" + "=" * 80)