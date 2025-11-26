import { Component, signal, computed, ChangeDetectionStrategy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';

// Interface für die Antwort vom FastAPI Backend
interface PredictionResponse {
  filename: string;
  score: number; // Float zwischen 0.0 und 1.0
  label: string; // "viral" oder "normal"
  note?: string; // Optional, falls das Modell nicht geladen wurde
  features?: Record<string, any>;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  // --- STATE MANAGEMENT ---
  appState = signal<'upload' | 'analyzing' | 'result' | 'error'>('upload');
  selectedFile = signal<File | null>(null);

  // Wir speichern Score und Feedback für die UI
  analysisResult = signal<{
    score: number;
    label: string;
    feedback: string;
    features: { key: string; value: any }[]; // <--- NEU
  } | null>(null);
  errorMessage = signal<string>('');

  fileName = computed(() => this.selectedFile()?.name ?? null);

  // -- Status für den Drag-Effekt ---
  isDragging = signal<boolean>(false);

  // --- API-KONFIGURATION ---
  private http = inject(HttpClient);

  // URL zum lokalen FastAPI Backend
  private backendUrl = 'http://127.0.0.1:8000/predict';

  // --- COMPONENT METHODS ---

  onFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile.set(input.files[0]);
      // Fehler zurücksetzen, falls vorher einer da war
      this.appState.set('upload');
      this.errorMessage.set('');
    }
  }

  analyze(): void {
    const file = this.selectedFile();
    if (!file) return;

    // 1. UI auf Ladezustand setzen
    this.appState.set('analyzing');

    // 2. FormData erstellen
    const formData = new FormData();
    // WICHTIG: Das Backend erwartet 'file' als Parametername
    formData.append('file', file);

    // 3. API Aufruf
    this.http.post<PredictionResponse>(this.backendUrl, formData).subscribe({
      next: (response) => {
        if (response.score === null || response.score === undefined) {
          this.handleError("Das KI-Modell konnte im Backend nicht geladen werden.");
          return;
        }

        const scorePercent = Math.round(response.score * 100);
        const feedbackText = this.generateFeedback(response.label, scorePercent);

        // 3. Features umwandeln (Object -> Array) und sortieren
        let featureList: { key: string; value: any }[] = [];
        if (response.features) {
          featureList = Object.entries(response.features)
            .map(([key, value]) => {
              // Zahlen schön formatieren (max 4 Nachkommastellen)
              let displayValue = value;
              if (typeof value === 'number') {
                displayValue = Math.round(value * 10000) / 10000;
              }
              return { key, value: displayValue };
            })
            .sort((a, b) => a.key.localeCompare(b.key)); // Alphabetisch sortieren
        }

        this.analysisResult.set({
          score: scorePercent,
          label: response.label,
          feedback: feedbackText,
          features: featureList // <--- NEU
        });

        this.appState.set('result');
      },
      error: (err: HttpErrorResponse) => {
        console.error('Upload Fehler:', err);
        let msg = 'Verbindung zum Server fehlgeschlagen.';
        if (err.status === 500) msg = 'Serverfehler bei der Analyse (500).';
        if (err.status === 422) msg = 'Ungültiges Dateiformat (422).';
        this.handleError(msg);
      },
    });
  }

  // --- DRAG & DROP METHODEN ---

  /**
   * Wird gefeuert, wenn eine Datei über die Zone gezogen wird.
   */
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(true);
  }

  /**
   * Wird gefeuert, wenn die Maus die Zone verlässt.
   */
  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);
  }

  /**
   * Wird gefeuert, wenn die Datei losgelassen wird.
   */
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);

    if (event.dataTransfer && event.dataTransfer.files.length > 0) {
      const file = event.dataTransfer.files[0];

      // Prüfen ob es ein Video ist
      if (file.type.startsWith('video/')) {
        this.selectedFile.set(file);
        this.appState.set('upload');
        this.errorMessage.set('');
      } else {
        this.handleError('Bitte nur Videodateien hochladen.');
      }
    }
  }

  /**
   * Hilfsfunktion: Generiert menschenlesbaren Text basierend auf Score/Label
   */
  private generateFeedback(label: string, score: number): string {
    if (label === 'viral') {
      if (score > 90)
        return 'Fantastisch! Die Audio- und Videomerkmale deuten auf extrem hohes virales Potenzial hin.';
      return 'Sehr gut! Dein Video zeigt starke Merkmale erfolgreicher Inhalte. Gute Chancen auf hohe Reichweite.';
    } else {
      if (score > 40)
        return 'Solide Basis, aber noch Luft nach oben. Versuche, den Einstieg dynamischer zu gestalten oder trendigere Musik zu nutzen.';
      return 'Das Video wirkt eher ruhig. Für mehr Viralität empfehlen wir schnellere Schnitte, hellere Beleuchtung oder energiereichere Musik.';
    }
  }

  private handleError(msg: string): void {
    this.errorMessage.set(msg);
    this.appState.set('error');
  }

  reset(): void {
    this.appState.set('upload');
    this.selectedFile.set(null);
    this.analysisResult.set(null);
    this.errorMessage.set('');

    const fileInput = document.getElementById('file-upload') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }
}
