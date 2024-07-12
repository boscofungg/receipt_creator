import os
import string
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from operator import itemgetter
import jinja2
import pdfkit
from datetime import datetime
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import DocArrayInMemorySearch

if __name__ == "__main__":
    for DN in os.listdir("DN"):
        test = 0
        DN_Number = DN
        for filename in os.listdir("Debit Note backup Master File"):
            if filename.endswith('.pdf'):
                if filename == f"{DN_Number}":
                    global path
                    path = "/Users/boscofungg/Desktop/LSC/Crew-main/DN/" + filename
                    global loader
                    loader = PyPDFLoader(path)
                    global text
                    text = extract_text(path, laparams=LAParams())
                    test += 1
                    found = text.find("Mortgagee")
                    found2 = text[found:].find("To")  
                    d = text[found+18:found2+found]
                    while d[0].isalpha() == False:
                        d = d[1:]
                    found = text.find("The insured:")
                    found2 = text[found:].find("\n")
                    print(text[found+13:found2+found])