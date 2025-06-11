# AI Flash Card Generator CLI ⚡

Generate custom educational flashcards from various sources using the power of AI! This interactive command-line tool allows you to create flashcards from text, images, audio files, PDFs, web links, specific topics, or even personalized based on a user's bio.

![Showcase](https://via.placeholder.com/800x400.png?text=Your+App+In+Action+Here)
*(☝️ Replace the placeholder above with a GIF or a key screenshot of your application in action!)*

## ✨ Features

*   **Multiple Input Sources:**
    *   📝 Direct Text Input
    *   🖼️ Image Files (OCR for text extraction)
    *   🎙️ Audio Files (Speech-to-Text transcription)
    *   📄 PDF Documents (Text extraction)
    *   🔗 Web Links (Content scraping)
    *   🧠 Specific Topics (AI-generated content)
    *   👤 User Bio (AI-generated personalized content)
*   **Interactive CLI:** User-friendly command-line interface built with `rich` for a polished experience.
*   **Customizable Output:** Specify the number of flashcards you want to generate.
*   **AI-Powered:** Leverages state-of-the-art models for:
    *   Image Analysis (Fireworks AI: Phi-3 Vision)
    *   Audio Transcription (OpenAI Whisper)
    *   Content Generation (Fireworks AI: Deepseek)
    *   Flashcard Creation (Fireworks AI: Deepseek with structured JSON output)
*   **Structured Flashcards:** Output includes question, answer, category, and importance rating.
*   **Visually Appealing Display:** Flashcards are presented clearly in the terminal using `rich` panels.
*   **Progress Indicators:** See what the app is doing with spinners and status messages.

## 🚀 Supported Input Types & Processing

| Emoji | Input Type | Description                                                                 | AI/Library Used                                  |
| :---- | :--------- | :-------------------------------------------------------------------------- | :----------------------------------------------- |
| 📝    | Text       | Directly paste or type your text.                                           | Fireworks AI (Flashcard Gen)                     |
| 🖼️    | Image      | Extracts text from `.png` or `.jpeg` images.                                | Fireworks AI (Phi-3 Vision for OCR)              |
| 🎙️    | Audio      | Transcribes spoken English from `.mp3` or `.wav` files.                     | OpenAI Whisper (Base model)                      |
| 📄    | PDF        | Extracts text content from `.pdf` files.                                    | PyMuPDF                                          |
| 🔗    | Web Link   | Fetches and parses content from a given URL.                                | Crawl4AI                                         |
| 🧠    | Topic      | Generates introductory content on a user-specified topic.                   | Fireworks AI (Deepseek)                          |
| 👤    | User Bio   | Generates personalized study content based on user demographics and interests. | Fireworks AI (Deepseek)                          |

## 🛠️ Technologies Used

*   **Python 3.8+**
*   **Core AI & Processing:**
    *   `fireworks-ai`: For LLM access (Phi-3 Vision, Deepseek for generation and flashcards).
    *   `openai-whisper`: For robust audio transcription.
    *   `pymupdf`: For PDF text extraction.
    *   `crawl4ai`: For asynchronous web content scraping.
*   **CLI & Utilities:**
    *   `rich`: For beautiful and interactive command-line interfaces.
    *   `pydantic`: For data validation and settings management (used for `UserBio` and flashcard schema).
    *   `python-dotenv`: For managing environment variables (API keys).
*   **Standard Libraries:** `os`, `json`, `sys`, `base64`, `asyncio`, `typing`.

## 📋 Prerequisites

1.  **Python 3.8 or higher.**
2.  **`pip` (Python package installer).**
3.  **FFmpeg:** Required by `openai-whisper` for audio processing.
    *   **macOS:** `brew install ffmpeg`
    *   **Ubuntu/Debian:** `sudo apt update && sudo apt install ffmpeg`
    *   **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your system's PATH.
4.  **Fireworks AI API Key:**
    *   Sign up at [Fireworks AI](https://fireworks.ai/).
    *   Obtain your API key from your account settings.

## ⚙️ Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ananya868/FlashCards-AI.git
    cd FlashCards-AI
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install dependencies:**
    Create a `requirements.txt` file with the following content:
    ```txt
    python-dotenv
    pymupdf
    fireworks-ai
    openai-whisper
    crawl4ai
    pydantic
    rich
    # Add any other specific versions if needed, e.g., torch for whisper if not auto-installed
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: `openai-whisper` might require `torch`. If you encounter issues, you might need to install it separately: `pip install torch torchvision torchaudio` (check Whisper documentation for specific versions if needed).*

4.  **Set up Environment Variables:**
    Create a file named `.env` in the root directory of the project and add your Fireworks AI API key:
    ```env
    FIREWORKS_API_KEY="your_fireworks_api_key_here"
    ```

## ▶️ How to Run

Once the setup is complete, run the application from the root directory of the project:

```bash
python app.py
```

**Follow the interactive prompts in your terminal:**
- You'll see a welcome header and a list of input options.
- Enter the number corresponding to your desired input type.
- Enter the number of flashcards you wish to generate.
- Provide the required input (e.g., file path, URL, text, topic details).
- The application will process the input and generate flashcards.
- Generated flashcards will be displayed one by one. Press Enter or confirm to see the next card.
- After viewing all cards, you'll be asked if you want to generate more.


## 💡 Future Enhancements / To-Do

    Export Flashcards: Option to save generated flashcards to JSON, CSV, or Anki deck format.

    More LLM Options: Allow selection of different models or providers.

    Advanced Error Handling: More specific error messages and recovery options.

    Input Validation: Stricter validation for file paths and URLs.

    Configuration File: For default settings (e.g., default number of cards).

    Testing: Add unit and integration tests.

    GUI Version: Potentially build a web or desktop GUI.

## 🤝 Contributing

Contributions are welcome! If you have ideas for improvements or find a bug, please feel free to:

    Fork the repository.

    Create a new branch (git checkout -b feature/YourFeature or bugfix/YourBug).

    Make your changes.

    Commit your changes (git commit -m 'Add some feature').

    Push to the branch (git push origin feature/YourFeature).

    Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE.md file for details (if you choose to add one).
(Consider adding an MIT License file to your repo).
