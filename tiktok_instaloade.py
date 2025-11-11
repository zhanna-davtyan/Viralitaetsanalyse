#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Direkter Download: Top 100 + Normal 100
Automatischer Download von TikTok ohne vorhandene Videos
"""

import yt_dlp
import json
import random
import time
from pathlib import Path
from datetime import datetime
import re

class TikTokDirectDownloader:
    def __init__(self, output_dir="tiktok_100_vs_100"):
        self.output_dir = Path(output_dir)
        self.top_dir = self.output_dir / "Top_100"
        self.normal_dir = self.output_dir / "Normal_100"
        
        self.top_dir.mkdir(parents=True, exist_ok=True)
        self.normal_dir.mkdir(parents=True, exist_ok=True)
        
        self.top_metadata = []
        self.normal_metadata = []
    
    def get_user_videos_info(self, username, max_videos=50):
        """
        Video-Informationen von einem TikTok-Benutzer abrufen
        """
        url = f'https://www.tiktok.com/@{username}'
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'playlistend': max_videos,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"    Lade Informationen von @{username}...")
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    videos = list(info['entries'])[:max_videos]
                    print(f"    ✓ {len(videos)} Videos gefunden")
                    return videos
                return []
        except Exception as e:
            print(f"    ✗ Fehler bei @{username}: {e}")
            return []
    
    def download_top_100(self, popular_users):
        """
        Top 100: Die viralsten Videos von beliebten TikTokern
        """
        print("=" * 60)
        print("PHASE 1: TOP 100 VIRALE VIDEOS")
        print("=" * 60)
        print(f"\nStrategie: Videos von {len(popular_users)} beliebten TikTokern sammeln")
        print("           und die 100 mit höchstem Engagement auswählen\n")
        
        all_videos = []
        
        # Schritt 1: Video-Informationen sammeln
        print("📊 Schritt 1/3: Video-Informationen sammeln\n")
        
        for idx, username in enumerate(popular_users, 1):
            print(f"  [{idx}/{len(popular_users)}] @{username}")
            
            videos = self.get_user_videos_info(username, max_videos=20)
            
            for video in videos:
                likes = video.get('like_count', 0) or 0
                comments = video.get('comment_count', 0) or 0
                views = video.get('view_count', 0) or 0
                
                video['engagement_score'] = likes + (comments * 2)
                video['engagement_rate'] = (likes + comments) / views if views > 0 else 0
                all_videos.append(video)
            
            # Verzögerung zwischen Benutzern
            time.sleep(random.uniform(2, 4))
        
        print(f"\n✓ Insgesamt {len(all_videos)} Videos gesammelt")
        
        if len(all_videos) == 0:
            print("\n❌ Keine Videos gefunden. Abbruch.")
            return 0
        
        # Schritt 2: Top 100 nach Engagement auswählen
        print("\n🔥 Schritt 2/3: Nach Engagement sortieren\n")
        
        sorted_videos = sorted(
            all_videos,
            key=lambda x: x['engagement_score'],
            reverse=True
        )
        
        top_100 = sorted_videos[:100]
        
        # Top 10 anzeigen
        print("Top 10 Videos (höchstes Engagement):")
        for i, video in enumerate(top_100[:10], 1):
            likes = video.get('like_count', 0)
            comments = video.get('comment_count', 0)
            author = video.get('uploader_id', 'unknown')
            print(f"  {i:2d}. {likes:>10,} Likes | {comments:>8,} Komm. | @{author}")
        
        # Schritt 3: Videos herunterladen
        print(f"\n⏬ Schritt 3/3: Download der Top 100 Videos\n")
        print("Dies kann 30-60 Minuten dauern...\n")
        
        downloaded = self._download_videos(
            top_100,
            self.top_dir,
            "top",
            self.top_metadata
        )
        
        print(f"\n✅ Top_100: {downloaded} Videos heruntergeladen")
        return downloaded
    
    def download_normal_100(self, popular_users):
        """
        Normal 100: Zufällige normale Videos mit niedrigem Engagement
        """
        print("\n" + "=" * 60)
        print("PHASE 2: NORMAL 100 VIDEOS")
        print("=" * 60)
        print(f"\nStrategie: Videos sammeln und 100 mit niedrigem Engagement auswählen\n")
        
        all_videos = []
        
        # Schritt 1: Mehr Videos sammeln
        print("📊 Schritt 1/3: Video-Informationen sammeln\n")
        
        for idx, username in enumerate(popular_users, 1):
            print(f"  [{idx}/{len(popular_users)}] @{username}")
            
            videos = self.get_user_videos_info(username, max_videos=20)
            
            for video in videos:
                likes = video.get('like_count', 0) or 0
                comments = video.get('comment_count', 0) or 0
                views = video.get('view_count', 0) or 0
                
                video['engagement_score'] = likes + (comments * 2)
                video['engagement_rate'] = (likes + comments) / views if views > 0 else 0
                all_videos.append(video)
            
            time.sleep(random.uniform(2, 4))
        
        print(f"\n✓ Insgesamt {len(all_videos)} Videos gesammelt")
        
        if len(all_videos) == 0:
            print("\n❌ Keine Videos gefunden. Abbruch.")
            return 0
        
        # Schritt 2: Normale Videos auswählen
        print("\n📊 Schritt 2/3: Normale Videos auswählen\n")
        
        # Nach Engagement sortieren (niedrigste zuerst)
        sorted_videos = sorted(
            all_videos,
            key=lambda x: x['engagement_score']
        )
        
        # Strategie: Untere 10-50% auswählen
        total = len(sorted_videos)
        start_idx = int(total * 0.1)
        end_idx = int(total * 0.5)
        
        candidates = sorted_videos[start_idx:end_idx]
        
        print(f"Kandidaten-Pool: {len(candidates)} Videos")
        print(f"  (Von {start_idx} bis {end_idx} in Engagement-Ranking)")
        
        # Zufällig 100 auswählen
        if len(candidates) >= 100:
            selected = random.sample(candidates, 100)
        else:
            selected = candidates
            print(f"\n⚠️  Nur {len(selected)} Videos verfügbar")
        
        # Statistiken
        avg_likes = sum(v.get('like_count', 0) for v in selected) / len(selected)
        print(f"\nNormal_100 Durchschnitt:")
        print(f"  • Likes: {avg_likes:,.0f}")
        
        # Untere 10 anzeigen
        selected_sorted = sorted(selected, key=lambda x: x['engagement_score'])
        print(f"\nUntere 10 Videos (niedrigstes Engagement):")
        for i, video in enumerate(selected_sorted[:10], 1):
            likes = video.get('like_count', 0)
            comments = video.get('comment_count', 0)
            author = video.get('uploader_id', 'unknown')
            print(f"  {i:2d}. {likes:>10,} Likes | {comments:>8,} Komm. | @{author}")
        
        # Schritt 3: Videos herunterladen
        print(f"\n⏬ Schritt 3/3: Download der Normal 100 Videos\n")
        print("Dies kann 30-60 Minuten dauern...\n")
        
        downloaded = self._download_videos(
            selected,
            self.normal_dir,
            "normal",
            self.normal_metadata
        )
        
        print(f"\n✅ Normal_100: {downloaded} Videos heruntergeladen")
        return downloaded
    
    def _download_videos(self, videos, save_dir, prefix, metadata_list):
        """
        Videos herunterladen (gemeinsame Funktion)
        """
        downloaded_count = 0
        
        for idx, video in enumerate(videos, 1):
            try:
                video_url = video.get('webpage_url') or video.get('url')
                
                if not video_url:
                    print(f"  [{idx}/{len(videos)}] ✗ Keine URL")
                    continue
                
                likes = video.get('like_count', 0)
                comments = video.get('comment_count', 0)
                author = video.get('uploader_id', 'unknown')
                video_id = video.get('id', f'vid_{idx}')
                
                print(f"  [{idx}/{len(videos)}] Download...")
                print(f"    @{author} | {likes:,} Likes | {comments:,} Komm.")
                
                # Download mit yt-dlp
                filename = f'{prefix}_{idx}_likes_{likes}_id_{video_id}'
                
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': str(save_dir / f'{filename}.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Metadaten speichern
                metadata = {
                    'rank': idx,
                    'group': prefix,
                    'video_id': video_id,
                    'uploader': author,
                    'likes': likes,
                    'comments': comments,
                    'views': video.get('view_count', 0),
                    'shares': video.get('repost_count', 0),
                    'engagement_score': video.get('engagement_score', 0),
                    'title': video.get('title', '')[:200],
                    'duration': video.get('duration', 0),
                }
                metadata_list.append(metadata)
                
                downloaded_count += 1
                print(f"    ✓ Erfolgreich ({downloaded_count}/{len(videos)})")
                
                # Verzögerung zwischen Downloads
                time.sleep(random.uniform(8, 15))
                
            except Exception as e:
                print(f"    ✗ Fehler: {e}")
                time.sleep(5)
                continue
        
        return downloaded_count
    
    def save_metadata_and_report(self):
        """Metadaten und Bericht speichern"""
        
        # Top_100 Metadaten
        if self.top_metadata:
            top_file = self.top_dir / "top_metadata.json"
            with open(top_file, 'w', encoding='utf-8') as f:
                json.dump(self.top_metadata, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Top_100 Metadaten: {top_file}")
        
        # Normal_100 Metadaten
        if self.normal_metadata:
            normal_file = self.normal_dir / "normal_metadata.json"
            with open(normal_file, 'w', encoding='utf-8') as f:
                json.dump(self.normal_metadata, f, ensure_ascii=False, indent=2)
            print(f"✓ Normal_100 Metadaten: {normal_file}")
        
        # Vergleichsbericht
        if self.top_metadata and self.normal_metadata:
            self._generate_report()
    
    def _generate_report(self):
        """Vergleichsbericht erstellen"""
        
        top_likes = [v['likes'] for v in self.top_metadata]
        normal_likes = [v['likes'] for v in self.normal_metadata]
        
        top_avg = sum(top_likes) / len(top_likes)
        normal_avg = sum(normal_likes) / len(normal_likes)
        ratio = top_avg / normal_avg if normal_avg > 0 else 0
        
        print("\n" + "=" * 60)
        print("VERGLEICHSBERICHT")
        print("=" * 60)
        
        print(f"\n📊 TOP_100:")
        print(f"  • Videos: {len(self.top_metadata)}")
        print(f"  • Durchschn. Likes: {top_avg:,.0f}")
        print(f"  • Höchste: {max(top_likes):,}")
        print(f"  • Niedrigste: {min(top_likes):,}")
        
        print(f"\n📊 NORMAL_100:")
        print(f"  • Videos: {len(self.normal_metadata)}")
        print(f"  • Durchschn. Likes: {normal_avg:,.0f}")
        print(f"  • Höchste: {max(normal_likes):,}")
        print(f"  • Niedrigste: {min(normal_likes):,}")
        
        print(f"\n📈 UNTERSCHIED:")
        print(f"  • Verhältnis: {ratio:.2f}x")
        print(f"  • Top_100 hat {ratio:.1f}x mehr Likes")
        
        print("=" * 60)
        
        # Bericht speichern
        report_file = self.output_dir / "vergleichsbericht.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"TikTok Datensatz Vergleich\n")
            f.write(f"Erstellt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Top_100:\n")
            f.write(f"  Videos: {len(self.top_metadata)}\n")
            f.write(f"  Durchschn. Likes: {top_avg:,.0f}\n\n")
            f.write(f"Normal_100:\n")
            f.write(f"  Videos: {len(self.normal_metadata)}\n")
            f.write(f"  Durchschn. Likes: {normal_avg:,.0f}\n\n")
            f.write(f"Verhältnis: {ratio:.2f}x\n")
        
        print(f"\n✓ Bericht gespeichert: {report_file}")

def main():
    print("=" * 60)
    print("TikTok Direkter Download: Top 100 + Normal 100")
    print("=" * 60)
    
    # Beliebte TikTok-Benutzer (verifiziert, hohe Aktivität)
    popular_users = [
        # Mega-Stars (über 100M Follower)
        "khaby.lame",        # 162M - Comedy
        "charlidamelio",     # 155M - Tanz
        "bellapoarch",       # 94M - Musik
        
        # Top-Creator (50-100M Follower)
        "addisonre",         # 88M - Tanz/Lifestyle
        "zachking",          # 82M - Magie
        "willsmith",         # 73M - Entertainment
        "kimberly.loaiza",   # 67M - Musik
        
        # Beliebte Creator (20-50M Follower)
        "dixiedamelio",      # 57M - Tanz
        "jasonderulo",       # 58M - Musik
        "spencerx",          # 56M - Beatbox/Musik
        "lorengray",         # 54M - Musik/Mode
        "domelipa",          # 59M - Tanz
        
        # Virale Creator (10-20M Follower)
        "avani",             # 42M - Beauty/Lifestyle
        "jamescharles",      # 38M - Beauty
        "brentrivera",       # 47M - Comedy
        "babyariel",         # 36M - Entertainment
        
        # Zusätzliche Creator für mehr Vielfalt
        "thehypehouse",      # 21M - Kollaboration
        "riyaz.14",          # 45M - Mode/Lifestyle
        "tiktok",            # Offiziell
        "therock",           # 76M - Entertainment
    ]
    
    print(f"\n📋 {len(popular_users)} Beliebte TikToker ausgewählt")
    print("💡 Strategie:")
    print("  1. Von jedem ~20 Videos sammeln (insgesamt ~400)")
    print("  2. Top 100 nach Engagement auswählen")
    print("  3. Normal 100 aus mittlerem/unterem Bereich auswählen")
    
    print("\n⏱️  Geschätzte Dauer: 1-2 Stunden")
    print("⚠️  Wichtig: Stabile Internetverbindung erforderlich")
    
    confirm = input("\nMöchten Sie fortfahren? (j/n): ").strip().lower()
    
    if confirm != 'j':
        print("Abgebrochen.")
        return
    
    downloader = TikTokDirectDownloader()
    
    # Phase 1: Top 100
    print("\n" + "=" * 60)
    print("START")
    print("=" * 60)
    
    top_count = downloader.download_top_100(popular_users)
    
    if top_count == 0:
        print("\n❌ Fehler bei Top_100. Abbruch.")
        return
    
    # Phase 2: Normal 100
    normal_count = downloader.download_normal_100(popular_users)
    
    if normal_count == 0:
        print("\n❌ Fehler bei Normal_100. Abbruch.")
        return
    
    # Metadaten und Bericht
    downloader.save_metadata_and_report()
    
    # Abschluss
    print("\n" + "=" * 60)
    print("🎉 ERFOLGREICH ABGESCHLOSSEN!")
    print("=" * 60)
    print(f"\n📁 Datensatz: {downloader.output_dir}/")
    print(f"  • Top_100/     → {top_count} virale Videos")
    print(f"  • Normal_100/  → {normal_count} normale Videos")
    print(f"\n✅ Gesamt: {top_count + normal_count} Videos")
    print("=" * 60)

if __name__ == "__main__":
    main()