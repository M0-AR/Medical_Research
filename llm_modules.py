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
        # General purpose models
        "flan_t5": "google/flan-t5-large",  # More stable than xxl
        "pegasus_xsum": "google/pegasus-xsum",  # Verified working
        "mistral": "mistralai/Mistral-7B-Instruct-v0.2",  # Latest stable version
        "bloomz": "bigscience/bloomz-560m",  # Smaller but stable version

        # Academic-focused models
        "bart_cnn": "facebook/bart-large-cnn",  # Verified for summarization
        "pegasus_pubmed": "google/pegasus-pubmed",  # Medical papers
        "led_base": "allenai/led-base-16384",  # Long document processing
        "bigbird_pegasus": "google/bigbird-pegasus-large-pubmed",  # Scientific papers

        # Arabic-specialized models
        "arabic_mt5": "marefa-nlp/marefa-mt5-base",  # Verified Arabic base
        "arabert": "aubmindlab/arabert-base-v2",  # Modern Arabic
        "camelbert": "CAMeL-Lab/bert-base-arabic-camelbert-mix",  # Mixed Arabic
        "ara_t5": "araT5/araT5-base-title-generation"  # Arabic generation
    }

    def __init__(self, model_key="flan_t5"):
        self.api_key = os.getenv('HF_API_KEY', '')
        self.model = self.AVAILABLE_MODELS.get(model_key, self.AVAILABLE_MODELS["flan_t5"])
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
        # General purpose models - Working  
        'huggingface_flan_t5': lambda: HuggingFaceInferenceLLM("flan_t5"),  
        'huggingface_pegasus_xsum': lambda: HuggingFaceInferenceLLM("pegasus_xsum"),  
        'huggingface_mistral': lambda: HuggingFaceInferenceLLM("mistral"),  
        # 'huggingface_bloomz': lambda: HuggingFaceInferenceLLM("bloomz"),  # Need fixing  

        # Academic models - Working  
        'huggingface_bart_cnn': lambda: HuggingFaceInferenceLLM("bart_cnn"),  
        'huggingface_pegasus_pubmed': lambda: HuggingFaceInferenceLLM("pegasus_pubmed"),  
        'huggingface_led_base': lambda: HuggingFaceInferenceLLM("led_base"),  
        'huggingface_bigbird_pegasus': lambda: HuggingFaceInferenceLLM("bigbird_pegasus"),  

        # Arabic models - Need fixing  
        # 'huggingface_arabic_mt5': lambda: HuggingFaceInferenceLLM("arabic_mt5"),  
        # 'huggingface_arabert': lambda: HuggingFaceInferenceLLM("arabert"),  
        # 'huggingface_camelbert': lambda: HuggingFaceInferenceLLM("camelbert"),  
        # 'huggingface_ara_t5': lambda: HuggingFaceInferenceLLM("ara_t5")  
    }