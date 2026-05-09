from abc import ABC, abstractmethod
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqGeneration, pipeline
import os

class BaseLLM(ABC):
    @abstractmethod
    def summarize(self, text):
        pass

class T5Summarizer(BaseLLM):
    def __init__(self):
        self.model_name = "t5-base"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqGeneration.from_pretrained(self.model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
    def summarize(self, text):
        inputs = self.tokenizer.encode("summarize: " + text, 
                                     return_tensors="pt", 
                                     max_length=1024, 
                                     truncation=True)
        inputs = inputs.to(self.device)
        
        summary_ids = self.model.generate(inputs,
                                        max_length=150,
                                        min_length=40,
                                        length_penalty=2.0,
                                        num_beams=4,
                                        early_stopping=True)
        
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

class BartSummarizer(BaseLLM):
    def __init__(self):
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=0 if torch.cuda.is_available() else -1
        )
        
    def summarize(self, text):
        summary = self.summarizer(text, 
                                max_length=130, 
                                min_length=30, 
                                do_sample=False)
        return summary[0]['summary_text']

def get_available_models():
    """Return a dictionary of available LLM models."""
    models = {
        'T5': T5Summarizer,
        'BART': BartSummarizer
    }
    return models
