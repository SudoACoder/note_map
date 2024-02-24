from os.path import basename
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from utils import *
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('QtAgg')

class AI(object):
    def __init__(self, OPENAI_API_KEY, model_type, llm_model):
        # Initialize OpenAI client and model
        self.client, self.model = initialize_openai_and_embedding(OPENAI_API_KEY, model_type, llm_model)
        self.llm_model = llm_model
    
    def content_embedding(self, content):
        return self.model.encode(content).tolist()

    def clustering(self, allowed_type, txt_files, pdf_files, docx_files, num_clusters):
        # Clustering logic
        contents = []
        C_path = []
        if allowed_type == "txt" or allowed_type == "all":
            for file in txt_files:
                with open(file, 'r', encoding='utf-8') as f:
                    contents.append(f.read())
                    C_path.append(basename(file))

        if allowed_type == "pdf" or allowed_type == "all":
            for file in pdf_files:
                try:
                    pdf_text = read_pdf(file)
                    contents.append(pdf_text)
                    C_path.append(basename(file))
                except Exception as e:
                    write_log(f"Warning: Error reading PDF file: {e}")

        if allowed_type == "docx" or allowed_type == "all":
            for file in docx_files:
                try:
                    docx_text = read_docx(file)
                    contents.append(docx_text)
                    C_path.append(basename(file))
                except Exception as e:
                    write_log(f"Warning: Error reading DOCX file: {e}")
        
        if len(contents) < num_clusters:
            return "Error"
        X = [self.content_embedding(content) for content in contents]
        svd = TruncatedSVD(n_components=2)
        X_svd = svd.fit_transform(X)

        kmeans = KMeans(n_clusters=num_clusters)
        kmeans.fit(X)
        y_kmeans = kmeans.predict(X)

        plt.figure(figsize=(8, 6))
        
        for i in range(num_clusters):
            plt.scatter(X_svd[y_kmeans == i, 0], X_svd[y_kmeans == i, 1], label=f'Cluster {i+1}')

        for i in range(len(contents)):
            plt.annotate(C_path[i], (X_svd[i, 0], X_svd[i, 1]))
        
        plt.title('Clustering of Text Files Content')
        plt.xlabel('Feature 1')
        plt.ylabel('Feature 2')
        plt.legend()
        plt.show()


    def keyword_search(self, allowed_type, txt_files, pdf_files, docx_files, keyword):
        # Keyword search logic
        results = []
        if allowed_type == "txt" or allowed_type == "all":
            for file in txt_files:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if keyword.lower() in content.lower():
                        results.append(file)

        if allowed_type == "pdf" or allowed_type == "all":
            for file in pdf_files:
                try:
                    pdf_text = read_pdf(file)
                    if keyword.lower() in pdf_text.lower():
                        results.append(file)
                except Exception as e:
                    write_log(f"Warning: Error reading PDF file: {e}")

        if allowed_type == "docx" or allowed_type == "all":
            for file in docx_files:
                try:
                    docx_text = read_docx(file)
                    if keyword.lower() in docx_text.lower():
                        results.append(file)
                except Exception as e:
                    write_log(f"Warning: Error reading DOCX file: {e}")

        return results
    
    def chat_interaction(self, msg, selected_note_files, chat_history):
        # Chat interaction logic
        notes_text = ""
        for file in selected_note_files:
            with open(file, 'r', encoding='utf-8') as f:
                notes_text += f.read() + "\n"
        if self.llm_model in ["Tinyllama(Q5)", "Llama2-7B(Q4)"]:
            history_str = '\n'.join([f"{c['role']}: {c['content']}" for c in chat_history])
            prompt = f"""Answer the user question based on the following notes.(answer max one sentence(15-20 words)\n\nNotes: \n{notes_text}\n\n{history_str}\nuser: {msg}\nassistant: """
            chatbot_response = self.client(prompt, temperature=0.7, max_new_tokens=41, stop=['assistant:','user:'], threads=4)
        else: 
            response = self.client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "Answer the user question based on the notes.(answer max one sentence(15-20 words)"},
                                {"role": "user", "content": f"Notes: \n{notes_text}"}] + chat_history + [{"role": "user", "content": msg}], max_tokens=41)

            chatbot_response = response.choices[0].message.content
        return chatbot_response.strip()
