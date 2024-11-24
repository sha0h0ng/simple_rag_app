from abc import ABC, abstractmethod
import openai
import groq
from llama_index.llms.openai import OpenAI
from llama_index.llms.groq import Groq
from llama_index.llms.gemini import Gemini
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import DeterministicFakeEmbedding
from config import (
    OPENAI_API_KEY,
    GROQ_API_KEY,
    EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE,
    OPENAI_MODEL,
    GEMINI_MODEL,
    GROQ_MODEL,
    OLLAMA_MODEL
)


class BaseLLM(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        pass

    @abstractmethod
    def to_llamaindex_llm(self):
        pass

    def get_embedding_model(self, provider: str = "fake"):
        if provider == "openai":
            return OpenAIEmbedding(
                model=EMBEDDING_MODEL,
                embed_batch_size=EMBEDDING_BATCH_SIZE,
                api_key=OPENAI_API_KEY
            )
        elif provider == "fake":
            return LangchainEmbedding(DeterministicFakeEmbedding(size=4096))
        elif provider == "ollama":
            return LangchainEmbedding(OllamaEmbeddings(model=EMBEDDING_MODEL))
        elif provider == "huggingface":
            return LangchainEmbedding(HuggingFaceEmbeddings(model=EMBEDDING_MODEL))
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")


class OpenAILLM(BaseLLM):
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        self.model = OPENAI_MODEL

    def complete(self, prompt: str) -> str:
        response = openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def to_llamaindex_llm(self):
        return OpenAI(model=self.model)


class GeminiLLM(BaseLLM):
    def __init__(self):
        gemini.api_key = GEMINI_API_KEY
        self.model = GEMINI_MODEL

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def to_llamaindex_llm(self):
        return Gemini(model_name=self.model)


class GroqLLM(BaseLLM):
    def __init__(self):
        self.client = groq.Client(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def to_llamaindex_llm(self):
        return Groq(model_name=self.model)


class OllamaLLM(BaseLLM):
    def __init__(self):
        self.model = OLLAMA_MODEL

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def to_llamaindex_llm(self):
        return Ollama(model=self.model)


class LLMFactory:
    @staticmethod
    def get_llm(provider: str) -> BaseLLM:
        llm_classes = {
            "openai": OpenAILLM,
            "groq": GroqLLM,
            "gemini": GeminiLLM,
            "ollama": OllamaLLM
        }
        if provider in llm_classes:
            return llm_classes[provider]()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
