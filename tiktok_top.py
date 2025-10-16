#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Top 200 Viral Videos Downloader
Download der 200 beliebtesten Videos (nach Likes und Kommentaren) für Forschungsanalyse
"""

import yt_dlp
import json
import random
import time
from pathlib import Path
from datetime import datetime

class TikTokTop200Downloader:
    def __init__(self, save_dir="tiktok_top_200"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self.metadata_list = []
        
    def get_video_info(self, url):
        """Video-Informationen abrufen ohne Download"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except:
            return None
    
    def download_from_multiple_users(self, usernames, videos_per_user=20):
        """
        Videos von mehreren beliebten Benutzern herunterladen und genügend Samples sammeln
        """
        print("=" * 60)
        print("TikTok Top 200 Viral Videos Downloader")
        print("=" * 60)
        print(f"Ziel: 200 Videos von {len(usernames)} beliebten TikTokern")
        print(f"Pro Benutzer: ~{videos_per_user} Videos\n")
        
        all_videos_info = []
        
        # Schritt 1: Alle Video-Informationen sammeln
        print("📊 Schritt 1/3: Video-Informationen sammeln...\n")
        
        for idx, username in enumerate(usernames, 1):
            print(f"[{idx}/{len(usernames)}] Sammle Videos von @{username}...")
            
            try:
                videos = self._get_user_videos_info(username, videos_per_user)
                all_videos_info.extend(videos)
                print(f"  ✓ {len(videos)} Videos gefunden")
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                print(f"  ✗ Fehler: {e}")
                continue
        
        print(f"\n✓ Insgesamt {len(all_videos_info)} Videos gesammelt")
        
        # Schritt 2: Nach Engagement-Rate sortieren (Likes + Kommentare)
        print("\n🔥 Schritt 2/3: Nach Engagement sortieren...\n")
        
        # Engagement-Score berechnen: likes + comments * 2 (Kommentare haben höheres Gewicht)
        for video in all_videos_info:
            likes = video.get('like_count', 0) or 0
            comments = video.get('comment_count', 0) or 0
            video['engagement_score'] = likes + (comments * 2)
        
        # Sortieren
        sorted_videos = sorted(
            all_videos_info, 
            key=lambda x: x['engagement_score'], 
            reverse=True
        )
        
        # Top 10 anzeigen
        print("Top 10 Videos nach Engagement:")
        for i, video in enumerate(sorted_videos[:10], 1):
            print(f"  {i}. Likes: {video.get('like_count', 0):,} | "
                  f"Kommentare: {video.get('comment_count', 0):,} | "
                  f"@{video.get('uploader_id', 'unbekannt')}")
        
        # Schritt 3: Top 200 herunterladen
        print(f"\n⏬ Schritt 3/3: Download der Top 200 Videos...\n")
        
        top_200 = sorted_videos[:200]
        downloaded_count = 0
        
        for idx, video in enumerate(top_200, 1):
            try:
                print(f"\n[{idx}/200] Download startet...")
                print(f"  - Autor: @{video.get('uploader_id', 'unbekannt')}")
                print(f"  - Likes: {video.get('like_count', 0):,}")
                print(f"  - Kommentare: {video.get('comment_count', 0):,}")
                print(f"  - Aufrufe: {video.get('view_count', 0):,}")
                
                # Video herunterladen
                video_url = video.get('webpage_url') or video.get('url')
                
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': str(self.save_dir / f'top_{idx}_likes_{video.get("like_count", 0)}_%(id)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Metadaten speichern
                metadata = {
                    'rank': idx,
                    'video_id': video.get('id'),
                    'uploader': video.get('uploader_id'),
                    'likes': video.get('like_count', 0),
                    'comments': video.get('comment_count', 0),
                    'views': video.get('view_count', 0),
                    'shares': video.get('repost_count', 0),
                    'engagement_score': video['engagement_score'],
                    'title': video.get('title', '')[:200],
                    'duration': video.get('duration', 0),
                    'upload_date': video.get('upload_date'),
                }
                self.metadata_list.append(metadata)
                
                downloaded_count += 1
                print(f"  ✓ Erfolgreich ({downloaded_count}/200)")
                
                # Verzögerung zur Vermeidung von Einschränkungen
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                print(f"  ✗ Fehler: {e}")
                time.sleep(5)
                continue
        
        # Metadaten speichern
        self._save_metadata()
        
        print("\n" + "=" * 60)
        print(f"✓ Download abgeschlossen! {downloaded_count} Videos gespeichert")
        print("=" * 60)
        
        return downloaded_count
    
    def _get_user_videos_info(self, username, count):
        """Benutzer-Video-Informationen abrufen"""
        url = f'https://www.tiktok.com/@{username}'
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'playlistend': count,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
            
            if 'entries' in playlist_info:
                return list(playlist_info['entries'])[:count]
            return []
    
    def _save_metadata(self):
        """Metadaten und Statistiken speichern"""
        if not self.metadata_list:
            return
        
        # JSON speichern
        metadata_file = self.save_dir / "top_200_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata_list, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Metadaten gespeichert: {metadata_file}")
        
        # Statistikbericht erstellen
        self._generate_report()
    
    def _generate_report(self):
        """Detaillierten Statistikbericht erstellen"""
        if not self.metadata_list:
            return
        
        print("\n" + "=" * 60)
        print("STATISTIKBERICHT - Top 200 Virale TikTok Videos")
        print("=" * 60)
        
        total_likes = sum(v['likes'] for v in self.metadata_list)
        total_comments = sum(v['comments'] for v in self.metadata_list)
        total_views = sum(v['views'] for v in self.metadata_list)
        count = len(self.metadata_list)
        
        print(f"\n📊 Gesamtstatistiken:")
        print(f"  • Heruntergeladene Videos: {count}")
        print(f"  • Gesamt-Likes: {total_likes:,}")
        print(f"  • Gesamt-Kommentare: {total_comments:,}")
        print(f"  • Gesamt-Aufrufe: {total_views:,}")
        
        print(f"\n📈 Durchschnittswerte:")
        print(f"  • Durchschn. Likes: {total_likes/count:,.0f}")
        print(f"  • Durchschn. Kommentare: {total_comments/count:,.0f}")
        print(f"  • Durchschn. Aufrufe: {total_views/count:,.0f}")
        
        print(f"\n🏆 Extremwerte:")
        print(f"  • Höchste Likes: {max(v['likes'] for v in self.metadata_list):,}")
        print(f"  • Niedrigste Likes: {min(v['likes'] for v in self.metadata_list):,}")
        print(f"  • Höchste Kommentare: {max(v['comments'] for v in self.metadata_list):,}")
        
        # Top 5 Content-Creators
        from collections import Counter
        creators = [v['uploader'] for v in self.metadata_list]
        top_creators = Counter(creators).most_common(5)
        
        print(f"\n👥 Top 5 Content-Creators:")
        for i, (creator, count) in enumerate(top_creators, 1):
            print(f"  {i}. @{creator}: {count} Videos")
        
        print("=" * 60)
        
        # Bericht in Datei speichern
        report_file = self.save_dir / "analysis_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"TikTok Top 200 Analyse-Bericht\n")
            f.write(f"Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\nVideos: {count}\n")
            f.write(f"Gesamt-Likes: {total_likes:,}\n")
            f.write(f"Gesamt-Kommentare: {total_comments:,}\n")
        
        print(f"\n✓ Bericht gespeichert: {report_file}")

