from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
import re
import openai
import os

class openaiintegration:
    def __init__(self) -> None:
        self.embeddings = OpenAIEmbeddings()
    def split_into_chunks(self, raw_text, separator='\n'):
        text_splitter = CharacterTextSplitter(
            separator = separator,
            chunk_size = 1000,
            chunk_overlap = 150,
            length_function = len,
        )
        texts = text_splitter.split_text(raw_text)
        self.embedding(texts)
    
    def embedding(self, texts):
        self.docsearch = FAISS.from_texts(texts, self.embeddings)
        self.chain = load_qa_chain(OpenAI(), chain_type="stuff")
    
    def question(self, query: str):
        docs = self.docsearch.similarity_search(query)
        return self.chain.run(input_documents=docs, question=query)

    def formQuestion3(self,numberOfQuestions: str):
        covered_topic = self.question("Point out the topics covered in the context, give me only the points")
        covered_topics = covered_topic.replace("\n-",",")
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = [{"role":"system","content":"You are a good openai chat assistant who can generate complex questions based on the topics which user gives"},
                        {"role":"user", "content":"".join(['Generate ', numberOfQuestions,' very complex questions based on the topics ',covered_topics])}]
        )
        responseFromGPT = response.choices[0].message.content
        print(type(responseFromGPT), responseFromGPT)
        result = self.limitQuestions(responseFromGPT, int(numberOfQuestions))
        return result
    
    #To limit number of questions even if we get more number of questions from GPT
    def limitQuestions(self, response:str, numberOfQuestions:int):
        print(response,777777777777777777, numberOfQuestions)
        print(response.split('\n\n'))
        # Splitting the string based on integer bullets
        bullets = [str(i) + '.' for i in range(1, 10)]
        delimiter = '|'.join(bullets)
        print("Bullets are :", bullets)

        # Using str.split() with the custom delimiter
        items = re.split(delimiter, response)
        items = [item.strip() for item in items if item.strip()]

        newArray = []
        for i in range(0,len(items)):
            if(i<numberOfQuestions ):
                newArray.append(str(i+1) + ". " + items[i])
            else:
                break
        return "\n\n".join(newArray)