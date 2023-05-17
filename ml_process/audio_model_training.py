import os
import pickle
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

os.environ["OPENAI_API_KEY"] = "" #API key from open AI.

class Models(object):
    def __init__(self, filename):
        self.filename = filename

    def dump(self, chain, docsearch):
        pickle.dump({"chain": chain, "docsearch": docsearch}, open(f'models/{self.filename}.pkl', 'wb'))

    def model(self):
        self.embeddings = OpenAIEmbeddings()
        file_path = os.path.join("extracted_files")
        raw_text = ""
        for file in os.listdir(file_path):
            with open(os.path.join(file_path, file), 'r') as f:
                raw_text += f.read()
        text_splitter = CharacterTextSplitter(
            separator = ' ',
            chunk_size = 1000,
            chunk_overlap = 150,
            length_function = len,
        )
        texts = text_splitter.split_text(raw_text)
        self.docsearch = FAISS.from_texts(texts, self.embeddings)
        self.chain = load_qa_chain(OpenAI(), chain_type="stuff")
        self.dump(self.chain, self.docsearch)
        
    
def get_answer(question: str, model: str):
    data = pickle.load(open(f'models/{model}.pkl', 'rb'))
    chain, docsearch =  data.get("chain"), data.get("docsearch")
    docs = docsearch.similarity_search(question)
    return chain.run(input_documents=docs, question=question)

# if __name__ == "__main__":
#     obj = Models()
#     obj.model()
#     question = lambda t: print(get_answer(t))

#     question("who lost all money")
