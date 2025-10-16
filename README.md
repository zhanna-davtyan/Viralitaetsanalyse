#  Decoding Virality: Eine algorithmische Analyse von Kurzvideo-Inhalten

**Projektziel:** Dieses Projekt geht über subjektive Spekulationen hinaus, um eine zentrale Frage der modernen digitalen Landschaft zu beantworten: 

**Was sind die quantifizierbaren Faktoren, die ein Kurzvideo erfolgreich machen?** 

wWir wenden eine mehrstufige Datenanalyse- und Machine-Learning-Pipeline an, um visuelle Trends zu identifizieren und das Engagement von Videos vorherzusagen.

---

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