def main():
    print("=" * 60)
    print("TikTok Top 200 Viral Videos Downloader")
    print("Für DBSCAN und K-Means Clustering-Analyse")
    print("=" * 60)
    
    # Liste der beliebten TikTok-Benutzer (verifizierte High-Engagement-Accounts)
    top_tiktokers = [
        "khaby.lame",        # Comedy
        "charlidamelio",     # Tanz
        "zachking",          # Magie/Effekte
        "bellapoarch",       # Musik
        "addisonre",         # Tanz/Lifestyle
        "willsmith",         # Unterhaltung
        "kimberly.loaiza",   # Musik
        "domelipa",          # Tanz
        "spencerx",          # Musik/Comedy
        "jasonderulo",       # Musik
        "dixiedamelio",      # Tanz
        "lorengray",         # Musik/Mode
        "babyariel",         # Unterhaltung
        "riyaz.14",          # Mode
        "avani",             # Beauty
        "thehypehouse",      # Kollaborative Inhalte
        "jamescharles",      # Beauty
        "brentrivera",       # Comedy
        "tiktok",            # Offiziell
        "therock",           # Unterhaltung
    ]
    
    print("\n📋 Ausgewählte TikTok-Creator (Top 20):")
    for i, user in enumerate(top_tiktokers, 1):
        print(f"  {i}. @{user}")
    
    print("\n💡 Strategie:")
    print("  1. Von jedem Creator ~15-20 Videos sammeln")
    print("  2. Nach Likes + Kommentaren sortieren")
    print("  3. Top 200 Videos herunterladen")
    
    confirm = input("\nMöchten Sie fortfahren? (j/n): ").strip().lower()
    
    if confirm != 'j':
        print("Abgebrochen.")
        return
    
    downloader = TikTokTop200Downloader()
    
    # 15 Videos pro Benutzer, 20 Benutzer = 300 Videos, dann Top 200 auswählen
    videos_per_user = 15
    
    print("\n⏳ Download startet...")
    print("Dies kann 1-2 Stunden dauern (mit Pausen zur Vermeidung von Sperrungen)\n")
    
    downloaded = downloader.download_from_multiple_users(
        top_tiktokers, 
        videos_per_user=videos_per_user
    )
    
    print("\n" + "=" * 60)
    print("FERTIG!")
    print("=" * 60)
    print(f"✓ {downloaded} Videos für Ihre Analyse bereit")
    print(f"✓ Gespeichert in: {downloader.save_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()