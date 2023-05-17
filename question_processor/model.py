from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import ElasticVectorSearch, Pinecone, Weaviate, FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from question_processor.openaifile import openaiintegration
import os



os.environ["OPENAI_API_KEY"] = "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"
obj = None

class pdf_analysis:
    covered_topics = ""
    raw_text = ""
    def __init__(self, file_obj) -> None:
        self.embeddings = OpenAIEmbeddings()
        # self.read_pdf(file_obj)
        self.extract_text(file_obj)
    
    def read_pdf(self, file_object):
        self.extract_text(PdfReader(stream=file_object.file))
    
    def extract_text(self, book):
        global obj
        raw_text = ""
        for i, page in enumerate(book.pages):
            text = page.extract_text()
            if text:
                raw_text += text
        obj = openaiintegration()
        obj.split_into_chunks(raw_text)

    def generateQuestion(self, noQuestions:str):
        return obj.formQuestion3(noQuestions)
   
