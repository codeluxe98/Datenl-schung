# Incogni Ähnliche Anwendung

Dieses Projekt stellt eine einfache Webanwendung bereit, mit der Nutzer die Löschung ihrer Daten bei Brokern beantragen können. Die Anwendung basiert auf Flask und MySQL und kann per Docker betrieben werden (z. B. auf einem Raspberry Pi).

## Funktionen

* Registrierung mit Benutzername, E‑Mail und Telefonnummer
* Verschlüsselte Speicherung von E‑Mail und Telefonnummer in MySQL
* Login und Rollenverwaltung (Kunde und Admin)
* Admin‑Panel zur Benutzerübersicht
* Versenden von Löschungsanfragen per E‑Mail an Broker

## Starten mit Docker


1. Passen Sie in `docker-compose.yml` die Umgebungsvariablen für MySQL und Gmail an.
2. Führen Sie anschließend aus:
=======
1. Erzeugen Sie zunächst einen Fernet-Schlüssel mit dem gleichen Python‑Befehl wie beim manuellen Start und tragen Sie ihn in `docker-compose.yml` bei `ENCRYPTION_KEY` ein:

   ```bash
   python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
   ```

   Der Schlüssel muss zwischen Neustarts gleich bleiben, damit zuvor verschlüsselte Daten wieder entschlüsselt werden können.
2. Passen Sie in `docker-compose.yml` die weiteren Umgebungsvariablen für MySQL und Gmail an.
3. Führen Sie anschließend aus:


```bash
docker compose up --build
```

Die Weboberfläche ist danach unter `http://localhost:5000` erreichbar.


## Benötigte Pakete

Zum Kompilieren von `mysqlclient` werden einige Systempakete benötigt:

* libmysqlclient-dev (oder libmariadb-dev)
* build-essential

Diese Pakete installiert das Dockerfile automatisch, bei einer lokalen Installation müssen sie zuvor manuell installiert werden.

## Manuelles Starten

Alternativ können Sie die Anwendung lokal starten (Python 3.12 vorausgesetzt):

```bash
pip install -r requirements.txt
export DATABASE_URL="mysql://user:password@localhost/app"
export GMAIL_USER="you@example.com"
export GMAIL_PASS="yourpass"
export ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
export SECRET_KEY="changeme"
python app/app.py
# oder alternativ
flask --app app/app.py run
```

## Hinweise

Damit der Versand von E‑Mails über Gmail funktioniert, muss für das verwendete Konto ggf. ein App‑Passwort eingerichtet werden.
