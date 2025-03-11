import os
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
# from langchain_community.embeddings import GPT4AllEmbeddings
# from langchain_openai import OpenAIEmbeddings
# from openai import OpenAI
import streamlit as st

# As variáveis de ambiente são carregadas automaticamente do arquivo .streamlit/secrets.toml

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004", 
    task_type="retrieval_document",
    google_api_key=st.secrets["secrets"]["GOOGLE_API_KEY"]
)


chunk_size = 10
percentual_overlap = 0.2

criar_db = True

def open_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            contents = file.read()
        return contents
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"Error: {e}"

if criar_db:
    arquivo = "finup_ajudAI_investimentos.md"
    

    texto = open_file(arquivo)
    filename = os.path.basename(arquivo)
    metadatas = [{"nome do arquivo": filename}]


    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=chunk_size,
    #text_splitter = RecursiveCharacterTextSplitter(separators=["}\n{"],chunk_size=chunk_size,
                                        chunk_overlap=int(chunk_size * percentual_overlap),
                                        length_function=len,
                                        is_separator_regex=False,
                                        )


    all_splits = text_splitter.create_documents([texto], metadatas=metadatas)
    #for index, text in enumerate(all_splits):
    #    print("#####", index + 1, "#####")
    #    print(text.page_content)
    #    print(text.metadata)

    vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings, persist_directory="chroma")

else:
    print("Não criou o BD")
    vectorstore = Chroma(embedding_function=embeddings, persist_directory="chroma")

#question = "Quantos parâmetros tem o maior modelo Llama 3.1?"
#question = "Qual o maior Lhama?"
question = "Quais os tamanhos dos modelos Llama?"

docs_with_scores = vectorstore.similarity_search_with_score(question, k=4)
docs = [doc for doc, score in docs_with_scores]


def enviar_pergunta(question):
    try:
        # Envia a pergunta para a API
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            convert_system_message_to_human=True,
            google_api_key=st.secrets["secrets"]["GOOGLE_API_KEY"]
        )
        chain = load_qa_chain(llm, chain_type="stuff")
        
        resposta = chain.run(input_documents=docs, question=question)
        
        return resposta
    
    except Exception as e:
        return f"Ocorreu um erro: {e}"
    
resposta = enviar_pergunta(question + " \nUse os dados a seguir como referencia para a resposta" + str(docs))
print("Resposta: ", resposta)


