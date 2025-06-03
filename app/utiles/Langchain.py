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
        You are a helpful assistant that cleans and corrects lecture transcriptions.
        The text may contain grammar mistakes, broken sentences, or unstructured content.
        Fix the grammar and complete any broken sentences to make it clearer, without adding extra information.

        Raw transcription:
        {raw_text}

        Cleaned and structured version:
        """
    )

    clean_chain = LLMChain(llm=llm, prompt=clean_prompt)
    cleaned_text = clean_chain.run({"raw_text": transcription})
    return latex_conversion(cleaned_text)

def latex_conversion(cleaned_transcription):
    latex_prompt = PromptTemplate(
    input_variables=["raw_text"],
    template="""
        You are an expert in LaTeX formatting.

        Task:
        Convert **only** the mathematical expressions in the given text into LaTeX. Leave all other text exactly as it is.

        Instructions:
        - Replace math phrases like "a squared plus b squared equals c squared" with LaTeX-formatted inline math: \( a^2 + b^2 = c^2 \)
        - Keep all non-math content unchanged (e.g., introductions, explanations, titles).
        - Use \( ... \) for inline equations.
        - Do not wrap the whole text in \\documentclass or any LaTeX boilerplate — only convert equations.
        - Return only the modified text.

        Input:
        \"\"\"
        {raw_text}
        \"\"\"
        """
    )
    latex_chain = LLMChain(llm=llm, prompt=latex_prompt)
    output = latex_chain.run({"raw_text": cleaned_transcription})
    print("latex output::\n",output)
    return output


def summary_fn(sum_inp):
    lecture_summary_prompt = PromptTemplate(
    input_variables=["raw_text"],
    template="""
        You are an assistant that summarizes class lectures.

        Given the following raw transcript of a lecture, generate a clear and concise summary. The raw input may contain:
        - Spoken or conversational language
        - Minor repetition or filler words
        - Mixed topics or transitions

        Instructions:
        - Identify the **main topic(s)** of the lecture.
        - List out the **key points**, concepts, or examples discussed.
        - Use clear and concise language.
        - Output should be in paragraph form or bullet points (if appropriate).
        - Do not include irrelevant filler content or broken sentences.
        - Do not hallucinate extra content — only summarize what's in the transcript.

        Transcript:
        \"\"\"
        {raw_text}
        \"\"\"

        Summary:
        """
    )
    summary_chain = LLMChain(llm=llm, prompt=lecture_summary_prompt)
    sum_output = summary_chain.run({"raw_text": sum_inp})
    return sum_output

raw_text = """
This document explains the integration .
The equation is: integral of a from 0 to 7 dx Now consider the formula for the area of a circle: pi times r squared.
"""
sum_inp = """
Alright, so today we're going to dive into the concept of linear regression, which is one of the fundamental algorithms in supervised machine learning. Basically, linear regression is used to predict a dependent variable based on the value of one or more independent variables. So when we say simple linear regression, we mean there's just one input variable, and the model tries to fit a straight line that best represents the relationship between the input and the output. The equation we use here is y equals mx plus b, where m is the slope of the line and b is the y-intercept. Now, we estimate these parameters — m and b — using a method called least squares, which minimizes the sum of squared differences between the predicted values and the actual data points. It's important to remember that linear regression makes certain assumptions, like the relationship between the variables is linear, the residuals are normally distributed, and there's little or no multicollinearity. We also talked about the R-squared value, which tells us how well the model explains the variance in the data. An R-squared value closer to 1 indicates a better fit. During the second half of the class, we also briefly discussed multiple linear regression, where you have more than one input variable. In that case, the model extends to y equals b0 plus b1x1 plus b2x2 and so on. And just a quick reminder, before applying linear regression, always visualize your data and check for outliers because they can significantly affect your model. Any questions on this?

"""







# print("Summary output:\n",sum_output)



# print("Latex output:\n",output)


# print("Input variables: ",latex_prompt.input_variables)  # Should show ['raw_text']
