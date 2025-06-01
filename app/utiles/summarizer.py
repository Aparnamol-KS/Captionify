from transformers import pipeline, BartForConditionalGeneration, BartTokenizer
import torch

class TextSummarizer:
    def __init__(self):
        """Initialize the TextSummarizer class with model configurations."""
        self.device = 0 
        self.model_name = "facebook/bart-large-cnn" 
        self.model = None
        self.tokenizer = None
        self.summarizer = None

    def initialize_model(self):
        """Lazy initialization of the summarization model to avoid blocking app startup."""
        if self.model is None or self.tokenizer is None or self.summarizer is None:
            print("Initializing BART Summarization Model...")
            self.model = BartForConditionalGeneration.from_pretrained(self.model_name).to(self.device)
            self.tokenizer = BartTokenizer.from_pretrained(self.model_name)
            # Create a summarization pipeline using the model and tokenizer
            self.summarizer = pipeline(
                "summarization",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1 
            )

    def calculate_dynamic_length(self, text, min_summary_ratio=0.2, max_summary_ratio=0.4):
        """
        Dynamically calculate min_length and max_length for summarization based on input text length.
        Args:
            text (str): Input text to summarize.
            min_summary_ratio (float): Minimum length ratio for the summary.
            max_summary_ratio (float): Maximum length ratio for the summary.
        Returns:
            tuple: (min_length, max_length) for the summary.
        """
        input_length = len(text.split())  
        min_length = max(10, int(input_length * min_summary_ratio))  
        max_length = max(20, int(input_length * max_summary_ratio)) 
        return min_length, max_length

    def split_into_paragraphs(self, text, max_paragraph_length=512):
        """
        Splits the input text into smaller chunks (paragraphs) to maintain context.
        Args:
            text (str): The input text to be split.
            max_paragraph_length (int): Maximum length of each paragraph in characters.
        Returns:
            list: List of split paragraphs for easier summarization.
        """
        paragraphs = []
        current_paragraph = ""
        sentences = text.split(". ")  
        for sentence in sentences:
            # Add sentence to current paragraph if it doesn't exceed the max length
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
        Summarizes the input text using a pre-trained BART model.
        Args:
            text (str): The input text to summarize.
            min_summary_ratio (float): Minimum summary length ratio.
            max_summary_ratio (float): Maximum summary length ratio.
            batch_size (int): Number of text chunks to process in a batch.
        Returns:
            str: The summarized version of the text.
        """
        if not text.strip():
            return "No text provided for summarization."
        self.initialize_model()
        chunks = self.split_into_paragraphs(text)
        summaries = []
        for chunk in chunks:
            min_length, max_length = self.calculate_dynamic_length(chunk, min_summary_ratio, max_summary_ratio)
            summary = self.summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False, batch_size=batch_size)
            summaries.append(summary[0]['summary_text']) 
        final_summary = " ".join(summaries)
        return final_summary
