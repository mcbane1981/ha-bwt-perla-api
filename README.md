# BWT Perla (Local API) – Home Assistant Custom Integration

Eine maßgeschneiderte Home Assistant Custom Integration zur lokalen Einbindung von **BWT Perla** und **Rondomat Duo (2. Generation)** Wasserenthärtungsanlagen über die interne REST-API (ohne Cloud-Zwang).

---

## 🏗️ Funktionen

* **Vollständige GUI-Konfiguration (Config Flow):** Einfache Einrichtung unter *Geräte & Dienste* mit Eingabe von IP-Adresse, Login-Code und Abfrage-Intervall.
* **100 % Lokale Steuerung:** Direkte Abfrage der Anlage im lokalen Netzwerk (Port 8080) ohne Abhängigkeit von BWT-Cloud-Diensten.
* **Vollständige Entitäten-Abdeckung:** Liest alle **32 Parameter** des `/api/GetCurrentData`-Endpunkts aus.
* **Fehlercodes in Klartext:** Wandelt die Roh-Fehler-IDs (`ActiveErrorIDs`) automatisch in deutsche Klartext-Meldungen sowie kompakte Dashboard-Kurztexte um.
* **Optimierte Datenverarbeitung:** Berücksichtigt abweichende HTTP-Header (`text/plain`) und stellt den zuverlässigen Datenempfang sicher.
* **HACS-Kompatibel:** Schnelle Installation und Aktualisierung über den Home Assistant Community Store.

---

## 📋 Voraussetzungen

1. **Software-Version der BWT Perla:** Mindestens **Firmware 2.02xx** (vorherige Versionen bieten keine REST-API).
2. **API am Gerät aktiviert:** In den Einstellungen der BWT Perla unter `Einstellungen` ➔ `Allgemeines` ➔ `Verbindung` den Schieberegler **API** auf *Aktiv* stellen.
3. **Login-Code:** Der mehrstellige Code aus der Registrierungs-E-Mail von BWT (wird für die HTTP Basic Auth als Passwort genutzt).
4. **Netzwerk:** Die BWT Perla muss per LAN oder WLAN im selben Netzwerk wie dein Home Assistant Server erreichbar sein.

---

## 🚀 Installation

### Methode 1: Über HACS (Empfohlen)

1. Öffne **HACS** in Home Assistant.
2. Klicke oben rechts auf die drei Punkte **⋮** ➔ **Benutzerdefinierte Repositories**.
3. Füge die URL deines Repositories ein:
`[https://github.com/DEIN_USERNAME/bwt_perla_api](https://github.com/DEIN_USERNAME/bwt_perla_api)`
4. Wähle als Kategorie **Integration**.
5. Klicke auf **Hinzufügen**, suche nach **BWT Perla (Local API)** und klicke auf **Herunterladen**.
6. Starte Home Assistant neu.

---

### Methode 2: Manuelle Installation

1. Lade den Ordner `custom_components/bwt_perla_api` aus diesem Repository herunter.
2. Kopiere den Ordner in das Konfigurationsverzeichnis deines Home Assistant Servers:
```text
/config/custom_components/bwt_perla_api/

```


3. Die Ordnerstruktur muss wie folgt aussehen:
```text
/config/custom_components/bwt_perla_api/
├── __init__.py
├── config_flow.py
├── const.py
├── manifest.json
├── sensor.py
├── strings.json
├── translations/
│   └── de.json
├── icon.png
└── logo.png

```


4. Starte Home Assistant neu (`docker restart homeassistant` oder über die GUI).

---

## ⚙️ Einrichtung (Config Flow)

1. Gehe in Home Assistant zu **Einstellungen** ➔ **Geräte & Dienste**.
2. Klicke unten rechts auf **Integration hinzufügen**.
3. Suche nach **BWT Perla (Local API)**.
4. Gib die Verbindungsdaten deiner Anlage ein:
* **IP-Adresse:** Die IP-Adresse deiner BWT Perla (z. B. `192.168.1.52`).
* **Login-Code:** Dein persönlicher Registrierungscode von BWT.
* **Abfrage-Intervall:** Intervall in Sekunden (Standard: `30`).



---

## 📊 Bereitsgestellte Entitäten

Die Integration legt automatisch ein Gerät **BWT Perla Wasserenthärtung** mit folgenden Sensoren an:

| Entität | Beschreibung | Einheit / Format |
| --- | --- | --- |
| **Fehlermeldung** | Detaillierter Fehlertext in deutschem Klartext | Text (z. B. *Regeneriermittelvolumen nicht erreicht*) |
| **Fehler Kurztext** | Kompakte Statusanzeige für Dashboard-Kacheln | Text (z. B. *OK*, *Sole-Volumen*, *Salz 0%*) |
| **Status** | Betriebszustand der Anlage | *Betriebsbereit (OK)*, *Warnung*, *Fehler* |
| **Salz Füllstand** | Füllstand des Salzbehälters | `%` |
| **Salz Verbleibende Tage** | Geschätzte Restreichweite des Salzes | `Tage` |
| **Salzverbrauch gesamt** | Salzverbrauch seit Inbetriebnahme | `g` |
| **Aktueller Durchfluss** | Momentaner Durchfluss | `L/h` |
| **Restkapazität Säule 1 / 2** | Verbleibende Enthärtungskapazität je Säule | `ml*°dH` |
| **Aufbereitetes Wasser Heute** | Enthärtetes Wasser am aktuellen Tag | `L` |
| **Aufbereitetes Wasser Monat / Jahr** | Kumulierter Verbrauch im Monat / Jahr | `L` |
| **Ausgangswasser gesamt** | Wasserverbrauch seit Inbetriebnahme | `L` |
| **Eingangshärte / Ausgangshärte** | Härtegrad vor/nach Enthärtung | `°dH`, `°fH`, `ppm`, `mmol/L` |
| **Regenerationen Gesamt** | Anzahl aller durchgeführten Regenerationen | Zähler |
| **Urlaubsmodus Status** | Status des Urlaubsmodus | *Aktiviert* / *Deaktiviert* |
| **Firmware Version** | Installierte Softwareversion der Anlage | Text |

---

## 🛠️ Technische Details der BWT REST-API

* **Endpunkt:** `http://<IP>:8080/api/GetCurrentData`
* **Authentifizierung:** HTTP Basic Auth (`user` : `<Login-Code>`)
* **Port-Achtung:** Port 80 verweist bei BWT-Geräten auf die VNC-Weboberfläche. Die REST-API antwortet ausschließlich auf **Port 8080**.

---

## ❓ Troubleshooting & Fehlerbehebung

| Fehler in der GUI | Mögliche Ursache & Lösung |
| --- | --- |
| **Verbindung fehlgeschlagen: Port 8080 abgelehnt** | Die API ist im Menü der BWT Perla deaktiviert. Überprüfe `Einstellungen` ➔ `Verbindung`. |
| **Verbindung fehlgeschlagen: IP nicht erreichbar** | Falsche IP-Adresse eingegeben oder Gerät befindet sich in einem isolierten VLAN/Subnetz. |
| **Ungültiger Login-Code (HTTP 401/403)** | Der Login-Code unterscheidet zwischen Groß-/Kleinschreibung. Nutze den Code aus der BWT-E-Mail. |
| **Invalid handler specified** | Home Assistant wurde nach dem Kopieren des Ordners noch nicht neu gestartet. |

---

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** veröffentlicht – siehe [LICENSE](https://www.google.com/search?q=LICENSE) Datei für Details.

*Hinweis: Dies ist ein inoffizielles Community-Projekt und steht in keiner offiziellen Verbindung zur BWT Holding GmbH.*
