import os
import streamlit as st
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

# from langchain_community.embeddings import GPT4AllEmbeddings
# from langchain_openai import OpenAIEmbeddings
# from openai import OpenAI
from dotenv import load_dotenv
from style.style_config import apply_custom_style, COLORS, add_footer

# Aplicar estilo customizado
apply_custom_style()

# Título da página
st.title("❓❔ AjudAI FinUp Investimentos ")

# Carregar variáveis de ambiente
load_dotenv()

# Botão para recarregar a base de conhecimento
# col1, col2 = st.columns([3, 1])
# with col2:
#     if st.button("🔄 Recarregar Base"):
#         if "vectorstore" in st.session_state:
#             del st.session_state.vectorstore
#         if "chat_history" in st.session_state:
#             del st.session_state.chat_history
#         st.rerun()

# Configurar embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004", task_type="retrieval_document"
)

# Parâmetros para divisão do texto
chunk_size = 1000
percentual_overlap = 0.3


# Função para abrir arquivo
def open_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            contents = file.read()
        return contents
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"Error: {e}"


# Inicializar o vectorstore no estado da sessão se não existir
if "vectorstore" not in st.session_state:
    arquivo = "finup_ajudAI_investimentos.md"

    # Obter caminho absoluto para o arquivo
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivo_path = os.path.join(base_path, arquivo)

    texto = open_file(arquivo_path)
    filename = os.path.basename(arquivo)
    metadatas = [{"nome do arquivo": filename}]

    text_splitter = CharacterTextSplitter(
        separator=r"%%%",
        chunk_size=chunk_size,
        chunk_overlap=int(chunk_size * percentual_overlap),
        length_function=len,
        is_separator_regex=True,
    )

    all_splits = text_splitter.create_documents([texto], metadatas=metadatas)

    # Criar ou carregar o vectorstore
    try:
        # Obter caminho absoluto para o diretório chroma
        chroma_path = os.path.join(base_path, "chroma")
        st.session_state.vectorstore = Chroma.from_documents(
            documents=all_splits, embedding=embeddings, persist_directory=chroma_path
        )
    except Exception as e:
        st.error(f"Erro ao criar banco de dados vetorial: {e}")
        st.session_state.vectorstore = None


# Função para enviar pergunta ao modelo
def enviar_pergunta(question, docs):
    try:
        # Envia a pergunta para a API
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            convert_system_message_to_human=True,
            temperature=0.3,
        )

        # Criar um sistema de prompt para o modelo
        system_prompt = """
        Você é um assistente especializado em investimentos e finanças, focado em fornecer informações precisas sobre o dashboard FinUp Investimentos.
        
        Ao responder perguntas:
        1. Use APENAS as informações contidas nos documentos de referência fornecidos.
        2. Se a informação não estiver presente nos documentos, indique claramente que não há informação disponível sobre esse tópico específico.
        3. Seja conciso e direto nas suas respostas.
        4. Forneça detalhes específicos quando disponíveis nos documentos.
        5. Não invente informações que não estejam presentes nos documentos.
        """

        # Configurar a cadeia de QA com o sistema de prompt
        prompt_template = """
        {system_prompt}
        
        Documentos de referência:
        {context}
        
        Pergunta do usuário: {question}
        
        Resposta:
        """

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"],
            partial_variables={"system_prompt": system_prompt},
        )

        chain = load_qa_chain(llm, chain_type="stuff", prompt=PROMPT)

        resposta = chain.run(input_documents=docs, question=question)

        return resposta

    except Exception as e:
        return f"Ocorreu um erro: {e}"


# Inicializar histórico de chat se não existir
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Exibir histórico de chat
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        with st.chat_message("assistant", avatar="images/icons/logo_icon.ico"):
            st.write(message["content"])

# Input do usuário
if prompt := st.chat_input("ajudAI Finup Investimentos Responde..."):
    # Adicionar mensagem do usuário ao histórico
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Exibir mensagem do usuário
    st.chat_message("user").write(prompt)

    # Exibir mensagem do assistente com loading
    with st.chat_message("assistant", avatar="images/icons/logo_icon.ico"):
        message_placeholder = st.empty()

        try:
            if st.session_state.vectorstore:
                # Buscar documentos relevantes
                docs_with_scores = (
                    st.session_state.vectorstore.similarity_search_with_score(
                        prompt, k=8
                    )
                )
                docs = [doc for doc, score in docs_with_scores]

                # Extrair o conteúdo dos documentos para um formato mais legível
                docs_content = "\n\n".join(
                    [
                        f"Documento {i + 1}:\n{doc.page_content}"
                        for i, doc in enumerate(docs)
                    ]
                )

                # Gerar resposta com a pergunta original
                resposta = enviar_pergunta(question=prompt, docs=docs)

                # Exibir resposta
                message_placeholder.write(resposta)

                # Adicionar resposta ao histórico
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": resposta}
                )
            else:
                message_placeholder.write(
                    "Não foi possível carregar a base de conhecimento. Por favor, tente novamente mais tarde."
                )
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": "Não foi possível carregar a base de conhecimento. Por favor, tente novamente mais tarde.",
                    }
                )
        except Exception as e:
            message_placeholder.write(f"Ocorreu um erro: {e}")
            st.session_state.chat_history.append(
                {"role": "assistant", "content": f"Ocorreu um erro: {e}"}
            )


# Adicionar rodapé
# add_footer()
