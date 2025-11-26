#  Decoding Virality: Eine algorithmische Analyse von Kurzvideo-Inhalten

**Projektziel:** Dieses Projekt geht über subjektive Spekulationen hinaus, um eine zentrale Frage der modernen digitalen Landschaft zu beantworten: **Was sind die quantifizierbaren Faktoren, die ein Kurzvideo erfolgreich machen?** Wir wenden eine mehrstufige Datenanalyse- und Machine-Learning-Pipeline an, um visuelle Trends zu identifizieren und das Engagement von Videos vorherzusagen.


**ACHTUNG: Kritische Versionsabhängigkeiten!**

Dieses Projekt verwendet Bibliotheken (insbesondere `deepface` und `tensorflow`), die **nicht** mit den neuesten Python-Versionen (wie 3.11+) kompatibel sind.

Die Ausführung erfordert **zwingend Python 3.10.x**.

### Schritt-für-Schritt-Anleitung (macOS)

1.  **Python 3.10 installieren** (falls noch nicht geschehen, z. B. mit Homebrew):
    ```bash
    brew install python@3.10
    ```

2.  **Virtuelles Environment (venv) erstellen:**
    Stelle sicher, dass du im Hauptverzeichnis (`Viralitaetsanalyse/`) bist und führe aus:
    ```bash
    # Erstellt das venv mit Python 3.10
    python3.10 -m venv .venv
    ```

3.  **Environment aktivieren:**
    ```bash
    source .venv/bin/activate
    ```
    *(Dein Terminal-Prompt sollte nun `(.venv)` anzeigen.)*

4.  **Erforderliche Pakete installieren:**
    Dieser Schritt installiert die exakten Versionen, die für die Kompatibilität (insbesondere für Apple Silicon Macs) erforderlich sind.
    ```bash
    # Pip selbst aktualisieren
    pip install --upgrade pip
    
    # TensorFlow 2.11 
    pip install tensorflow-macos==2.11.0
    
    # Exakt passende Numpy-Version
    pip install numpy==1.24.4
    
    # Der Rest der Projekt-Bibliotheken
    pip install deepface opencv-python pandas matplotlib ultralytics jupyter
    ```

### Warum diese Versionen?

* **TensorFlow & DeepFace:** `deepface` (für die Emotionsanalyse) basiert auf TensorFlow. Neuere TF-Versionen (wie 2.20, die für Python 3.13 verfügbar sind) haben einen Fehler (`EagerTensor object is not subscriptable`), der die Gesichtserkennung in `deepface` unbrauchbar macht.
* **Python 3.10:** Ist die letzte Python-Version, die offiziell von `tensorflow==2.11.0` (der stabilsten Version für `deepface`) unterstützt wird.

## 🚀 Methodik & Vorgehensweise

Unsere Vorgehensweise ist in klare Phasen gegliedert, um eine robuste und relevante Analyse zu gewährleisten:

1.  **Explorative Datenanalyse (EDA):** Wir beginnen mit einem Datensatz, um unsere ersten Hypothesen und Analyse-Skripte schnell zu entwickeln und zu testen.
2.  **Analyse der visuellen Inhalte:** Wir gehen über einfache Metadaten hinaus. Mithilfe eines vortrainierten Convolutional Neural Networks (CNN) analysieren wir den visuellen Inhalt jedes Videos und wandeln ihn in numerische Vektoren um.
3.  **Algorithmische Trend-Identifikation:** Der Kern unseres Projekts besteht darin, Clustering-Algorithmen auf diese visuellen Vektoren anzuwenden und zu vergleichen, um automatisch visuelle Stile und Trends zu entdecken.
4.  **Prädiktive Modellierung:** Schließlich kombinieren wir alle Datenpunkte (Metadaten + visuelle Merkmale), um ein Vorhersagemodell zu trainieren, das die wichtigsten Treiber der Viralität identifiziert.

---

## 📊 Datensätze

---

---

## 🛠️ Technischer Stack & Schlüsselalgorithmen

Dieses Projekt basiert vollständig auf Python 3 und nutzt einen modernen Data-Science-Stack.

**Bibliotheken:**
* **Datensammlung:** `instaloader`
* **Datenmanipulation & -analyse:** `pandas`, `numpy`
* **Machine Learning:** `scikit-learn`, `TensorFlow`/`PyTorch`, `xgboost`
* **Datenvisualisierung:** `matplotlib`, `seaborn`

**Schlüsselalgorithmen:**
* **CNN zur Merkmalsextraktion:** Wir verwenden **ResNet50** mittels Transfer Learning, um aus jedem Video einen hochdimensionalen Merkmalsvektor (einen "visuellen Fingerabdruck") zu extrahieren.
* **Clustering zur Trend-Identifikation:**
    * **K-Means:** Dient als Baseline-Algorithmus, um Videos in eine vordefinierte Anzahl von visuellen Clustern zu gruppieren.
    * **DBSCAN:** Dient als fortgeschrittener Algorithmus, um eine realistischere Anzahl von Clustern basierend auf der Datendichte zu finden und nicht-trendiges "Rauschen" herauszufiltern.
