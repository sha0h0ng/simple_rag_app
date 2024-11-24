from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.prompts import PromptTemplate
from services.llm_service import LLMFactory
from services.document_loader import DocumentLoader
from config import (
    LLM_PROVIDER,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    DEFAULT_QA_TEMPLATE,
    PROFESSIONAL_QA_TEMPLATE,
    CONCISE_QA_TEMPLATE,
    STEP_BY_STEP_QA_TEMPLATE,
    BANK_TELLER_TEMPLATE,
    EMBEDDING_PROVIDER
)


class IndexService:
    def __init__(self):
        self.llm = LLMFactory.get_llm(LLM_PROVIDER)
        self.document_loader = DocumentLoader()

        Settings.llm = self.llm.to_llamaindex_llm()
        Settings.embed_model = self.llm.get_embedding_model(EMBEDDING_PROVIDER)
        Settings.node_parser = SimpleNodeParser.from_defaults(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

        # Initialize prompt templates
        self.qa_templates = {
            "default": PromptTemplate(DEFAULT_QA_TEMPLATE),
            "professional": PromptTemplate(PROFESSIONAL_QA_TEMPLATE),
            "concise": PromptTemplate(CONCISE_QA_TEMPLATE),
            "step_by_step": PromptTemplate(STEP_BY_STEP_QA_TEMPLATE),
            "bank_teller": PromptTemplate(BANK_TELLER_TEMPLATE),
        }

        # Start with empty index
        self.index = None

    def create_index(self, directory_path):
        documents = self.document_loader.load_documents(directory_path)
        self.index = VectorStoreIndex.from_documents(
            documents=documents,
            show_progress=True
        )
        return {
            "status": "success",
            "documents_processed": len(documents)
        }

    def query(self, question, similarity_top_k=3, template_type="default"):
        if not self.index:
            raise ValueError("No documents have been indexed yet")

        if template_type not in self.qa_templates:
            raise ValueError(f"Invalid template type. Choose from: {
                             ', '.join(self.qa_templates.keys())}")

        query_engine = self.index.as_query_engine(
            similarity_top_k=similarity_top_k,
            text_qa_template=self.qa_templates[template_type],
            streaming=False
        )
        response = query_engine.query(question)

        return {
            "response": response.response,
            "source_nodes": [
                {
                    "text": node.node.text,
                    "score": node.score,
                    "metadata": node.node.metadata
                } for node in response.source_nodes
            ]
        }
