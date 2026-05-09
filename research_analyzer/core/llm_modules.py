from abc import ABC, abstractmethod
import requests
import json
import os
from dotenv import load_dotenv
import time

load_dotenv()

class BaseLLM(ABC):
    @abstractmethod
    def summarize(self, text):
        pass

class HuggingFaceInferenceLLM(BaseLLM):
    AVAILABLE_MODELS = {
        # Original models
        "flan_t5_xxl": "google/flan-t5-xxl",  # General-purpose summarization
        "pegasus_xsum": "google/pegasus-xsum",  # Abstractive summarization
        "led": "allenai/led-large-16384",  # Long document summarization
        "mistral": "mistralai/Mistral-7B-v0.1",  # General-purpose
        "bloomz": "bigscience/bloomz-7b1",  # Multilingual and technical summarization

        # Academic-focused models
        "bart": "facebook/bart-large-xsum",  # Scientific text
        "pegasus_arxiv": "google/pegasus-arxiv",  # ArXiv papers
        "longformer": "allenai/longformer-base-4096",  # Long documents
        "bigbird": "google/bigbird-pegasus-large-arxiv",  # Scientific papers

        # Arabic-specialized models
        "arabic_mt5": "ArabicNLP/mT5-base_ar",  # Arabic base model
        "arabic_bart": "facebook/bart-large-arabic",  # Arabic summarization
        "arabic_pegasus": "google/pegasus-arabic",  # Arabic summarization
        "arabic_nougat": "MohamedRashad/arabic-small-nougat"  # Arabic OCR/text
    }

    def __init__(self, model_key="flan_t5_xxl"):
        self.api_key = os.getenv('HF_API_KEY', '')
        self.model = self.AVAILABLE_MODELS.get(model_key, self.AVAILABLE_MODELS["flan_t5_xxl"])
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    def preprocess_text(self, text):
        """Preprocess text before summarization"""
        # Handle LaTeX equations (preserve them)
        # Basic cleaning while preserving important academic content
        return text

    def chunk_text(self, text, chunk_size=1500):
        """Split text into smaller chunks for processing"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0

        for word in words:
            current_size += len(word) + 1
            if current_size > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word) + 1
            else:
                current_chunk.append(word)

        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    def summarize(self, text):
        if not self.api_key:
            return "Error: HF_API_KEY not set in environment variables"

        # Preprocess text
        processed_text = self.preprocess_text(text)

        # Handle long texts through chunking
        if len(processed_text) > 2048:
            chunks = self.chunk_text(processed_text)
            summaries = []
            for chunk in chunks:
                summary = self._summarize_chunk(chunk)
                summaries.append(summary)
            return " ".join(summaries)
        else:
            return self._summarize_chunk(processed_text)

    def _summarize_chunk(self, text):
        """Internal method to summarize a single chunk of text"""
        max_chars = 2048
        truncated_text = text[:max_chars] + ("..." if len(text) > max_chars else "")

        payload = {
            "inputs": truncated_text,
            "parameters": {
                "max_length": 250,
                "min_length": 100,
                "do_sample": False,
                "early_stopping": True,
                "num_beams": 4,
                "temperature": 0.7,
                "top_k": 50,
                "top_p": 0.95,
                "repetition_penalty": 1.2,
                "length_penalty": 2.0,
                "no_repeat_ngram_size": 3
            }
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)

            if response.status_code == 503:
                time.sleep(20)
                response = requests.post(self.api_url, headers=self.headers, json=payload)

            response.raise_for_status()
            result = response.json()

            if isinstance(result, list):
                return result[0].get('summary_text', result[0].get('generated_text', ''))
            elif isinstance(result, dict):
                return result.get('summary_text', result.get('generated_text', ''))
            else:
                return str(result)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                error_msg += f" | Response: {e.response.text[:200]}"
            return error_msg

def get_available_models():
    """Get all available free models"""
    return {
        # Original models
        'huggingface_flan_t5_xxl': lambda: HuggingFaceInferenceLLM("flan_t5_xxl"),
        'huggingface_pegasus_xsum': lambda: HuggingFaceInferenceLLM("pegasus_xsum"),
        'huggingface_led': lambda: HuggingFaceInferenceLLM("led"),
        'huggingface_mistral': lambda: HuggingFaceInferenceLLM("mistral"),
        'huggingface_bloomz': lambda: HuggingFaceInferenceLLM("bloomz"),

        # Academic models
        'huggingface_bart': lambda: HuggingFaceInferenceLLM("bart"),
        'huggingface_pegasus_arxiv': lambda: HuggingFaceInferenceLLM("pegasus_arxiv"),
        'huggingface_longformer': lambda: HuggingFaceInferenceLLM("longformer"),
        'huggingface_bigbird': lambda: HuggingFaceInferenceLLM("bigbird"),

        # Arabic models
        'huggingface_arabic_mt5': lambda: HuggingFaceInferenceLLM("arabic_mt5"),
        'huggingface_arabic_bart': lambda: HuggingFaceInferenceLLM("arabic_bart"),
        'huggingface_arabic_pegasus': lambda: HuggingFaceInferenceLLM("arabic_pegasus"),
        'huggingface_arabic_nougat': lambda: HuggingFaceInferenceLLM("arabic_nougat")
    }
