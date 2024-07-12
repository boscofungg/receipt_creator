import os
import string
import time
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
                    print(f"{DN_Number}: DN found!")
                    time1 = time.time()
                    try:
                        model = Ollama(model="llama3")
                        embeddings = OllamaEmbeddings(model="llama3")
                        parser = StrOutputParser()
                        template = """
                        Answer the question based on the context below. If you can't 
                        answer the question, reply "None".

                        Context: {context}

                        Question: {question}
                        """

                        prompt = PromptTemplate.from_template(template)
                        prompt.format(context="Here is some context", question="Here is a question")
                        chain = prompt | model | parser
                        data1 = chain.invoke({"context": text, "question": "Return the date that appeared on this note. do not return anything else including text and conjuntions."})
                        date = data1

                        found = text.find("Total Charges")
                        total = text[found+15:found+25]
                        while total[-1].isdigit() == False:
                            total = total[:-1]

                        data3 = chain.invoke({"context": text, "question": "Who is the insured. do not return anything else including text and conjuntions."})
                        insured = data3
                        if len(insured) < 43:
                            insured1 = insured
                            insured2 = ""
                            insured3 = ""
                            insured4 = ""
                            insured5 = ""
                        elif len(insured) < 86 and len(insured) >= 43:
                            insured1 = insured[:43]
                            insured2 = insured[43:]
                            insured3 = ""
                            insured4 = ""
                            insured5 = ""
                        elif len(insured) < 129 and len(insured) >= 86:
                            insured1 = insured[:43]
                            insured2 = insured[43:86]
                            insured3 = insured[86:]
                            insured4 = ""
                            insured5 = ""
                        elif len(insured) < 172 and len(insured) >= 129:
                            insured1 = insured[:43]
                            insured2 = insured[43:86]
                            insured3 = insured[86:129]
                            insured4 = insured[129:]
                            insured5 = ""
                        else:
                            insured1 = insured[:43]
                            insured2 = insured[43:86]
                            insured3 = insured[86:129]
                            insured4 = insured[129:172]
                            insured5 = insured[172:]

                        found = text.find("Mortgagee")
                        found2 = text[found:].find("To")  
                        d = text[found+18:found2+found]
                        while d[0].isalpha() == False:
                            d = d[1:]
                        d = d.split("\n")
                        product = d[1]
                        i = 0
                        for n in range(len(product)):
                            if product[i] in string.ascii_letters or product[i] == " ":
                                i += 1
                        product = product[0:i]
                        try:
                            PN = d[2]
                            if PN[0].isdigit() == False and PN[0].isalpha() == False:
                                PN = "TBA"
                        except:
                            PN = "TBA"
                        ac = "What is the A/C No. please only return the No. and and exclude all conjunctions."
                        pages = loader.load_and_split()
                        vectorstore = DocArrayInMemorySearch.from_documents(pages, embedding=embeddings)
                        retriever = vectorstore.as_retriever()
                        chain = (
                        {
                            "context": itemgetter("question") | retriever,
                            "question": itemgetter("question"),
                        }
                        | prompt
                        | model
                        | parser
                        )
                        AC_Number = chain.invoke({'question': ac})
                        dn = DN_Number[:-4]

                        context = { 'insured1': insured1, 'insured2': insured2, 'insured3': insured3, 'insured4': insured4, 'insured5': insured5, 'today_date': date, 'total': f'${total}', 'month': date,
                                    'subtotal1': f'${total}', 'product': product,
                                    'DN_Number': dn, 'AC_Number': AC_Number, 'Policy_Number': PN,
                                    }

                        template_loader = jinja2.FileSystemLoader('./')
                        template_env = jinja2.Environment(loader=template_loader)

                        html_template = 'invoice.html'
                        template = template_env.get_template(html_template)
                        output_text = template.render(context)

                        config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
                        output_pdf = f'{DN_Number}'
                        pdfkit.from_string(output_text, output_pdf, configuration=config, css='invoice.css')
                        time2 = time.time()
                        print(f"{DN_Number} completed in {time2 - time1} seconds!")
                    except Exception as error:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(DN + " failed!")
                        print("An exception occurred:", type(error).__name__) # An exception occurred: ZeroDivisionError
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")