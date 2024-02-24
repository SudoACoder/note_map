# Note Map

Note Map is a simple yet powerful tool for quickly analyzing, organizing, and uncovering patterns and similarities within large volumes of textual files. With its intuitive interface and advanced features, Note Map empowers users to effortlessly visualize, search, and relate information across various file formats, including PDFs, TXTs, and DOCXs. Additionally, Note Map enables brainstorming, idea generation, and even communication with your notes!

## Features

- **Textual Analysis**: Quickly analyze and uncover patterns within large volumes of textual files.
- **Organize and Visualize**: Effortlessly organize and visualize information across various file formats.
- **Cross-File Format Support**: Supports analysis of PDFs, TXTs, DOCXs, and more (in future) for comprehensive insights.
- **Brainstorming**: Foster creativity by enabling brainstorming and idea generation.
- **Note Interaction**: Communicate and engage with your notes for enhanced productivity.(OpenAI api, TinyLlama and Llama2 7B)

## Usage

https://github.com/SudoACoder/note_map/assets/58640233/8b961b4d-0845-49d3-94a0-82e9e8c835b9

1. **Select Directory:**
   - Click on the "Browse" button to select a directory containing text files (TXT, PDF, DOCX).

2. **Number of Clusters:**
   - Specify the desired number of clusters for text file clustering.

3. **File Type:**
   - Choose the file type to include in the analysis (TXT, PDF, DOCX, or all).

4. **Keyword Search:**
   - Enter a keyword to search for within the selected text files.

5. **Cluster Text Files:**
   - Click on the "Cluster Text Files" button to initiate the clustering process.

6. **Chat Interface:**
   - To chat with your notes, please enter your openai api key in settings.
   - Click on the "Chat" button to open a chat window and interact with the notes using a chatbot interface.

## To-Do List
- ~~Support for local llms~~ <sub>24 Feb 2024 : +TinyLlama and Llama2 7B</sub>
- Conversation Log (+Long-Term Memory)
- Auto Summarizer
- Zero shot classification
- Named-entity recognition (NER)
- Using layers of encryption to store notes in the cache
- Light version
  
## Installation

1. Clone the repository:

   ```
   git clone https://github.com/SudoACoder/note_map.git
   ```

2. Navigate to the project directory:

   ```
   cd note_map
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Run the application:

   ```
   python main.py
   ```
   
## Notes

- You can run this tool completely locally to protect the privacy of your sensitive information and personal notes! Just select TinyLlama or Llama2 in the settings before starting a conversation! (downloads the model only for the first time)

## Contribution

Contributions are welcome! If you have any ideas, suggestions, or bug fixes, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
