# from langchain.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
import secrets
import time
import json
import boto3
import io
from botocore.exceptions import ClientError

def upload_file(chroma_client, collection_name, openai_embed_function, texts, filename):
    collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=openai_embed_function)
    pdfname_collection = chroma_client.get_or_create_collection(name=collection_name+"pdf")
    hash = generate_unique_string()
    pdfname_collection.add(ids=filename, metadatas={"hash": hash}, embeddings = [0])
    collection.add(documents=[text.page_content for text in texts], metadatas=[{"hash": hash} for i in range(len(texts))], ids=[filename + str(i) for i in range(len(texts))])

def generate_unique_string():
    timestamp = str(int(time.time()))
    random_part = secrets.token_hex(8)
    return timestamp + random_part

def delete_embeddings(pdfname_collection, collection, filename):
    hash = pdfname_collection.get(ids=[filename])["metadatas"][0]["hash"]
    collection.delete(where={"hash": {"$eq": hash}})
    pdfname_collection.delete(where={"hash": {"$eq": hash}})

def respond(chroma_client, collection_name, message):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    custom_func = OpenAIEmbeddings()
    vectorchrom = Chroma(client=chroma_client, collection_name=collection_name, embedding_function=custom_func)
    qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0), vectorchrom.as_retriever(), memory=memory)
    return qa.run(message)

def get_secret(sn, key):
    secret_name = sn
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret_string = get_secret_value_response['SecretString']
    
    try:
        secret_dict = json.loads(secret_string)
        return secret_dict.get(key)
    except json.JSONDecodeError:
        return secret_string