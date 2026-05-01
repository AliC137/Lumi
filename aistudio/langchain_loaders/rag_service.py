import subprocess
import sys
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
#from langchain_community.llms import Ollama
from langchain_core.documents import Document
from datetime import date
import locale


def restart_ollama_linux():
    """Optional: only on Linux servers where systemd manages Ollama."""
    if sys.platform != "linux":
        return
    try:
        subprocess.run(["sudo", "systemctl", "restart", "ollama"], check=True)
        print("Ollama service restarted successfully on Linux.")
    except subprocess.CalledProcessError as e:
        print(f"Error restarting Ollama service on Linux: {e}")
    except FileNotFoundError:
        print("Error: 'sudo' or 'systemctl' command not found. Ensure they are in your PATH.")

# Call the function to restart Ollama
# restart_ollama_linux()

class RAGService:
    def __init__(self, hf_model_name="sentence-transformers/all-MiniLM-L6-v2", ollama_model_name="deepseek-r1:latest"):
        self.embeddings = HuggingFaceEmbeddings(model_name=hf_model_name)
        self.vectorstore = None
        self.ollama_model_name = ollama_model_name
        self.qa_chain = None
        self.base_url = "http://91.218.114.141:11434"
        self.llm = OllamaLLM(base_url = self.base_url, model=self.ollama_model_name)

    def get_llm(self):
        """Return LLM instance — do not restart Ollama on every call (was causing long hangs / 504 on upload)."""
        if self.llm is None:
            self.llm = OllamaLLM(base_url=self.base_url, model=self.ollama_model_name)
        return self.llm

    def get_date(self):
        """Neutral English date for prompts (Russian locale biased answers toward Russian)."""
        try:
            locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
            out = date.today().strftime("%A, %d %B %Y")
            locale.setlocale(locale.LC_ALL, "")
            return out
        except (locale.Error, OSError):
            return date.today().strftime("%Y-%m-%d")

    def _ensure_qa_chain(self) -> None:
        """Build retrieval chain when needed (first query after ingest), not during upload."""
        if self.vectorstore is None:
            return
        retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        prompt = PromptTemplate.from_template(
            """
Use ONLY the following context to answer the question.
If the answer is not in the context, reply exactly: I don't know.

Important:
- Respond in the SAME language as the user's question (English question → English answer; Russian → Russian; etc.).
- The context may be in any language; translate ideas into the user's language when needed.
- Be concise and helpful.

Today is {current_data}.

Context:
{context}

Question: {question}
Answer:""",
            partial_variables={"current_data": self.get_date()},
        )
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.get_llm(),
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True,
        )

    def add_documents(self, documents, id=None):
        """Ingest only — fast HTTP response. Chain is built lazily on first ``query``."""
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vectorstore.add_documents(documents)
        self.qa_chain = None

    def common_context(self, document):

        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(document, self.embeddings)
        else:
            self.vectorstore.add_documents(document)
        # Use a strict prompt

        self.qa_chain = None

    def query(self, question: str, k=3) -> str:
        if self.vectorstore is None:
            return "No documents uploaded yet."
        if self.qa_chain is None:
            self._ensure_qa_chain()
        if self.qa_chain:
            try:
                result = self.qa_chain.invoke({"query": question})
                return result["result"]
            except Exception as e:
                print("🔴 RAG failed, falling back to Ollama:", e)

        # Fallback if no vectorstore or RAG chain
#        ollama_llm = Ollama(base_url = self.base_url, model=self.ollama_model_name)
#        return ollama_llm.invoke(question)
        return None

    def forget(self):
        self.qa_chain = None
        self.vectorstore = None
