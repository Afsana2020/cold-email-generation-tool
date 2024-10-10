__import__('pysqlite3')
import sys
sys.modules['sqlite3']= sys.modules.pop('pysqlite3')

import time
import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📬 Cold Mail Generator")
    st.markdown(
        """
        <div style="background-color:#f0f8ff;padding:15px;border-radius:10px;margin-bottom:20px;">
            <h2 style="text-align:center;color:#4B6584;">Welcome!</h2>
            <p style="text-align:center;color:#2C3A47;font-size:16px;">
                This AI-powered tool helps you craft personalized cold emails for job listings or client outreach. 
                Just enter a job link and we’ll generate custom emails in seconds!
            </p>
            <ul style="color:#2C3A47;text-align:center;font-size:16px;">
                <li>🔗 Enter a job listing URL</li>
                <li>📧 Click <strong>'Submit'</strong> to generate up to 3 emails at once</li>
                <li>💼 Emails are tailored to the job's skills and requirements</li>
            </ul>
            <p style="text-align:center;color:#4B6584;font-size:16px;">
                Effortless email creation for job seekers and businesses! 🚀
            </p>
            <br>
        </div>
        """,
        unsafe_allow_html=True
    )

    url_input = st.text_input("Enter a URL below:", value="")
    submit_button = st.button("Submit")

    if submit_button:

        try:
            progress_bar = st.progress(0)

            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)

            progress_bar.progress(30)

            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            progress_bar.progress(60)

            flag=0
            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                st.subheader("Generated Mail:")
                st.code(email, language='markdown')
                
                flag=1
            if flag==0: st.error("Seems like It's not a job post, Try again!")
            else:
                progress_bar.progress(100)
                st.markdown(
                    """
                    <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;text-align:center;">
                        <h4>🎉 Great! Want more emails?</h4>
                        <p>Click the <strong>'Submit'</strong> button again to generate more emails!</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📬")
    create_streamlit_app(chain, portfolio, clean_text)
