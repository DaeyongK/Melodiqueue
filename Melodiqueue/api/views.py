from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from urllib.parse import unquote
from allauth.socialaccount.models import SocialAccount
from langchain.document_loaders import PyMuPDFLoader
import tempfile

from langchain.text_splitter import RecursiveCharacterTextSplitter

from .forms import UploadFileForm
from .ingest import upload_file, generate_unique_string, delete_embeddings, respond, get_secret
import os
import chromadb
from chromadb.utils import embedding_functions

os.environ['OPENAI_API_KEY'] = get_secret("openai", "OPENAI_API_KEY")
chroma_client = chromadb.HttpClient(host='52.71.253.7', port=8000)
openai_embed_function = embedding_functions.OpenAIEmbeddingFunction(get_secret("openai", "OPENAI_API_KEY"))

def index(request):
    return render(request, "index.html")

def main(request):
    request.session["id"] = SocialAccount.objects.filter(user=request.user, provider='google').first().extra_data["sub"]
    pdfname_collection = chroma_client.get_or_create_collection(name=request.session["id"]+"pdf")
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(request.FILES["file"].read())
                temp_file_path = temp_file.name
                loader = PyMuPDFLoader(temp_file_path)
                documents = loader.load()
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20, length_function=len, is_separator_regex=False)
                texts = text_splitter.split_documents(documents)
                upload_file(chroma_client, request.session["id"], openai_embed_function, texts, request.FILES["file"].name)
                temp_file.close()
                os.unlink(temp_file_path)
    else:
        form = UploadFileForm()
    file_list = pdfname_collection.get()["ids"]
    return render(request, "main.html", {'form': form, 'file_list': file_list})

def delete_file(request):
    if request.method == 'POST':
        filename = request.POST.get('filename')
        pdfname_collection = chroma_client.get_or_create_collection(name=request.session["id"]+"pdf")
        collection = chroma_client.get_or_create_collection(name=request.session["id"], embedding_function=openai_embed_function)
        delete_embeddings(pdfname_collection, collection, filename)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})
    
def logout_view(request):
    logout(request)
    return redirect("/")

def generate_response(request, user_input):
    query = str(unquote(user_input))
    result = respond(chroma_client, request.session["id"], query)
    return JsonResponse({'result': result})

def handler404(request, *args, **argv):
    return render(request, "error.html", {"error_message": "We couldn't find your page! Try navigating through Queread through our given interface."})

def handler500(request, *args, **argv):
    return render(request, "error.html", {"error_message": "There seems to have been an internal server error. If the issue continues, please contact the site admin!"})

