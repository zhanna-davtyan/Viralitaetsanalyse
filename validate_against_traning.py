#!/usr/bin/env python3
"""
Validierung: Vergleich der neuen Features mit den Trainings-Features
"""

import pandas as pd
from pathlib import Path
from feature_extractor import extract_features

print("=" * 60)
print(" Feature-Abgleich Validierung")
print("=" * 60)

# ============================================
# 1. Trainings-Feature laden
# ============================================

# Trainings-Feature-Matrix Datei laden
training_file = Path("features/FINAL_FEATURE_MATRIX.csv")

if not training_file.exists():
    print(f" Trainings-Feature-Datei nicht gefunden: {training_file}")
    exit(1)

df_train = pd.read_csv(training_file)

# Nicht-Feature-Spalten entfernen
non_feature_cols = ['video_id', 'is_viral', 'group', 'author']
training_features = [col for col in df_train.columns if col not in non_feature_cols]

print(f"\n Trainings-Features: {len(training_features)}")

# ============================================
# 2. Features aus neuem Video extrahieren
# ============================================

test_video = "test_videos/test_normal_7544548353590250758.mp4"

if not Path(test_video).exists():
    print(f" Test Video nicht gefunden: {test_video}")
    exit(1)

new_features = extract_features(test_video)
new_feature_names = list(new_features.keys())

print(f"Neue Features: {len(new_feature_names)}")

# ============================================
# 3. Vergleich
# ============================================

print("\n" + "=" * 60)
print(" Feature-Vergleich")
print("=" * 60)

# Fehlende Features (im Training vorhanden, in neuer Extraktion nicht)
missing = set(training_features) - set(new_feature_names)
if missing:
    print(f"\n Fehlende Features ({len(missing)}):")
    for f in sorted(missing):
        print(f"   - {f}")
else:
    print("\n Keine fehlenden Features")

# Zusätzliche Features (in neuer Extraktion vorhanden, im Training nicht)
extra = set(new_feature_names) - set(training_features)
if extra:
    print(f"\n Zusätzliche Features ({len(extra)}):")
    for f in sorted(extra):
        print(f"- {f}")
else:
    print("\n Keine zusätzlichen Features")

# ============================================
# 4. Zusammenfassung
# ============================================

print("\n" + "=" * 60)
print(" Zusammenfassung")
print("=" * 60)

match_rate = len(set(training_features) & set(new_feature_names)) / len(training_features) * 100

print(f"   Trainings-Features: {len(training_features)}")
print(f"   Neue Features:      {len(new_feature_names)}")
print(f"   Übereinstimmung:    {match_rate:.1f}%")

if match_rate == 100 and len(extra) == 0:
    print("\n Übereinstimmung! Code ist bereit für Backend!")
elif match_rate >= 95:
    print("\n Grundsätzliche Übereinstimmung. Fehlende/zusätzliche Features prüfen.")
else:
    print("\n Unzureichende Übereinstimmung. feature_extractor.py muss korrigiert werden.")

# ============================================
# 5. Korrekturvorschläge generieren
# ============================================

if missing:
    print("\n" + "=" * 60)
    print(" Korrekturvorschläge")
    print("=" * 60)
    
    print("\nFolgende Features in feature_extractor.py hinzufügen:")
    for f in sorted(missing)[:10]:
        print(f"   features['{f}'] = 0.0  # TODO: Extraktion implementieren")
    
    if len(missing) > 10:
        print(f"   ... insgesamt {len(missing)} fehlende Features")