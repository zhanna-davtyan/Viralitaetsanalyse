#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TikTok testvideos Download: 15 Normal + 15 Top
Automatischer Download von TikTok für Independent Test Set
"""

import yt_dlp
import json
import random
import time
from pathlib import Path
from datetime import datetime
import re

class TikTokTestDownloader:
    def __init__(self, output_dir="test_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata = []
        
    def get_user_videos_info(self, username, max_videos=2):
        """
        Video-Informationen von einem TikTok-Benutzer abrufen
        Nur die neuesten 2 Videos pro User (für Diversität)
        """
        url = f'https://www.tiktok.com/@{username}'
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Nur Metadaten, kein Download
            'playlistend': max_videos,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info and 'entries' in info:
                    return info['entries']
                return []
        except Exception as e:
            print(f"   ✗ Fehler bei @{username}: {str(e)[:80]}")
            return []
    
    def download_video(self, video_url, video_id, group):
        """
        Einzelnes Video herunterladen
        """
        filename = f"test_{group}_{video_id}"
        output_template = str(self.output_dir / f"{filename}.%(ext)s")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                
                # Metadaten extrahieren
                metadata = {
                    'video_id': video_id,
                    'group': group,
                    'is_viral': 1 if group == 'top' else 0,
                    'url': video_url,
                    'author': info.get('uploader', 'unknown'),
                    'likes': info.get('like_count', 0),
                    'views': info.get('view_count', 0),
                    'comments': info.get('comment_count', 0),
                    'shares': info.get('repost_count', 0),
                    'description': info.get('description', '')[:200],
                    'download_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                return metadata
        except Exception as e:
            print(f"   ✗ Download fehlgeschlagen: {str(e)[:80]}")
            return None
    
    def scrape_from_users(self, users, group, target_count):
        """
        Von User-Liste Videos sammeln
        
        Args:
            users: Liste von TikTok Benutzernamen
            group: 'normal' oder 'top'
            target_count: Ziel-Anzahl Videos
        """
        print(f"\n{'='*60}")
        print(f"🔍 SCRAPING {group.upper()} USERS")
        print(f"{'='*60}")
        
        collected = []
        
        for i, username in enumerate(users, 1):
            if len(collected) >= target_count:
                break
            
            print(f"\n[{i}/{len(users)}] @{username}...")
            
            # Video-Infos abrufen
            videos = self.get_user_videos_info(username, max_videos=2)
            
            if not videos:
                print(f"   ⏭️ Keine Videos gefunden")
                continue
            
            # Erstes passendes Video herunterladen
            for video in videos:
                if len(collected) >= target_count:
                    break
                
                try:
                    video_id = video.get('id', '')
                    video_url = video.get('url', f"https://www.tiktok.com/@{username}/video/{video_id}")
                    
                    # Likes prüfen (falls verfügbar)
                    likes = video.get('like_count', 0)
                    
                    # Filter nach Gruppe
                    if group == 'normal' and likes > 10000:
                        print(f"   ⏭️ Video {video_id}: Zu viele Likes ({likes:,})")
                        continue
                    
                    if group == 'top' and likes < 400000 and likes > 0:
                        print(f"   ⏭️ Video {video_id}: Zu wenig Likes ({likes:,})")
                        continue
                    
                    # Download
                    print(f"   🔄 Downloading {video_id}...")
                    metadata = self.download_video(video_url, video_id, group)
                    
                    if metadata:
                        collected.append(metadata)
                        self.metadata.append(metadata)
                        print(f"   ✓ [{len(collected)}/{target_count}] Success! "
                              f"{metadata['likes']:,} Likes | @{metadata['author']}")
                        break  # Nur 1 Video pro User
                    
                except Exception as e:
                    print(f"   ✗ Fehler: {str(e)[:80]}")
                    continue
            
            # Pause zwischen Users
            time.sleep(random.uniform(2, 4))
        
        return collected
    
    def save_metadata(self, filename="test_metadata.csv"):
        """
        Metadaten als CSV speichern
        """
        import pandas as pd
        
        if self.metadata:
            df = pd.DataFrame(self.metadata)
            output_file = self.output_dir / filename
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"\n💾 Metadaten gespeichert: {output_file}")
            return df
        return None


# USER-LISTEN (JUST FOR TEST - NICHT IN TRAINING SET!)


# WICHTIG: Diese User dürfen NICHT im Training-Set sein!
TEST_USERS = {
    'normal': [
    # Lernen / Bildung
    'collegelife',               # Lern-Community
    'studyblr',                  
    'studymotivation',          
    'academicweapon',         
    'studywithinspo',          # Lerninspiration
    
    # Lebensstil
    'minimalist.aesthetic',    # Minimalistische Ästhetik
    'tidynest',                # Ordentliches Zuhause
    'apartmenttherapy',        # Wohnungs-Therapie
    'plantparentcommunity',    # Pflanzenliebhaber
    'frugalliving',            # Sparsames Leben
    
    # DIY / Handwerk
    'craftedwithlove',         # Handgemacht mit Liebe
    'stitchingtime',           # Stickzeit
    
    # Kochen
    'budgeteats',              # Günstige Mahlzeiten
    'quickmealsideas',         # Schnelle Gerichte
    'healthyrecipe',           # Gesunde Rezepte
    
   ],
    'top': [
    # Sportstars (nicht im Trainingsdatensatz)
    'cristiano',               # Cristiano Ronaldo (62 Mio. Follower)
    'leomessi',                # Lionel Messi (35 Mio.)
    'neymarjr',                # Neymar (30 Mio.)
    'kingjames',               # LeBron James (15 Mio.)
    'stephencurry30',          # Stephen Curry (12 Mio.)
    
    # Sänger / Musiker (nicht im Trainingsdatensatz)
    'selenagomez',             # Selena Gomez (60 Mio.)
    'justinbieber',            # Justin Bieber (25 Mio.)
    'arianagrande',            # Ariana Grande (36 Mio.)
    'billieeilish',            # Billie Eilish (10 Mio.)
    'shakira',                 # Shakira (31 Mio.)
    'bts.bighitofficial',      # Musik / Idolgruppe / Südkorea
    
    # Köche / Essen (nicht im Trainingsdatensatz)
    'gordonramsayofficial',    # Gordon Ramsay (35 Mio.)
    'chef.aaron',              # Koch Aaron (8 Mio.)
    'cznburak',                # Koch / Türkei / virale Rezepte
    
    # Humor
    'williesalim',             # Humor / virale Videos
    
    # Marken / Offizielle Accounts (nicht im Trainingsdatensatz)
    'nba',                     # Offizieller NBA-Account (20 Mio.)
    'netflix',                 # Netflix (27 Mio.)
    'nasa',                    # NASA (6 Mio.)
]
}

def main():
    print("=" * 60)
    print("🎬 TikTok Test Set Downloader")
    print("=" * 60)
    print(f"\nZiel: 15 Normal + 15 Top Videos")
    print(f"Methode: Identisch zum Training-Set Download\n")
    
    # Downloader initialisieren
    downloader = TikTokTestDownloader(output_dir="test_videos")
    
 
    # 1. Normal Videos sammeln

    print("\n" + "="*60)
    print("PHASE 1: NORMAL VIDEOS")
    print("="*60)
    
    normal_videos = downloader.scrape_from_users(
        users=TEST_USERS['normal'],
        group='normal',
        target_count=15
    )
    
    print(f"\n✓ Normal Videos gesammelt: {len(normal_videos)}/15")
    
    # Pause zwischen Phasen
    print("\n Pause 10 Sekunden...")
    time.sleep(10)
    
    # ============================================
    # 2. Top Videos sammeln
    # ============================================
    print("\n" + "="*60)
    print(" PHASE 2: TOP VIDEOS")
    print("="*60)
    
    top_videos = downloader.scrape_from_users(
        users=TEST_USERS['top'],
        group='top',
        target_count=15
    )
    
    print(f"\n✓ Top Videos gesammelt: {len(top_videos)}/15")
    
    # ============================================
    # Metadaten speichern
    # ============================================
    # print("\n" + "="*60)
    # print("💾 SPEICHERE METADATEN")
    # print("="*60)
    
    # df = downloader.save_metadata()
    
    # ============================================
    # 4. Finale Statistik
    # ============================================
    print("\n" + "="*60)
    print("FINALE STATISTIK")
    print("="*60)
    
    total = len(normal_videos) + len(top_videos)
    
    print(f"\n Erfolgreich heruntergeladen:")
    print(f"   - Normal: {len(normal_videos)}/15")
    print(f"   - Top:    {len(top_videos)}/15")
    print(f"   - Gesamt: {total}/30")
    
    if total >= 30:
        print(f"\nERFOLG! Alle 30 Test-Videos heruntergeladen!")
    elif total >= 25:
        print(f"\n Fast geschafft! Noch {30-total} Videos fehlen.")
        print(f"   Fügen Sie mehr Benutzer hinzu und führen Sie erneut aus.")
    else:
        print(f"\n NEIN！ Nur {total} Videos heruntergeladen.")
        print(f"   Überprüfen Sie die Benutzernamen und versuchen Sie es erneut.")
    
    # if df is not None:
    #   print(f"\n Durchschnittliche Likes:")
    #   print(f"   Normal: {df[df['group']=='normal']['likes'].mean():,.0f}")
     #   print(f"   Top:    {df[df['group']=='top']['likes'].mean():,.0f}")
    #print("\n" + "="*60)
    #print(" DOWNLOAD ABGESCHLOSSEN")
    #print("="*60)
    
    #print("\n Nächste Schritte:")
    #print("   1. Informiere T2: Audio-Features extrahieren")
    #print("   2. Informiere T3: Video-Features extrahieren")
    #print("   3. Führe test_independent_set.ipynb aus")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Download abgebrochen durch Benutzer")
    except Exception as e:
        print(f"\n\n Fehler: {str(e)}")