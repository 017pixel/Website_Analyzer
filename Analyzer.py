# MODELL_NAME = "gemini-2.5-flash-lite-preview-06-17" 

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
import time

# Initialisiert Colorama für farbige Terminal-Ausgabe
init(autoreset=True)

def print_banner():
    banner = f"""
{Style.BRIGHT}{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
║                    🌐 WEBSITE ANALYZER TOOL 🌐                  ║
║                      Professionelle Web-Analyse                  ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_header(title):
    """Druckt eine formatierte, farbige Überschrift."""
    print(f"\n{Style.BRIGHT}{Fore.CYAN}╭─── {title.upper()} ───╮{Style.RESET_ALL}")

def print_subheader(title):
    """Druckt eine formatierte Unterüberschrift."""
    print(f"\n{Style.BRIGHT}{Fore.YELLOW}▶ {title}{Style.RESET_ALL}")

def print_info(key, value):
    """Druckt ein Schlüssel-Wert-Paar formatiert."""
    print(f"  {Fore.BLUE}• {key:<25}{Style.RESET_ALL}{Fore.WHITE}{value}{Style.RESET_ALL}")

def print_success(message):
    """Druckt eine Erfolgsmeldung."""
    print(f"  {Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_warning(message):
    """Druckt eine Warnung."""
    print(f"  {Fore.YELLOW}⚠ WARNUNG: {message}{Style.RESET_ALL}")

def print_error(message):
    """Druckt eine Fehlermeldung formatiert."""
    print(f"  {Fore.RED}✗ FEHLER: {message}{Style.RESET_ALL}")

def print_separator():
    """Druckt eine dekorative Trennlinie."""
    print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")

def get_gemini_config():
    """Fragt nach Gemini API-Schlüssel und konfiguriert das Modell."""
    print_header("KI-Analyse Konfiguration")
    
    while True:
        choice = input(f"{Style.BRIGHT}Möchten Sie die erweiterte KI-Analyse mit Google Gemini verwenden? (j/n): {Style.RESET_ALL}").strip().lower()
        
        if choice in ['j', 'ja', 'y', 'yes']:
            api_key = input(f"{Style.BRIGHT}Bitte geben Sie Ihren Google Gemini API-Schlüssel ein: {Style.RESET_ALL}").strip()
            
            if not api_key:
                print_error("Kein API-Schlüssel eingegeben!")
                continue
                
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
                
                # Test der API-Verbindung
                print(f"{Fore.YELLOW}Teste API-Verbindung...{Style.RESET_ALL}")
                test_response = model.generate_content("Hallo")
                print_success("Gemini API erfolgreich konfiguriert!")
                return model
                
            except Exception as e:
                print_error(f"API-Konfiguration fehlgeschlagen: {e}")
                retry = input(f"{Style.BRIGHT}Möchten Sie es erneut versuchen? (j/n): {Style.RESET_ALL}").strip().lower()
                if retry not in ['j', 'ja', 'y', 'yes']:
                    break
                continue
                
        elif choice in ['n', 'nein', 'no']:
            print_info("Modus:", "Analyse ohne KI-Funktionen")
            return None
            
        else:
            print_warning("Bitte geben Sie 'j' für Ja oder 'n' für Nein ein.")

def get_advanced_website_info(url, model=None):
    """
    Sammelt und analysiert umfassende Informationen über eine Website und präsentiert sie strukturiert.
    """
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url
    
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    print_separator()
    print_header(f"Analyse für {domain}")
    print(f"  {Fore.CYAN}🔍 Ziel-URL: {Fore.WHITE}{url}{Style.RESET_ALL}")
    print_separator()

    # === 1. Domain- & Server-Informationen ===
    print_header("🌐 Domain- & Server-Informationen")

    # --- WHOIS-Abruf ---
    print_subheader("📋 WHOIS-Registerdaten")
    try:
        w = whois.whois(domain)
        if w.creation_date:
            creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
            print_info("Erstellt am:", creation_date)
        if w.expiration_date:
            expiration_date = w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date
            print_info("Läuft ab am:", expiration_date)
        if w.updated_date:
            updated_date = w.updated_date[0] if isinstance(w.updated_date, list) else w.updated_date
            print_info("Letztes Update:", updated_date)
        print_info("Registrar:", w.registrar or "Nicht verfügbar")
        print_info("Organisation:", w.org or "Nicht verfügbar")
        print_success("WHOIS-Daten erfolgreich abgerufen")
    except Exception as e:
        print_error(f"WHOIS-Abruf fehlgeschlagen: {e}")

    # --- DNS- & Netzwerk-Abruf ---
    print_subheader("🌍 Netzwerkinformationen")
    try:
        ip_address = socket.gethostbyname(domain)
        print_info("IP-Adresse:", ip_address)
        print_success("Netzwerkinformationen abgerufen")
    except socket.gaierror:
        print_error("IP-Adresse konnte nicht ermittelt werden.")

    # --- SSL-Zertifikat ---
    print_subheader("🔒 SSL-Zertifikat")
    if parsed_url.scheme == 'https':
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    subject = dict(x[0] for x in cert['subject'])
                    issuer = dict(x[0] for x in cert['issuer'])
                    
                    # Sicheres Datum-Parsing
                    try:
                        valid_from = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                        valid_to = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        
                        print_info("Ausgestellt für:", subject.get('commonName', 'N/A'))
                        print_info("Aussteller:", issuer.get('organizationName', 'N/A'))
                        print_info("Gültig von:", valid_from.strftime('%Y-%m-%d'))
                        print_info("Gültig bis:", valid_to.strftime('%Y-%m-%d'))
                        
                        # Prüfe Gültigkeit
                        now = datetime.now()
                        if now < valid_from or now > valid_to:
                            print_warning("Zertifikat ist abgelaufen oder noch nicht gültig!")
                        else:
                            print_success("SSL-Zertifikat ist gültig")
                    except ValueError as date_error:
                        print_error(f"Datum-Parsing fehlgeschlagen: {date_error}")
                        print_info("Zertifikat-Info:", "Grundlegende Informationen verfügbar, Datum nicht lesbar")
                        
        except Exception as e:
            print_error(f"SSL-Zertifikat konnte nicht geprüft werden: {e}")
    else:
        print_warning("Kein HTTPS, daher kein SSL-Zertifikat verfügbar")

    # === 2. On-Page-Analyse ===
    print_header("📄 On-Page-Analyse")
    text_content = ""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print(f"  {Fore.YELLOW}📡 Lade Website-Inhalt...{Style.RESET_ALL}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # --- Technische Details ---
        print_subheader("⚙️ Technische Seitendetails")
        print_info("HTTP-Statuscode:", f"{response.status_code} ✓" if response.status_code == 200 else f"{response.status_code} ⚠")
        print_info("Server-Technologie:", response.headers.get('Server', 'Nicht erkannt'))
        print_info("Content-Type:", response.headers.get('Content-Type', 'Nicht erkannt'))
        print_info("Content-Length:", f"{len(response.content):,} Bytes" if response.content else "Nicht verfügbar")
        
        if response.cookies:
            cookie_names = [cookie.name for cookie in response.cookies]
            print_info("Gesetzte Cookies:", f"{len(cookie_names)} Cookies: {', '.join(cookie_names[:3])}" + ("..." if len(cookie_names) > 3 else ""))
        else:
            print_info("Gesetzte Cookies:", "Keine")

        # --- Inhalts-Extraktion für KI ---
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Meta-Tags analysieren
        print_subheader("🏷️ Meta-Informationen")
        title = soup.find('title')
        print_info("Seitentitel:", title.text.strip() if title else "Nicht gefunden")
        
        description = soup.find('meta', attrs={'name': 'description'})
        print_info("Description:", description.get('content', 'Nicht gefunden') if description else "Nicht gefunden")
        
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        print_info("Keywords:", keywords.get('content', 'Nicht gefunden') if keywords else "Nicht gefunden")
        
        # Text für KI extrahieren
        for element in soup(["script", "style", "nav", "footer", "aside", "header"]):
            element.decompose()
        text_content = soup.get_text(separator=' ', strip=True)
        
        max_chars = 45000
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars]
            print_info("Extrahierter Text:", f"{len(text_content):,} Zeichen (gekürzt für KI-Analyse)")
        else:
            print_info("Extrahierter Text:", f"{len(text_content):,} Zeichen")
        
        print_success("Website-Inhalt erfolgreich analysiert")

    except requests.RequestException as e:
        print_error(f"Website konnte nicht abgerufen werden: {e}")
        return

    # --- Robots.txt & Sitemap ---
    print_subheader("🤖 Crawler-Anweisungen")
    try:
        robots_url = urljoin(base_url, 'robots.txt')
        robots_res = requests.get(robots_url, headers=headers, timeout=8)
        if robots_res.status_code == 200:
            content_type = robots_res.headers.get('Content-Type', '').lower()
            # Prüfe ob es wirklich eine Text-Datei ist
            if 'text' in content_type or not content_type or 'robots' in robots_url:
                print_success("robots.txt gefunden und lesbar")
                robots_text = robots_res.text.lower()
                if "sitemap" in robots_text:
                    # Extrahiere Sitemap-URLs
                    sitemap_lines = [line.strip() for line in robots_res.text.split('\n') if 'sitemap:' in line.lower()]
                    if sitemap_lines:
                        print_success(f"Sitemap-Verweis gefunden: {len(sitemap_lines)} URL(s)")
                        for sitemap_line in sitemap_lines[:2]:  # Zeige max. 2 an
                            sitemap_url = sitemap_line.split(':', 1)[1].strip()
                            print_info("Sitemap:", sitemap_url)
                    else:
                        print_success("Sitemap-Erwähnung in robots.txt gefunden")
                else:
                    print_info("Sitemap-Verweis:", "Keiner in robots.txt gefunden")
                
                # Zusätzliche robots.txt Info
                if "user-agent:" in robots_text:
                    print_info("User-Agent Regeln:", "Vorhanden")
            else:
                print_warning("robots.txt gefunden, aber unerwarteter Content-Type")
        else:
            print_warning(f"robots.txt nicht verfügbar (HTTP {robots_res.status_code})")
    except requests.RequestException as e:
        print_error(f"robots.txt konnte nicht geprüft werden: {e}")

    # === 3. Erweiterte KI-Analyse mit Gemini ===
    if model and text_content:
        print_header("🤖 Gemini KI-Analyse")
        try:
            print(f"  {Fore.YELLOW}🧠 KI analysiert Website-Inhalt...{Style.RESET_ALL}")
            
            # Prüfe Textlänge für bessere API-Nutzung
            if len(text_content) < 100:
                print_warning("Sehr wenig Text gefunden - KI-Analyse könnte ungenau sein")
            
            prompt = f"""
            Analysiere den folgenden Text der Webseite '{domain}' umfassend.
            Gib die Antwort auf Deutsch und in einem klaren, strukturierten Format zurück.
            Verwende Emojis und eine ansprechende Formatierung für bessere Lesbarkeit.

            Beantworte die folgenden Punkte basierend auf dem Text:

            🎯 **ZUSAMMENFASSUNG**
            Fasse den Hauptzweck und Inhalt der Seite in 2-3 Sätzen zusammen.

            👥 **ZIELGRUPPE**
            Wer ist die primäre Zielgruppe dieser Webseite? (z.B. Entwickler, Familien, Studenten, Unternehmen)

            📝 **TONALITÄT UND SPRACHE**
            Wie ist der Schreibstil? (z.B. formell, locker, technisch, werblich, informativ)

            🔍 **KERNTHEMEN & KEYWORDS**
            Liste die 5-7 wichtigsten Themen oder Keywords auf, die im Text vorkommen.

            📢 **CALL-TO-ACTIONS (CTAs)**
            Welche konkreten Handlungsaufforderungen werden an den Besucher gerichtet?

            💰 **GESCHÄFTSMODELL**
            Wie verdient diese Website wahrscheinlich Geld? (z.B. E-Commerce, Werbung, Abonnements)

            🏆 **BEWERTUNG**
            Bewerte die Website auf einer Skala von 1-10 bezüglich Professionalität und Benutzerfreundlichkeit.

            Hier ist der zu analysierende Text:
            ---
            {text_content}
            ---
            """
            
            # Gemini API Call mit Retry-Logic
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    gemini_response = model.generate_content(prompt)
                    if gemini_response.text:
                        print(f"\n{Style.BRIGHT}{Fore.GREEN}🎉 KI-Analyse abgeschlossen:{Style.RESET_ALL}")
                        print(f"{Fore.WHITE}{gemini_response.text}{Style.RESET_ALL}")
                        break
                    else:
                        print_warning("KI-Antwort war leer")
                        if attempt < max_retries:
                            print(f"  {Fore.YELLOW}Versuche erneut... ({attempt + 2}/{max_retries + 1}){Style.RESET_ALL}")
                            time.sleep(1)
                except Exception as api_error:
                    if attempt < max_retries:
                        print_warning(f"API-Versuch {attempt + 1} fehlgeschlagen, versuche erneut...")
                        time.sleep(2)
                    else:
                        raise api_error

        except Exception as e:
            print_error(f"Kommunikation mit der Gemini API fehlgeschlagen: {e}")
            if "quota" in str(e).lower():
                print_warning("Möglicherweise API-Quota erreicht. Prüfen Sie Ihr Gemini-Konto.")
    elif not model:
        print_header("ℹ️  KI-Analyse übersprungen")
        print_info("Status:", "KI-Analyse deaktiviert (kein API-Schlüssel konfiguriert)")
    else:
        print_error("KI-Analyse nicht möglich - kein Text von der Website extrahiert")

    print_separator()
    print(f"{Style.BRIGHT}{Fore.GREEN}✅ Analyse für {domain} abgeschlossen!{Style.RESET_ALL}")
    print_separator()


def main():
    """Hauptfunktion des Website-Analyzer-Tools."""
    try:
        print_banner()
        
        # Gemini-Konfiguration
        model = get_gemini_config()
        
        print_separator()
        
        while True:
            website_url = input(f"{Style.BRIGHT}{Fore.CYAN}🌐 Bitte geben Sie die URL der Website ein (z.B. wikipedia.org): {Style.RESET_ALL}").strip()
            
            if not website_url:
                print_warning("Keine URL eingegeben!")
                continue
                
            # Bestätigung anzeigen
            print(f"  {Fore.BLUE}➤ Analysiere: {Fore.WHITE}{website_url}{Style.RESET_ALL}")
            
            # Analyse starten
            get_advanced_website_info(website_url, model)
            
            # Weitere Analyse anbieten
            while True:
                continue_choice = input(f"\n{Style.BRIGHT}Möchten Sie eine weitere Website analysieren? (j/n): {Style.RESET_ALL}").strip().lower()
                if continue_choice in ['j', 'ja', 'y', 'yes']:
                    break
                elif continue_choice in ['n', 'nein', 'no']:
                    print(f"\n{Style.BRIGHT}{Fore.CYAN}👋 Vielen Dank für die Nutzung des Website Analyzer Tools!{Style.RESET_ALL}")
                    return
                else:
                    print_warning("Bitte geben Sie 'j' für Ja oder 'n' für Nein ein.")
                    
    except KeyboardInterrupt:
        print(f"\n{Style.BRIGHT}{Fore.YELLOW}⚠ Programm vom Benutzer abgebrochen.{Style.RESET_ALL}")
    except Exception as e:
        print_error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")


if __name__ == "__main__":
    main()
