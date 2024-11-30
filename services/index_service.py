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

    def create_index(self, directory_path=None):
        if directory_path:
            documents = self.document_loader.load_documents(directory_path)
            self.index = VectorStoreIndex.from_documents(
                documents=documents,
                show_progress=True
            )
            return {
                "status": "success",
                "documents_processed": len(documents)
            }
        else:
            # Create an empty index
            self.index = VectorStoreIndex([])
            return {
                "status": "success",
                "documents_processed": 0
            }

    def query_account(self, transaction_data):
        transaction_data = ", ".join(str(item) for item in transaction_data)
        question = (
            "As a financial advisor, analyze the following transaction data and provide a clear spending summary. "
            "Focus on key spending and deposits patterns, category with high spending and potential areas for budget optimization.\n\n"
            f"Transaction Data:\n{transaction_data}\n\n"
            "Requirements:\n"
            "- Keep the summary under 50 words in one paragraph\n"
            "- DO NOT format the response with markdown text \n"
            "- Use plain text only \n"
            "- Highlight the top spending categories\n"
            "- Include any concerning patterns if present\n"
            "- Please note that that transaction data marked as credit is actually a deposit\n"
            "- Do not give any sum value but only percentages and categories\n"
            "- Start your response with 'Here is the summary of your spending:' \n"
        )

        print(question)
        response = self.llm.complete(question)
        return {
            "response": response
        }

    def query(self, question, similarity_top_k=3, template_type="default", use_rag=True):
        if template_type not in self.qa_templates:
            raise ValueError(f"Invalid template type. Choose from: {
                             ', '.join(self.qa_templates.keys())}")

        if use_rag and self.index:
            # RAG approach - using documents
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
        else:
            # Direct LLM approach - no documents
            template = self.qa_templates[template_type]
            formatted_prompt = template.format(query=question)
            response = Settings.llm.complete(formatted_prompt)
            return {
                "response": response.text,
                "source_nodes": []  # Empty since we're not using documents
            }
