# 🤖 Agent IA - LangGraph + FastAPI + Groq

Agent IA conversationnel avec appel d'outils, construit avec **LangGraph**, exposé via **FastAPI** et propulsé par le modèle **`openai/gpt-oss-120b`** via **Groq**.

---


## Architecture

```
Client  →  FastAPI  →  LangGraph Agent  →  Groq (GPT-OSS 120B)
                              ↕
                           Tools
                     (météo, calculatrice...)
```

| Composant | Rôle |
|---|---|
| **FastAPI** | Exposition de l'API REST + streaming SSE |
| **LangGraph** | Orchestration du graphe de l'agent |
| **Groq** | Inférence ultra-rapide via LPU |
| **GPT-OSS 120B** | Modèle de langage principal |

---

## Prérequis

- Python 3.11+
- Une clé API Groq → [console.groq.com](https://console.groq.com)

---

## Installation

```bash
# Cloner le projet
git clone https://github.com/SeydinaBANE/mon-agent-ia.git
cd mon-agent-ia

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

**`requirements.txt`**
```txt
fastapi==0.115.12
uvicorn==0.41.0
langgraph==1.0.7
langchain-groq==1.1.2
langchain-core==1.0.0
pydantic==2.11.0
python-dotenv==1.1.0
```

---

## Configuration

Crée un fichier `.env` à la racine du projet :

```env
GROQ_API_KEY=gsk_...
```

---

## Lancer l'application

```bash
uvicorn main:app --reload
```

L'API est disponible sur `http://localhost:8000`

| URL | Description |
|---|---|
| `http://localhost:8000/docs` | Documentation Swagger UI interactive |
| `http://localhost:8000/redoc` | Documentation ReDoc |
| `http://localhost:8000/openapi.json` | Schéma OpenAPI brut |

---

## Structure du projet

```
mon-agent-ia/
├── main.py                  # Point d'entrée FastAPI
├── requirements.txt
├── .env                     # Variables d'environnement (non versionné)
├── .env.example
├── agent/
│   ├── __init__.py
│   ├── state.py             # Définition de l'état partagé (AgentState)
│   ├── nodes.py             # Nœuds du graphe (LLM, routeur)
│   └── graph.py             # Construction et compilation du graphe
└── api/
    ├── __init__.py
    └── routes.py            # Endpoints FastAPI + schémas Pydantic
```

---

## API Reference

### `GET /`
Vérifie que l'API est opérationnelle.

**Réponse**
```json
{
  "status": "ok",
  "message": "Agent IA opérationnel"
}
```

---

### `POST /api/chat`
Envoie un message à l'agent et reçoit une réponse complète.

**Body**
```json
{
  "message": "Quelle météo à DAKAR ?",
  "history": [],
  "system_prompt": "Tu es un assistant utile et concis."
}
```

| Champ | Type | Requis | Description |
|---|---|---|---|
| `message` | `string` | ✅ | Le message de l'utilisateur |
| `history` | `list[dict]` | ❌ | Historique `[{role, content}]` |
| `system_prompt` | `string` | ❌ | Comportement de l'agent |

**Réponse**
```json
{
  "response": "Il fait 27°C et ensoleillé à Dakar.",
  "history": [
    { "role": "user", "content": "Quelle météo à Dakar ?" },
    { "role": "assistant", "content": "Il fait 27°C et ensoleillé à Dakar." }
  ]
}
```

---

### `POST /api/chat/stream`
Identique à `/api/chat` mais retourne les tokens en temps réel via **Server-Sent Events (SSE)**.

**Body** - identique à `/api/chat`

**Réponse (SSE)**
```
data: {"token": "Il"}
data: {"token": " fait"}
data: {"token": " 27°C"}
data: {"token": " à Dakar."}
data: [DONE]
```

**Exemple avec JavaScript (fetch)**
```javascript
const res = await fetch("http://localhost:8000/api/chat/stream", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: "Quelle météo à Dakar ?" })
});

const reader = res.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const line = decoder.decode(value);
  if (line.startsWith("data: ") && !line.includes("[DONE]")) {
    const { token } = JSON.parse(line.replace("data: ", ""));
    process.stdout.write(token);
  }
}
```

---

## Outils disponibles

L'agent peut appeler les outils suivants de manière autonome selon le besoin :

| Outil | Description | Exemple                     |
|---|---|-----------------------------|
| `recherche_meteo` | Retourne la météo d'une ville | *"Quelle météo à Dakar ?"*  |
| `calculatrice` | Évalue une expression mathématique | *"Combien font 128 * 37 ?"* |

> Pour ajouter un outil, il suffit de décorer une fonction avec `@tool` dans `agent/graph.py` et de l'ajouter à la liste `tools`.

---

## Flux de l'agent

```
                    ┌─────────────┐
                    │   Entrée    │  (message utilisateur)
                    └──────┬──────┘
                           ↓
                    ┌─────────────┐
              ┌────▶│     LLM     │ (GPT-OSS 120B via Groq)
              │     └──────┬──────┘
              │            │
              │     ┌──────▼──────┐
              │     │  Tool call? │
              │     └──────┬──────┘
              │          YES│         NO
              │     ┌──────▼──────┐   │
              │     │    Tools    │   │
              │     └──────┬──────┘   │
              └────────────┘          │
                                      ▼
                               ┌─────────────┐
                               │   Réponse   │
                               └─────────────┘
```

---

## Exemples curl

```bash
# Chat simple
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quelle météo à Dakar ?"}'

# Avec historique
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Et à Matam ?",
    "history": [
      {"role": "user", "content": "Quelle météo à Dakar ?"},
      {"role": "assistant", "content": "Il fait 27°C à Dakar."}
    ]
  }'

# Streaming
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Explique-moi LangGraph en 3 phrases."}'
```