import subprocess
import sys
import threading
import time
import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
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


def normalize_reply_language(code: str | None) -> str:
    """Map API/UI codes to en | ru | tg | auto."""
    if not code:
        return "auto"
    c = code.lower().strip().replace("_", "-")
    if c in ("ru", "ru-ru"):
        return "ru"
    if c in ("en", "en-us", "en-gb"):
        return "en"
    if c in ("tg", "tj", "tj-tj", "tg-tj"):
        return "tg"
    return "auto"


def reply_language_instruction(code: str) -> str:
    """Strong system-style rule so the model does not default to English."""
    c = normalize_reply_language(code)
    if c == "ru":
        return (
            "LANGUAGE (strict): Answer entirely in Russian. "
            "Do not answer in English. Translate any English context into Russian."
        )
    if c == "tg":
        return (
            "LANGUAGE (strict): Answer entirely in Tajik (тоҷикӣ). "
            "Do not answer in English. Translate any English context into Tajik."
        )
    if c == "en":
        return (
            "LANGUAGE (strict): Write the entire answer in English only. "
            "Even if the Context excerpts or prior chat are in Russian or another language, "
            "summarize and translate into English — do not reply in Russian or Tajik."
        )
    return (
        "LANGUAGE (strict): Use exactly the same language as the user's question for the full answer "
        "(Russian → Russian, Tajik → Tajik, English → English). "
        "Do not default to English when the question is not in English."
    )


def strip_model_reasoning(text: str | None) -> str:
    """Remove DeepSeek-R1 / Ollama reasoning blocks and common English meta preambles."""
    if text is None:
        return ""
    t = text.strip()
    if not t:
        return ""

    for tag in ("think", "thinking", "redacted_thinking"):
        t = re.sub(rf"<{tag}>[\s\S]*?</{tag}>", "", t, flags=re.I)
        t = re.sub(rf"<{tag}[\s\S]*?>", "", t, flags=re.I)

    blocks = re.split(r"\n\s*\n", t)
    cyrillic_re = re.compile(r"[\u0400-\u04FF]")
    meta_start_re = re.compile(
        r"(?is)^(Hmm,|Okay, let\'s|The user asked|The user provided|Since the user|"
        r"The request |Let me process|I\'ll structure|I need to provide|"
        r"Step by step|Processing this query)",
    )
    kept: list[str] = []
    seen_kept = False
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        has_cyr = bool(cyrillic_re.search(b))
        looks_like_meta = bool(meta_start_re.search(b[:240])) and len(b) < 1500 and not has_cyr
        if not seen_kept and looks_like_meta:
            continue
        seen_kept = True
        kept.append(b)

    out = "\n\n".join(kept).strip()
    return out if len(out) > 80 else t


class RAGService:
    def __init__(self, hf_model_name="sentence-transformers/all-MiniLM-L6-v2", ollama_model_name="deepseek-r1:latest"):
        self.embeddings = HuggingFaceEmbeddings(model_name=hf_model_name)
        self.vectorstore = None
        self.ollama_model_name = ollama_model_name
        self._faiss_lock = threading.Lock()
        self._ingest_lock = threading.Lock()
        self._ongoing_ingests = 0
        self._ingest_cv = threading.Condition(self._ingest_lock)
        self.base_url = "http://91.218.114.141:11434"
        self.llm = OllamaLLM(base_url=self.base_url, model=self.ollama_model_name)

    def begin_ingest(self) -> None:
        with self._ingest_cv:
            self._ongoing_ingests += 1

    def end_ingest(self) -> None:
        with self._ingest_cv:
            self._ongoing_ingests -= 1
            self._ingest_cv.notify_all()

    def wait_for_ingest_idle(self, timeout: float = 20.0) -> None:
        """Brief wait while background ingest runs — cap avoids multi-minute blocked queries."""
        if self._ongoing_ingests <= 0:
            return
        deadline = time.monotonic() + timeout
        with self._ingest_cv:
            while self._ongoing_ingests > 0 and time.monotonic() < deadline:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self._ingest_cv.wait(timeout=min(remaining, 0.25))

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

    def add_documents(self, documents, id=None, replace: bool = False):
        """Embed into FAISS. Default merges with existing index; replace=True rebuilds index (chat uploads)."""
        with self._faiss_lock:
            if replace:
                if documents:
                    self.vectorstore = FAISS.from_documents(documents, self.embeddings)
                else:
                    self.vectorstore = None
            elif self.vectorstore is None:
                self.vectorstore = FAISS.from_documents(documents, self.embeddings)
            else:
                self.vectorstore.add_documents(documents)

    def common_context(self, document):
        with self._faiss_lock:
            if self.vectorstore is None:
                self.vectorstore = FAISS.from_documents(document, self.embeddings)
            else:
                self.vectorstore.add_documents(document)

    def query(
        self,
        question_for_llm: str,
        reply_language: str = "auto",
        retrieval_query: str | None = None,
    ) -> str | None:
        """
        Vector search uses retrieval_query (short, user-shaped text).
        The LLM sees question_for_llm (may include chat context).
        """
        self.wait_for_ingest_idle(timeout=20.0)
        if self.vectorstore is None:
            return "No documents uploaded yet."

        lang = normalize_reply_language(reply_language)
        lang_rule = reply_language_instruction(lang)
        rq = (retrieval_query or question_for_llm).strip()
        if not rq:
            rq = question_for_llm.strip()

        with self._faiss_lock:
            docs = self.vectorstore.similarity_search(rq, k=12)

        context = "\n\n---\n\n".join(d.page_content for d in docs if d.page_content)
        if not context.strip():
            return None

        prompt = f"""{lang_rule}

GROUNDING (critical — follow strictly):
- Use ONLY information supported by the Context excerpts below (uploaded materials).
- Do NOT invent textbook facts, dates, or chapter contents that are not clearly stated in Context.
- If Context does not contain the requested chapter or topic, say clearly that the excerpts do not cover it and avoid filling gaps from general knowledge.
- Output ONLY the final answer for the reader: no planning, no phrases like "the user asked", "step by step", "Hmm," or internal reasoning.

Formatting:
- Follow LANGUAGE above for the entire answer.
- Be concise; use headings only if helpful.

Today is {self.get_date()}.

Context:
{context}

User message (may include prior chat turns for reference only; facts must still come from Context):
{question_for_llm.strip()}

Repeat LANGUAGE rule: {lang_rule}

Answer (no language other than specified above):"""

        try:
            raw = self.get_llm().invoke(prompt)
            text = raw.content if hasattr(raw, "content") else str(raw)
            return strip_model_reasoning(text)
        except Exception as e:
            print("🔴 RAG LLM invoke failed:", e)
            return None

    def forget(self):
        self.vectorstore = None
