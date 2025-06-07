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

raw_text = """
This document explains the integration .
The equation is: integral of a from 0 to 7 dx Now consider the formula for the area of a circle: pi times r squared.
"""
sum_inp = """
Alright, so today we're going to dive into the concept of linear regression, which is one of the fundamental algorithms in supervised machine learning. Basically, linear regression is used to predict a dependent variable based on the value of one or more independent variables. So when we say simple linear regression, we mean there's just one input variable, and the model tries to fit a straight line that best represents the relationship between the input and the output. The equation we use here is y equals mx plus b, where m is the slope of the line and b is the y-intercept. Now, we estimate these parameters — m and b — using a method called least squares, which minimizes the sum of squared differences between the predicted values and the actual data points. It's important to remember that linear regression makes certain assumptions, like the relationship between the variables is linear, the residuals are normally distributed, and there's little or no multicollinearity. We also talked about the R-squared value, which tells us how well the model explains the variance in the data. An R-squared value closer to 1 indicates a better fit. During the second half of the class, we also briefly discussed multiple linear regression, where you have more than one input variable. In that case, the model extends to y equals b0 plus b1x1 plus b2x2 and so on. And just a quick reminder, before applying linear regression, always visualize your data and check for outliers because they can significantly affect your model. Any questions on this?

"""


# exm = "So today we’re going to start by revisiting the concept of quadratic equations, which we’ve already seen in earlier classes. Remember, a standard quadratic equation takes the form a x squared plus b x plus c equals zero, where a, b, and c are real numbers and a is not equal to zero. Now, the most common method we use to solve this is the quadratic formula, which is given by x equals negative b plus or minus the square root of b squared minus four a c, all divided by two a. As I mentioned before, this formula comes from completing the square, and it’s useful in almost every case. Also, keep in mind that the expression under the square root, which is b squared minus four a c, is called the discriminant, and it tells us about the nature of the roots. If it’s positive, we get two real and distinct solutions. If it’s zero, the roots are real and equal. And if it’s negative, the equation has two complex roots. Alright, now shifting gears a bit, let’s talk briefly about distance in two-dimensional space. Suppose we have two points, say x one comma y one and x two comma y two — the distance between them is given by the formula square root of open parenthesis x two minus x one close parenthesis squared plus open parenthesis y two minus y one close parenthesis squared. That’s basically the Pythagorean theorem applied in coordinate geometry. We use this often when analyzing geometric shapes or modeling physical systems. Okay, before we move on, just quickly jot that down and let me know if you need a recap on any of those formulas."


# print(summary_fn(sum_inp))

# print("Summary output:\n",sum_output)



# print("Latex output:\n",output)


# print("Input variables: ",latex_prompt.input_variables)  # Should show ['raw_text']
