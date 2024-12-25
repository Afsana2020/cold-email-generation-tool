from langchain_groq import ChatGroq
from groq._client import Client as GroqClient
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class Chain:
    def __init__(self):
           # Initialize Groq client without `proxies` if necessary
        client = GroqClient(api_key=st.secrets["GROQ_API_KEY"])
        self.llm = ChatGroq(
            model_name="llama-3.1-70b-versatile",
            temperature=0,
            groq_api_key=st.secrets["GROQ_API_KEY"],
            client=client  # Pass the manually created client
        )


    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
                ### SCRAPED TEXT FROM WEBSITE:
                {page_data}
                ### INSTRUCTION:
                The scraped text is from the career's page of a website.
                Your job is to extract the job postings and return them in JSON format containing the 
                following keys: `role`, `experience`, `skills` and `description`.
                Only return the valid JSON.
                ### VALID JSON (NO PREAMBLE):    
                """
        )

        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={'page_data': cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big, Unable to parse jobs")
        return res if isinstance(res,list) else [res]


    def write_mail(self,job,links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Afsana, a business development executive at A.H. Tech. A.H. Tech is an AI & Software Consulting company dedicated to facilitating
            the seamless integration of business processes through automated tools. 
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
            process optimization, cost reduction, and heightened overall efficiency. 
            Your job is to write a cold email to the client regarding the job mentioned above describing the capability of A.H. Tech 
            in fulfilling their needs.
            Also add the most relevant ones from the following links to showcase A.H. Tech's portfolio: {link_list}
            Remember you are Afsana, BDE at A.H. Tech. 
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):

            """
        )

        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content


if __name__ == "__main__":
    print(st.secrets["GROQ_API_KEY"])
