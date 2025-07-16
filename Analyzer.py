# API_SCHLUESSEL = "AIzaSyB1wng2WLK7CUji3wcFtlTWO4xvxfUz3N0" ----> Kostenlose API, desswegen hier drin
#     MODELL_NAME = "gemini-2.5-flash-lite-preview-06-17" 

import whois
import socket
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import sys
import ssl
from urllib.parse import urlparse, urljoin
from datetime import datetime
from colorama import init, Fore, Style

# Initialisiert Colorama für farbige Terminal-Ausgabe
init(autoreset=True)

def print_header(title):
    """ Druckt eine formatierte, farbige Überschrift. """
    print(f"\n{Style.BRIGHT}{Fore.CYAN}--- {title.upper()} ---{Style.RESET_ALL}")

def print_subheader(title):
    """ Druckt eine formatierte Unterüberschrift. """
    print(f"\n{Style.BRIGHT}{Fore.YELLOW}>> {title}{Style.RESET_ALL}")

def print_info(key, value):
    """ Druckt ein Schlüssel-Wert-Paar formatiert. """
    print(f"  {Fore.GREEN}{key:<25}{Style.RESET_ALL}{value}")

def print_error(message):
    """ Druckt eine Fehlermeldung formatiert. """
    print(f"  {Fore.RED}FEHLER: {message}{Style.RESET_ALL}")

