import glob
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from os.path import basename
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from pypdf import PdfReader
import docx
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = ""
client = OpenAI(api_key=OPENAI_API_KEY)

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

# Class for Text Clustering GUI
class TextClusteringGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Text Clustering Tool")
        
        # Variables
        self.txt_files = []
        self.pdf_files = []
        self.docx_files = []
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        #SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") #Heavy but great for working with non-English texts.
        self.num_clusters = tk.IntVar(value=3)
        self.keyword = tk.StringVar()
        self.file_type = tk.StringVar(value="all")
        
        # GUI Components
        self.create_widgets()

    def create_widgets(self):
        label1 = tk.Label(self.master, text="Select Directory:")
        label1.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        
        self.directory_entry = tk.Entry(self.master, width=50, state='readonly')
        self.directory_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
        browse_button = tk.Button(self.master, text="Browse", command=self.select_directory)
        browse_button.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        label2 = tk.Label(self.master, text="Number of Clusters:")
        label2.grid(row=1, column=0, padx=10, pady=5, sticky='w')

        label3 = tk.Label(self.master, text="File Type:")
        label3.grid(row=3, column=0, padx=10, pady=5, sticky='w')

        self.file_type_combobox = ttk.Combobox(self.master, textvariable=self.file_type, values=["txt", "pdf", "docx","all"])
        self.file_type_combobox.grid(row=3, column=1, padx=10, pady=5, sticky='w')
        
        cluster_entry = tk.Entry(self.master, textvariable=self.num_clusters, width=5)
        cluster_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        keyword_label = tk.Label(self.master, text="Keyword:")
        keyword_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')
        
        self.keyword_entry = tk.Entry(self.master, textvariable=self.keyword, width=20)
        self.keyword_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        search_button = tk.Button(self.master, text="Search", command=self.search_keyword)
        search_button.grid(row=2, column=2, padx=5, pady=5, sticky='w')
        
        cluster_button = tk.Button(self.master, text="Cluster Text Files", command=self.cluster_files)
        cluster_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        chat_button = tk.Button(self.master, text="Chat", command=self.open_chat_window)
        chat_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        self.result_text = scrolledtext.ScrolledText(self.master, height=20, width=80)
        self.result_text.grid(row=4, column=0, columnspan=3, padx=10, pady=5)
        
    def open_chat_window(self):
        if not self.txt_files and not self.pdf_files and not self.docx_files:
            messagebox.showwarning("Warning", "No note files loaded. Please select a directory containing note files.")
            return
        
        chat_window = tk.Toplevel(self.master)
        chat_window.title("Chat with Your Notes")
        
        # Create checkbuttons for each loaded file
        self.selected_files = []
        for file in self.txt_files + self.pdf_files + self.docx_files:
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(chat_window, text=basename(file), variable=var)
            cb.pack(anchor="w")
            self.selected_files.append((file, var))
        
        chat_history = scrolledtext.ScrolledText(chat_window, height=10, width=50)
        chat_history.pack(anchor="w", padx=10, pady=5)
        
        chat_input = tk.Entry(chat_window, width=50)
        chat_input.pack(anchor="w", padx=10, pady=5)
        
        send_button = tk.Button(chat_window, text="Send", command=lambda: self.send_message(chat_input, chat_history))
        send_button.pack(anchor="w", padx=5, pady=5)
    
    def send_message(self, chat_input, chat_history):
        selected_files = [file for file, var in self.selected_files if var.get()]
        if not selected_files:
            messagebox.showwarning("Warning", "Please select at least one note file.")
            return

        # Extract text from selected note files
        notes_text = ""
        for file in selected_files:
            with open(file, 'r', encoding='utf-8') as f:
                notes_text += f.read() + "\n"
        
        # Construct prompt with user input and notes text
        user_input = chat_input.get().strip()
        if user_input:    
            # Generate response from OpenAI
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                    {"role": "system", "content": "Answer the users question based on the notes.(answer only one sentence(15-20 words))"},
                    {"role": "user", "content": f"Question: {user_input}\n\n Notes:\n {notes_text}"}], max_tokens=41)

                chatbot_response = response.choices[0].message.content.strip()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate response: {e}")
                chatbot_response = "Sorry, I couldn't understand that."
            
            # Add user's message and chatbot's response to chat history
            self.add_message_to_chat(chat_history, user_input, is_user=True)
            self.add_message_to_chat(chat_history, chatbot_response, is_user=False)
            
            # Clear input field
            chat_input.delete(0, tk.END)
            
    def add_message_to_chat(self, chat_history, message, is_user=True):
        prefix = "You: " if is_user else "Chatbot: "
        chat_history.insert(tk.END, f"{prefix}{message}\n")
        chat_history.see(tk.END)  # Scroll to the end of the chat history


    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_entry.config(state='normal')
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, directory)
            self.directory_entry.config(state='readonly')
            self.txt_files = glob.glob(directory + "/*.txt")
            self.pdf_files = glob.glob(directory + "/*.pdf")
            self.docx_files = glob.glob(directory + "/*.docx")
    
    def cluster_files(self):
        if not self.txt_files and not self.pdf_files:
            messagebox.showwarning("Warning", "Please select a directory containing txt, pdf or docx files!")
            return

        contents = []
        if self.file_type.get() == "txt" or self.file_type.get() == "all":
            for file in self.txt_files:
                with open(file, 'r', encoding='utf-8') as f:
                    contents.append(f.read())
        
        if self.file_type.get() == "pdf" or self.file_type.get() == "all":
            for file in self.pdf_files:
                try:
                    pdf_text = read_pdf(file)
                    contents.append(pdf_text)
                except Exception as e:
                    messagebox.showwarning("Warning", f"Error reading PDF file: {e}")

        if self.file_type.get() == "docx" or self.file_type.get() == "all":
            for file in self.docx_files:
                try:
                    docx_text = read_docx(file)
                    contents.append(docx_text)
                except Exception as e:
                    messagebox.showwarning("Warning", f"Error reading DOCX file: {e}")

        if not contents:
            messagebox.showwarning("Warning", "No files found for the selected file type.")
            return


        X = [self.content_embedding(content) for content in contents]
        svd = TruncatedSVD(n_components=2)
        X_svd = svd.fit_transform(X)
        
        kmeans = KMeans(n_clusters=self.num_clusters.get())
        kmeans.fit(X)
        y_kmeans = kmeans.predict(X)
        
        plt.figure(figsize=(8, 6))
        for i in range(self.num_clusters.get()):
            plt.scatter(X_svd[y_kmeans == i, 0], X_svd[y_kmeans == i, 1], label=f'Cluster {i+1}')

        for i, txt_file in enumerate(self.txt_files + self.pdf_files):
            plt.annotate(basename(txt_file), (X_svd[i, 0], X_svd[i, 1]))
                    
        plt.title('Clustering of Text Files Content')
        plt.xlabel('Feature 1')
        plt.ylabel('Feature 2')
        plt.legend()
        plt.show()
        
    def content_embedding(self, content):
        return self.model.encode(content).tolist()
    
    def search_keyword(self):
        if not self.txt_files and not self.pdf_files:
            messagebox.showwarning("Warning", "Please select a directory containing text files or PDF files.")
            return
        
        keyword = self.keyword.get()
        if not keyword:
            messagebox.showwarning("Warning", "Please enter a keyword to search.")
            return
        
        results = []
        if self.file_type.get() == "txt" or self.file_type.get() == "all":
            for file in self.txt_files:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if keyword.lower() in content.lower():
                        results.append(file)
                        
        if self.file_type.get() == "pdf" or self.file_type.get() == "all":
            for file in self.pdf_files:
                try:
                    pdf_text = read_pdf(file)
                    if keyword.lower() in pdf_text.lower():
                        results.append(file)
                except Exception as e:
                    messagebox.showwarning("Warning", f"Error reading PDF file: {e}")

        if self.file_type.get() == "docx" or self.file_type.get() == "all":
            for file in self.docx_files:
                try:
                    docx_text = read_docx(file)
                    if keyword.lower() in docx_text.lower():
                        results.append(file)
                except Exception as e:
                    messagebox.showwarning("Warning", f"Error reading DOCX file: {e}")

        if results:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Files containing the keyword:\n")
            for file in results:
                self.result_text.insert(tk.END, file + "\n")
        else:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "No files found containing the keyword.")
        

def main():
    root = tk.Tk()
    app = TextClusteringGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
