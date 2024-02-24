from pypdf import PdfReader
import docx
import json
from sentence_transformers import SentenceTransformer
from ctransformers import AutoModelForCausalLM
from openai import OpenAI
import datetime

# Function to read PDF files
def read_pdf(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    except:
        text = ''
    return text

# Function to read DOCX files
def read_docx(file_path):
    text = ""
    doc = docx.Document(file_path)
    for paragraph in doc.paragraphs:
        text += paragraph.text
    return text


def load_settings():
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                OPENAI_API_KEY = settings.get("OPENAI_API_KEY", "")
                model_type = settings.get("model_type", "small")
                llm_model = settings.get("llm_model", "OpenAI api")
        except FileNotFoundError:
            OPENAI_API_KEY = ""
            model_type = "small"
            llm_model = "OpenAI api"
        return([OPENAI_API_KEY, model_type, llm_model])

def initialize_openai_and_embedding(OPENAI_API_KEY, model_type, llm_model):
             
        if OPENAI_API_KEY and llm_model == "OpenAI api":
            client = OpenAI(api_key=OPENAI_API_KEY)
        elif llm_model == "Tinyllama(Q5)":
            client = AutoModelForCausalLM.from_pretrained("TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF", model_file="tinyllama-1.1b-chat-v1.0.Q5_K_M.gguf", model_type="llama", gpu_layers=0)
        elif llm_model == "Llama2-7B(Q4)":
            client = AutoModelForCausalLM.from_pretrained("TheBloke/Llama-2-7B-Chat-GGUF", model_file=" llama-2-7b-chat.Q4_K_M.gguf", model_type="llama", gpu_layers=0)
        else:
            client = None

        if model_type == "small":
            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        elif model_type == "multilingual":
            model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        else:
            # Default to small model if model_type is not recognized
            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        
        return ([client, model])

def write_log(message, log_file="notemap_logs.txt"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}\n"
    with open(log_file, "a") as f:
        f.write(log_message)
