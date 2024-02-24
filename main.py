import glob
import sys
import json
from os.path import basename
from PyQt6 import QtWidgets
from utils import *
import warnings
from ai_logic import *

warnings.filterwarnings('ignore', category=UserWarning, message='TypedStorage is deprecated')

class TextClusteringGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Clustering Tool")

        # Variables
        self.txt_files = []
        self.pdf_files = []
        self.docx_files = []
        self.model = None
        self.num_clusters = 3
        self.keyword = ""
        self.chat_history = []

        # Load settings from file
        self.OPENAI_API_KEY, self.model_type = load_settings()
        self.Ai = AI(self.OPENAI_API_KEY, self.model_type)

        # GUI Components
        self.create_widgets()

    def save_settings(self, API_KEY, Type):
        settings = {
            "OPENAI_API_KEY": API_KEY.text(),
            "model_type": Type.currentText()
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        self.OPENAI_API_KEY = API_KEY.text()
        self.model_type = Type.currentText()
        self.client, self.model = initialize_openai_and_embedding(self.OPENAI_API_KEY, self.model_type)

    def open_settings(self):
        settings_window = QtWidgets.QDialog(self)
        settings_window.setWindowTitle("Settings")
        layout = QtWidgets.QFormLayout()
        api_key_entry = QtWidgets.QLineEdit(self.OPENAI_API_KEY)
        model_type_combobox = QtWidgets.QComboBox()
        model_type_combobox.addItems(["small", "multilingual"])
        model_type_combobox.setCurrentText(self.model_type)
        layout.addRow("OpenAI API Key (Optional):", api_key_entry)
        layout.addRow("Model Type:", model_type_combobox)
        save_button = QtWidgets.QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_settings(api_key_entry, model_type_combobox))
        layout.addRow(save_button)
        settings_window.setLayout(layout)
        settings_window.exec()

    def create_widgets(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QGridLayout(central_widget)

        # Add settings button
        settings_button = QtWidgets.QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings)
        layout.addWidget(settings_button, 6, 2, 1, 1)

        # Add directory selection widgets
        label1 = QtWidgets.QLabel("Select Directory:")
        layout.addWidget(label1, 0, 0)
        self.directory_entry = QtWidgets.QLineEdit()
        self.directory_entry.setReadOnly(True)
        layout.addWidget(self.directory_entry, 0, 1)
        browse_button = QtWidgets.QPushButton("Browse")
        browse_button.clicked.connect(self.select_directory)
        layout.addWidget(browse_button, 0, 2)

        # Add cluster count input
        label2 = QtWidgets.QLabel("Number of Clusters:")
        layout.addWidget(label2, 1, 0)
        self.num_clusters_entry = QtWidgets.QLineEdit(str(self.num_clusters))
        self.num_clusters_entry.textChanged.connect(self.update_cluster_value)
        layout.addWidget(self.num_clusters_entry, 1, 1)

        # Add file type selection combobox
        label3 = QtWidgets.QLabel("File Type:")
        layout.addWidget(label3, 2, 0)
        self.file_type_combobox = QtWidgets.QComboBox()
        self.file_type_combobox.addItems(["txt", "pdf", "docx", "all"])
        self.file_type_combobox.setCurrentText('all')
        layout.addWidget(self.file_type_combobox, 2, 1)

        # Add keyword search input
        keyword_label = QtWidgets.QLabel("Keyword:")
        layout.addWidget(keyword_label, 3, 0)
        self.keyword_entry = QtWidgets.QLineEdit(self.keyword)
        layout.addWidget(self.keyword_entry, 3, 1)

        # Add search button
        search_button = QtWidgets.QPushButton("Search")
        search_button.clicked.connect(self.search_keyword)
        layout.addWidget(search_button, 3, 2)

        # Add "Cluster Text Files" button
        cluster_button = QtWidgets.QPushButton("Cluster Text Files")
        cluster_button.clicked.connect(self.cluster_files)
        layout.addWidget(cluster_button, 4, 0, 1, 3)

        # Add "Chat" button
        chat_button = QtWidgets.QPushButton("Chat")
        chat_button.clicked.connect(self.open_chat_window)
        layout.addWidget(chat_button, 6, 0, 1, 1)

        # Add result text widget
        self.result_text = QtWidgets.QTextEdit()
        layout.addWidget(self.result_text, 5, 0, 1, 3)
    
    def update_cluster_value(self):
        # Update the num_clusters variable when the text in the QLineEdit changes
        num_clusters_text = self.num_clusters_entry.text()
        try:
            self.num_clusters = int(num_clusters_text)
        except ValueError:
            # Handle the case when the input is not a valid integer
            QtWidgets.QMessageBox.warning(self, "Warning", "only int!")

    def open_chat_window(self):
        if not self.txt_files and not self.pdf_files and not self.docx_files:
            QtWidgets.QMessageBox.warning(self, "Warning", "No note files loaded. Please select a directory containing note files.")
            return

        chat_window = QtWidgets.QDialog(self)
        chat_window.setWindowTitle("Chat with Your Notes")
        layout = QtWidgets.QVBoxLayout(chat_window)

        self.selected_files = []
        for file in self.txt_files + self.pdf_files + self.docx_files:
            cb = QtWidgets.QCheckBox(basename(file))
            layout.addWidget(cb)
            self.selected_files.append((file, cb))

        chat_history = QtWidgets.QTextEdit()
        layout.addWidget(chat_history)

        chat_input = QtWidgets.QLineEdit()
        layout.addWidget(chat_input)

        send_button = QtWidgets.QPushButton("Send")
        send_button.clicked.connect(lambda: self.send_message(chat_input, chat_history))
        layout.addWidget(send_button)

        chat_window.setLayout(layout)
        chat_window.exec()

    def send_message(self, chat_input, chat_history):
        selected_files = [file for file, cb in self.selected_files if cb.isChecked()]
        if not selected_files:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select at least one note file.")
            return
        
        user_input = chat_input.text().strip()
        if user_input:
            try:
                chatbot_response = self.Ai.chat_interaction(self.client, user_input, selected_files, self.chat_history)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to generate response: {e}")
                chatbot_response = "Sorry, I couldn't understand that."

            self.add_message_to_chat(chat_history, user_input, is_user=True)
            self.add_message_to_chat(chat_history, chatbot_response, is_user=False)

            chat_input.clear()

    def add_message_to_chat(self, chat_history, message, is_user=True):
        prefix = "You: " if is_user else "Chatbot: "
        chat_history.append(f"{prefix}{message}\n")

        self.chat_history.append({"role": "user" if is_user else "assistant", "content": message})

    def select_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self)
        if directory:
            self.directory_entry.setText(directory)
            self.txt_files = glob.glob(directory + "/*.txt")
            self.pdf_files = glob.glob(directory + "/*.pdf")
            self.docx_files = glob.glob(directory + "/*.docx")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a directory!")

    def cluster_files(self):
        if not self.txt_files and not self.pdf_files and not self.docx_files:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a directory containing txt, pdf or docx files!")
            return
        
        
        S = self.Ai.clustering(self.file_type_combobox.currentText(), self.txt_files, self.pdf_files, self.docx_files, self.num_clusters)
        if S == 'Error':
            QtWidgets.QMessageBox.warning(self, "Warning", "The number of files in this path with this format is less than the number of clusters!")
            
    def search_keyword(self):
        if not self.txt_files and not self.pdf_files:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a directory containing text files or PDF files.")
            return

        keyword = self.keyword_entry.text()
        if not keyword:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a keyword to search.")
            return

        results = self.Ai.keyword_search(self.file_type_combobox.currentText(), self.txt_files, self.pdf_files, self.docx_files, keyword)

        if results:
            self.result_text.clear()
            self.result_text.append("Files containing the keyword:\n")
            for file in results:
                self.result_text.append(file)
        else:
            self.result_text.clear()
            self.result_text.append("No files found containing the keyword.")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = TextClusteringGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
