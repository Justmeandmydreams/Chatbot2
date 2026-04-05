# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.cosmos import CosmosClient
import uuid, os
from datetime import datetime

app = FastAPI(title="College Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Azure Clients ──────────────────────────────────────────────
openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01"
)

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name="college-knowledge",
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

cosmos_client = CosmosClient(
    os.getenv("COSMOS_ENDPOINT"),
    os.getenv("COSMOS_KEY")
)
db = cosmos_client.get_database_client("chatbot-db")
container = db.get_container_client("conversations")

# ── Models ─────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    sources: list = []

# ── Helpers ────────────────────────────────────────────────────
def search_knowledge_base(query: str) -> tuple[str, list]:
    """Search college knowledge base for relevant context."""
    results = search_client.search(
        search_text=query,
        top=3,
        select=["title", "content", "category"]
    )
    context_parts, sources = [], []
    for r in results:
        context_parts.append(f"[{r['title']}]\n{r['content']}")
        sources.append(r['title'])
    return "\n\n".join(context_parts), sources

def get_conversation_history(session_id: str) -> list:
    """Retrieve last 10 messages from Cosmos DB."""
    try:
        item = container.read_item(item=session_id, partition_key=session_id)
        return item.get("messages", [])[-10:]
    except:
        return []

def save_conversation(session_id: str, messages: list):
    """Save conversation to Cosmos DB."""
    container.upsert_item({
        "id": session_id,
        "session_id": session_id,
        "messages": messages,
        "updated_at": datetime.utcnow().isoformat()
    })

# ── Main Chat Endpoint ─────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    # 1. Search knowledge base
    context, sources = search_knowledge_base(req.message)

    # 2. Get history
    history = get_conversation_history(session_id)

    # 3. Build prompt
    system_prompt = f"""You are a helpful and friendly college assistant chatbot for XYZ Engineering College.
Answer student queries about admissions, fees, courses, facilities, exams, and placements.
Be concise, accurate, and warm. If you don't know something, say "Please contact the college office."

Use this college knowledge base to answer:
{context}"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": req.message})

    # 4. Call Azure OpenAI
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )
    reply = response.choices[0].message.content

    # 5. Save to Cosmos DB
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})
    save_conversation(session_id, history)

    return ChatResponse(reply=reply, session_id=session_id, sources=sources)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "College Chatbot"}