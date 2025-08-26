import os
from typing import List, Optional
from groq import Groq
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load the variables from config.env
load_dotenv("config.env")

# Access the API key
GROQ_KEY = os.getenv("GROQ_API_KEY")

class GroqLLM(LLM):
    model: str = "llama3-8b-8192"
    api_key: str = GROQ_KEY
    temperature: float = 0.0

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        client = Groq(api_key=self.api_key)

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )

        return response.choices[0].message.content

    @property
    def _llm_type(self) -> str:
        return "groq-llm"

llm = GroqLLM(model="llama3-8b-8192", api_key=GROQ_KEY, temperature=0.7)

#Defining prompt templates


def clean_transcription(transcription):
    clean_prompt = PromptTemplate(
    input_variables=["raw_text"],
    template="""
You are a transcription cleaner.

Task:
Fix grammar mistakes, broken sentences, and unstructured text in the given lecture transcription. Make the sentences clear and complete — but do not add, summarize, or explain anything.

Rules:
- Keep the original meaning and structure.
- Return only the cleaned paragraph without any explanations, labels, or headings.
- Do not include any prefix like "Cleaned text:" or wrap the output in quotes.

Input:
{raw_text}

Output:
        """
    )

    clean_chain = LLMChain(llm=llm, prompt=clean_prompt)
    cleaned_text = clean_chain.run({"raw_text": transcription})
    return latex_conversion(cleaned_text)

def latex_conversion(cleaned_transcription):
    latex_prompt = PromptTemplate(
        input_variables=["raw_text"],
        template="""
You are a LaTeX converter.

Task:
Replace only the spoken mathematical expressions in the following paragraph with correct LaTeX format using inline math delimiters like \\( ... \\).

Rules:
- Only convert math-related parts (e.g., "x squared plus y squared equals z squared" becomes \\(x^2 + y^2 = z^2\\)).
- Do not change any other part of the text.
- Do not reword or summarize the paragraph.
- Do not include any additional text like "Here is your result" or triple quotes.
- Return the full updated paragraph with math converted, and nothing else.
- Always use standard LaTeX syntax.
- For square roots, always use \sqrt{...}.
- For powers, always use ^{...}.

Input:
{raw_text}

Output:
"""
    )

    latex_chain = LLMChain(llm=llm, prompt=latex_prompt)
    output = latex_chain.run({"raw_text": cleaned_transcription})

    return output


def summary_fn(sum_inp):
    lecture_summary_prompt = PromptTemplate(
    input_variables=["raw_text"],
    template="""
You are a summarizer for class lectures.

Given a raw lecture transcript, cleanly extract and present the key points or concepts discussed. Focus only on the actual content of the transcript.

Rules:
- Remove repetition and filler words.
- Keep only meaningful academic content.
- Present the summary in clean paragraph form or bullet points.
- Do not include any explanation, instruction, headers, or labels in the output.
-Do not include any additional text like "Here is your result" or triple quotes.
- Return the result only, nothing else.

Transcript:
\"\"\" 
{raw_text} 
\"\"\"
       """
    )
    summary_chain = LLMChain(llm=llm, prompt=lecture_summary_prompt)
    sum_output = summary_chain.run({"raw_text": sum_inp})
    return sum_output