def get_advanced_website_info(url):
    """
    Sammelt und analysiert umfassende Informationen über eine Website und präsentiert sie strukturiert.
    """
    # --- Konfiguration ---
    API_SCHLUESSEL = "AIzaSyB1wng2WLK7CUji3wcFtlTWO4xvxfUz3N0"
    MODELL_NAME = "gemini-2.5-flash-lite-preview-06-17"

    # --- Gemini API Konfiguration ---
    model = None
    try:
        genai.configure(api_key=API_SCHLUESSEL)
        model = genai.GenerativeModel(MODELL_NAME)
    except Exception as e:
        print_error(f"Konfiguration der Gemini API fehlgeschlagen: {e}")
        
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url
    
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    print_header(f"Analyse wird für {domain} gestartet")

    # === 1. Domain- & Server-Informationen ===
    print_header("Domain- & Server-Informationen")

    # --- WHOIS-Abruf ---
    print_subheader("WHOIS-Registerdaten")
    try:
        w = whois.whois(domain)
        print_info("Erstellt am:", w.creation_date)
        print_info("Läuft ab am:", w.expiration_date)
        print_info("Letztes Update:", w.updated_date)
        print_info("Registrar:", w.registrar)
        print_info("Organisation:", w.org)
    except Exception as e:
        print_error(f"WHOIS-Abruf fehlgeschlagen: {e}")

    # --- DNS- & Netzwerk-Abruf ---
    print_subheader("Netzwerkinformationen")
    try:
        ip_address = socket.gethostbyname(domain)
        print_info("IP-Adresse:", ip_address)
    except socket.gaierror:
        print_error("IP-Adresse konnte nicht ermittelt werden.")

    # --- SSL-Zertifikat ---
    print_subheader("SSL-Zertifikat")
    if parsed_url.scheme == 'https':
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    subject = dict(x[0] for x in cert['subject'])
                    issuer = dict(x[0] for x in cert['issuer'])
                    valid_from = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    valid_to = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    print_info("Ausgestellt für:", subject.get('commonName', 'N/A'))
                    print_info("Aussteller:", issuer.get('organizationName', 'N/A'))
                    print_info("Gültig von:", valid_from.strftime('%Y-%m-%d'))
                    print_info("Gültig bis:", valid_to.strftime('%Y-%m-%d'))
        except Exception as e:
            print_error(f"SSL-Zertifikat konnte nicht geprüft werden: {e}")
    else:
        print_info("Status:", "Kein HTTPS, daher kein SSL-Zertifikat.")

    # === 2. On-Page-Analyse ===
    print_header("On-Page-Analyse")
    text_content = ""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # --- Technische Details ---
        print_subheader("Technische Seitendetails")
        print_info("HTTP-Statuscode:", response.status_code)
        print_info("Server-Technologie:", response.headers.get('Server', 'Nicht erkannt'))
        if response.cookies:
            print_info("Gesetzte Cookies:", ", ".join([cookie.name for cookie in response.cookies]))
        else:
            print_info("Gesetzte Cookies:", "Keine")

        # --- Inhalts-Extraktion für KI ---
        soup = BeautifulSoup(response.content, 'html.parser')
        for element in soup(["script", "style", "nav", "footer", "aside", "header"]):
            element.decompose()
        text_content = soup.get_text(separator=' ', strip=True)
        
        max_chars = 45000
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars]
        
        print_info("Text für KI-Analyse:", "Erfolgreich extrahiert.")

    except requests.RequestException as e:
        print_error(f"Website konnte nicht abgerufen werden: {e}")

    # --- Robots.txt & Sitemap ---
    print_subheader("Crawler-Anweisungen")
    try:
        robots_url = urljoin(base_url, 'robots.txt')
        robots_res = requests.get(robots_url, headers=headers, timeout=5)
        if robots_res.status_code == 200 and 'html' not in robots_res.headers.get('Content-Type', ''):
            print_info("robots.txt:", "Gefunden und lesbar.")
            if "sitemap" in robots_res.text.lower():
                 print_info("Sitemap-Verweis:", "In robots.txt gefunden.")
            else:
                 print_info("Sitemap-Verweis:", "Keiner in robots.txt gefunden.")
        else:
            print_info("robots.txt:", "Nicht gefunden oder nicht lesbar.")
    except requests.RequestException:
        print_error("robots.txt konnte nicht geprüft werden.")

    # === 3. Erweiterte KI-Analyse mit Gemini ===
    if model and text_content:
        print_header("Gemini KI-Analyse")
        try:
            prompt = f"""
            Analysiere den folgenden Text der Webseite '{domain}' umfassend.
            Gib die Antwort auf Deutsch und in einem klaren, strukturierten Format zurück.
            Beantworte die folgenden Punkte basierend auf dem Text:

            1.  **Zusammenfassung:** Fasse den Hauptzweck und Inhalt der Seite in 2-3 Sätzen zusammen.
            2.  **Zielgruppe:** Wer ist die primäre Zielgruppe dieser Webseite? (z.B. Entwickler, Familien, Studenten, Unternehmen)
            3.  **Tonalität und Sprache:** Wie ist der Schreibstil? (z.B. formell, locker, technisch, werblich, informativ)
            4.  **Kernthemen & Keywords:** Liste die 5-7 wichtigsten Themen oder Keywords auf, die im Text vorkommen.
            5.  **Call-to-Actions (CTAs):** Welche konkreten Handlungsaufforderungen werden an den Besucher gerichtet? (z.B. "Jetzt kaufen", "Registrieren", "Mehr erfahren")
            6.  **Potenzielles Geschäftsmodell:** Wie verdient diese Website wahrscheinlich Geld? (z.B. E-Commerce, Werbung, Abonnements, Lead-Generierung)

            Hier ist der zu analysierende Text:
            ---
            {text_content}
            ---
            """
            
            gemini_response = model.generate_content(prompt)
            print(gemini_response.text)

        except Exception as e:
            print_error(f"Kommunikation mit der Gemini API fehlgeschlagen: {e}")
    elif not model:
        print_error("Überspringe KI-Analyse, da das Modell nicht geladen werden konnte.")
    else:
        print_error("Überspringe KI-Analyse, da kein Text von der Website extrahiert werden konnte.")


if __name__ == "__main__":
    try:
        website_url = input(f"{Style.BRIGHT}Bitte geben Sie die URL der Website ein (z.B. wikipedia.org): {Style.RESET_ALL}")
        if website_url:
            get_advanced_website_info(website_url)
        else:
            print("Keine URL eingegeben. Programm wird beendet.")
    except KeyboardInterrupt:
        print("\nProgramm vom Benutzer abgebrochen.")
    except Exception as e:
        print_error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
