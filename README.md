# 🧠 Advanced Website Analyzer

Ein **leistungsstarkes Python-Skript** zur umfassenden Analyse von Websites. Es kombiniert klassische Techniken zur Informationsgewinnung (z. B. WHOIS, DNS, SSL) mit der **Intelligenz der Google Gemini API**, um tiefgehende Einblicke in Technik, Inhalte und Strategie einer Webseite zu liefern.

Die Ausgabe erfolgt direkt im Terminal – **farblich formatiert** für perfekte Lesbarkeit.

---

## ✨ Features

Das Skript sammelt viele verschiedene Datenpunkte und zeigt sie sauber strukturiert an:

### 🌐 1. Domain- & Server-Informationen
- WHOIS-Daten wie Erstellungs- und Ablaufdatum, Registrar und Organisation.
- Netzwerkinformationen wie die IP-Adresse der Domain.
- SSL-Zertifikat-Infos, z. B. Aussteller und Gültigkeit (bei HTTPS-Seiten).

### 🧩 2. On-Page-Analyse (Technik & Inhalt)
- HTTP-Header wie Server-Statuscode und verwendete Technologie (z. B. Apache).
- Liste der gesetzten Cookies.
- Analyse von robots.txt und Suche nach einer sitemap.xml.
- Intelligente Textextraktion für die KI-Analyse.

### 🤖 3. Erweiterte KI-Analyse (via Gemini API)
- Automatische Zusammenfassung des Seiteninhalts.
- Einschätzung der Zielgruppe.
- Analyse des Sprachstils (formell, werblich, technisch usw.).
- Erkennung der wichtigsten Themen & Keywords.
- Auswertung von Handlungsaufforderungen (Call-to-Actions).
- Vermutung eines möglichen Geschäftsmodells.

---

## 🛠️ Anforderungen

- Python 3.6 oder neuer  
- Benötigte Bibliotheken:
  - python-whois  
  - requests  
  - beautifulsoup4  
  - google-generativeai  
  - colorama  

---

## 📦 Installation

1. Repository klonen oder das Skript lokal abspeichern (z. B. als `advanced_web_analyzer.py`).

2. Im Terminal folgenden Befehl ausführen, um alle Bibliotheken zu installieren:

   **pip install python-whois requests beautifulsoup4 google-generativeai colorama**

---

## 🔧 Konfiguration

Damit die KI-Analyse funktioniert, muss ein **Google Gemini API-Schlüssel** hinterlegt werden.

- Einen kostenlosen API-Schlüssel gibt’s über Google AI Studio.  
- Danach einfach im Skript den Platzhalter durch den eigenen Schlüssel ersetzen.

⚠️ Wichtig: API-Schlüssel ist von mir, der ist kostenlos, kann man benutzen, doch wenn möglich eigenen verwenden!!!

---

## 🚀 Verwendung

Starte das Skript im Terminal mit:

**python advanced_web_analyzer.py**

Du wirst danach aufgefordert, eine URL einzugeben (z. B. `github.com`) – und schon beginnt die Analyse.

---

## 📋 Beispiel-Ausgabe

Das Tool zeigt danach gegliedert:

- Domain-Infos inkl. WHOIS und IP
- Serverdetails und HTTPS-Zertifikat
- Technische Daten der Seite (Statuscode, Cookies, Robots.txt etc.)
- Intelligente Zusammenfassung, Zielgruppe, Stil, Keywords & mehr

---

Viel Spaß beim Analysieren! 🔍✨  
Für Feedback oder Erweiterungen: einfach melden 😄

---
**Uuuund dankiiii fürs nutzen meines Tools!!! ❤** 
