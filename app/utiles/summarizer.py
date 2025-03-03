from transformers import pipeline, BartForConditionalGeneration, BartTokenizer
import torch

class TextSummarizer:
    def __init__(self):
        self.device = 0  # Force summarizer to run on CPU (optional, change to "cuda" if needed)
        print(f"Summarizer will run on: {self.device}")

        self.model_name = "facebook/bart-large-cnn"
        self.model = None  # Lazy loading
        self.tokenizer = None
        self.summarizer = None

    def initialize_model(self):
        """Lazy initialization to avoid blocking app startup."""
        if self.model is None or self.tokenizer is None or self.summarizer is None:
            print("Initializing BART Summarization Model...")
            self.model = BartForConditionalGeneration.from_pretrained(self.model_name).to(self.device)
            self.tokenizer = BartTokenizer.from_pretrained(self.model_name)
            self.summarizer = pipeline(
                "summarization",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1  # Use CPU (-1), change to 0 if running on GPU
            )

    def calculate_dynamic_length(self, text, min_summary_ratio=0.2, max_summary_ratio=0.4):
        """
        Dynamically calculate min_length and max_length based on input text length.
        """
        input_length = len(text.split())  # Count words
        min_length = max(10, int(input_length * min_summary_ratio))
        max_length = max(20, int(input_length * max_summary_ratio))
        return min_length, max_length

    def split_into_paragraphs(self, text, max_paragraph_length=512):
        """
        Split the text into manageable chunks while maintaining context.
        """
        paragraphs = []
        current_paragraph = ""
        sentences = text.split(". ")  # Split into sentences

        for sentence in sentences:
            if len(current_paragraph) + len(sentence) <= max_paragraph_length:
                current_paragraph += sentence + ". "
            else:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = sentence + ". "
        
        if current_paragraph:
            paragraphs.append(current_paragraph.strip())
        
        return paragraphs

    def summarize(self, text, min_summary_ratio=0.2, max_summary_ratio=0.4, batch_size=4):
        """
        Summarize text using dynamic length calculation and context-aware chunking.
        """
        if not text.strip():
            return "No text provided for summarization."

        self.initialize_model()  # Ensure the model is loaded only when needed

        # Split text into paragraphs/chunks
        chunks = self.split_into_paragraphs(text)
        
        # Summarize each chunk
        summaries = []
        for chunk in chunks:
            min_length, max_length = self.calculate_dynamic_length(chunk, min_summary_ratio, max_summary_ratio)
            summary = self.summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False, batch_size=batch_size)
            summaries.append(summary[0]['summary_text'])
        
        # Combine summaries
        final_summary = " ".join(summaries)
        return final_summary
