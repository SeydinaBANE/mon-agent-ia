from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Agent IA - GPT-OSS 120B",
    description="""
## API d'un agent IA propulsé par Groq + LangGraph

### Fonctionnalités
- 💬 Chat avec historique de conversation
- 🔧 Appel d'outils automatique (météo, calculatrice...)
- ⚡ Streaming token par token
- 🧠 Modèle : `openai/gpt-oss-120b` via Groq
    """,
    version="1.0.0",
    contact={
        "name": "BANE IA",
        "email": "cea.baneia@gmail.com"
    },
    license_info={
        "name": "MIT"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok", "message": "Agent IA opérationnel"}