* **Prädiktive Modellierung (optional):**
    * **XGBoost:** Ein leistungsstarkes Gradient-Boosting-Modell, das verwendet wird, um den Erfolg von Videos vorherzusagen und – was am wichtigsten ist – die Merkmale nach ihrem Beitrag zu diesem Erfolg zu ordnen.
___

## 🔧 Einrichtung & Umgebung (macOS, Linux, Windows)

Folge diesen Schritten für eine reproduzierbare lokale Umgebung. Die Anweisungen decken macOS/Linux (zsh/bash), Windows (PowerShell/cmd) und WSL ab.

1) Virtuelle Umgebung erstellen (plattformübergreifend):

```bash
# macOS / Linux
python3 -m venv .venv
# oder auf manchen Windows-Setups
# python -m venv .venv
```

2) Virtuelle Umgebung aktivieren

- macOS / Linux (zsh, bash):

```bash
source .venv/bin/activate
# Prompt: (.venv) user@host:~/Projekt$
```

- Windows PowerShell (empfohlen auf Windows):

```powershell
# Falls nötig (als Administrator): Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
# Prompt: (.venv) PS C:\Users\User\Projekt>
```

- Windows cmd.exe:

```cmd
.\.venv\Scripts\activate.bat
```

- WSL (Ubuntu on Windows):

Öffne deine WSL-Shell und benutze die Linux-Befehle:

```bash
source .venv/bin/activate
```

3) Abhängigkeiten installieren

```bash
pip install -r requirements.txt
# Falls du noch kein requirements.txt hast, installiere die benötigten Pakete einzeln, z. B.: 
# pip install instaloader pandas numpy scikit-learn matplotlib seaborn ipykernel
```

4) Jupyter Kernel (optional, damit das Notebook den venv nutzt)

```bash
pip install ipykernel
python -m ipykernel install --user --name=viralitaetsanalyse --display-name "Python (viralitaetsanalyse)"
```

5) Nützliche Befehle

```bash
# Installierte Pakete anzeigen
pip list

# Abhängigkeiten in requirements.txt speichern
pip freeze > requirements.txt
```


# Viralytics Frontend

Dies ist das Angular-Frontend für **Viralytics**, ein KI-gestütztes Tool zur Vorhersage der Viralität von Kurzvideos (Instagram Reels, TikToks).

Es bietet eine Drag-and-Drop-Schnittstelle, um Videos hochzuladen, visualisiert den Viralitäts-Score und zeigt detaillierte Audio-, Video- und KI-Features in einer Tabelle an.

---

## 📋 Voraussetzungen

Bevor du startest, stelle sicher, dass folgende Tools installiert sind:

* **Node.js** (Version 18 oder höher empfohlen): [Download](https://nodejs.org/)
* **Angular CLI**: Installiere es global über dein Terminal:
    ```bash
    npm install -g @angular/cli
    ```

---

## 🛠️ Installation

1.  Navigiere in das Frontend-Verzeichnis:
    ```bash
    cd viralytics-frontend
    ```

2.  Installiere die Abhängigkeiten (Packages):
    ```bash
    npm install
    ```
    *(Dies lädt Angular, TypeScript und andere notwendige Bibliotheken herunter und speichert sie im `node_modules` Ordner.)*

---

## ⚙️ Konfiguration

### Backend-Verbindung
Das Frontend kommuniziert standardmäßig mit dem lokalen FastAPI-Backend unter `http://127.0.0.1:8000`.

Falls du das Backend auf einem anderen Port oder Server laufen lässt, musst du die URL anpassen:

1.  Öffne die Datei: `src/app/app.ts`
2.  Suche nach der Zeile:
    ```typescript
    private backendUrl = '[http://127.0.0.1:8000/predict](http://127.0.0.1:8000/predict)';
    ```
3.  Ändere die URL entsprechend deiner Backend-Konfiguration.

---

## ▶️ Starten der Anwendung

1.  Stelle sicher, dass dein **Python Backend läuft** (siehe Backend-Dokumentation), sonst erhältst du Verbindungsfehler.

2.  Starte den Angular Development Server:
    ```bash
    ng serve
    ```
    *Alternativ kannst du auch `npm start` verwenden.*

3.  Öffne deinen Browser und gehe auf:
    👉 **http://localhost:4200/**

---

##  Features & Nutzung

1.  **Video Upload:**
    * Ziehe eine Videodatei (`.mp4`, `.mov`, `.avi`) in die gestrichelte Dropzone.
    * Oder klicke auf die Zone, um den Datei-Explorer zu öffnen.
    * Klicke auf "Video Analysieren".

2.  **Analyse-Ergebnis:**
    * **Score:** Zeigt die Wahrscheinlichkeit (0-100%), dass das Video viral geht.
    * **KI-Feedback:** Ein generierter Text, der Stärken und Schwächen interpretiert.
    * **Feature-Tabelle:** Eine detaillierte Auflistung aller extrahierten Metriken (z.B. `ist_person_prominent`, `bpm`, `schnitt_frequenz`).
