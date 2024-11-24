import os
from dotenv import load_dotenv

load_dotenv()

# Dummy API Key Values
DUMMY_API_KEY = "PLEASE_DO_NOT_USE_THIS_KEY"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", DUMMY_API_KEY)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", DUMMY_API_KEY)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", DUMMY_API_KEY)

LLM_PROVIDER = "ollama"
EMBEDDING_PROVIDER = "ollama"

# Document Processing Settings OpenAI Embedding Model
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 200
EMBEDDING_BATCH_SIZE = 100

# Embedding Model (Uncomment the desired model)
# EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI Embedding Model
# EMBEDDING_MODEL = "fake"  # Fake Embedding Model
EMBEDDING_MODEL = "llama3.2:latest"  # Ollama Embedding Model
# EMBEDDING_MODEL = "BAAI/bge-small-en"  # HuggingFace Embedding Model

# LLM Model
OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "models/gemini-1.5-flash"
GROQ_MODEL = "mixtral-8x7b-32768"
OLLAMA_MODEL = "llama3.2:latest"

# QA Templates
DEFAULT_QA_TEMPLATE = """Use the provided context to answer the question and do not use any markdown formatting in your response. Be clear and comprehensive.

Context information is below:
---------------
{context_str}
---------------

Given the context information, answer the following question:
{query_str}

Answer:"""

PROFESSIONAL_QA_TEMPLATE = """As an expert analyst, provide a detailed professional response based on the given context and do not use any markdown formatting in your response.

Context information:
---------------
{context_str}
---------------

Question:
{query_str}

Expert Analysis:"""

CONCISE_QA_TEMPLATE = """Provide a brief, direct answer based on the following context and do not use any markdown formatting in your response.

Context:
---------------
{context_str}
---------------

Question:
{query_str}

Concise Answer:"""

STEP_BY_STEP_QA_TEMPLATE = """Break down your answer into clear steps, using the provided context and do not use any markdown formatting in your response.

Context:
---------------
{context_str}
---------------

Question:
{query_str}

Step-by-step response:
1."""

BANK_TELLER_TEMPLATE = """Act as a helpful bank teller and your name is Genbot. Use the provided context to assist the customer with their banking query.
And please do not use any markdown formatting in your response. And also make it short and concise and if possible less than 50 words.

Context:
---------------
{context_str}
---------------

Customer Question:
{query_str}

Bank Teller Response:"""
