# 🪺 The Nest

> **The Nest** è la piattaforma social e di matchmaking professionale per sviluppatori, designer e creativi. Permette di trovare talenti per i propri progetti, svilupparli in un ambiente integrato e lanciarli online.

---

## 🚀 Architettura del Progetto e Struttura dei File

Ecco una panoramica dettagliata della struttura del repository e della funzione di ogni singolo file:

```text
the-nest/
├── frontend/                 # Applicazione Client (HTML/CSS/JS + Framework)
│   ├── public/               # Asset statici pubblici (immagini, favicon, ecc.)
│   ├── src/                  # Codice sorgente della UI (componenti, pagine, stili)
│   └── package.json          # Dipendenze Node.js e script di avvio/build
│
├── backend/                  # API REST in Flask
│   ├── app.py                # Punto di ingresso dell'applicazione Flask e configurazione delle route
│   ├── requirements.txt      # Dipendenze Python (Flask, SQLAlchemy, PyMySQL, ecc.)
│   └── migrations/           # Tracciamento e storicizzazione dello schema DB (gestito da Flask-Migrate)
│
├── .env                      # [NON INCLUSO SU GIT] Credenziali locali e password per DB e servizi
├── .env.example              # Template di esempio per le variabili d'ambiente necessarie
├── .gitignore                # Regole per escludere file temporanei, build e credenziali da Git
├── Dockerfile                # Configurazione per la creazione dell'immagine Docker del backend
└── docker-compose.yml        # Orchestratore per avviare contemporaneamente il database MySQL e il backend