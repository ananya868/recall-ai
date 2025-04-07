import os, json, sys 
import base64


class ProcessTextInput:
    def __init__(self, text: str): 
        assert self.text, "Text input cannot be empty."
        self.text = text
    
    def _process(self, min_length: int = 30, max_length: int = 2000) -> str:
        # Check if the text is too short
        if len(self.text.split()) < min_length:
            raise ValueError("Text input is too short. Please provide a longer text.")
        # Check if the text is too long
        if len(self.text.split()) > max_length:
            raise ValueError("Text input is too long. Please provide a shorter text.")
        return self.text


class ProcessImageInput:
    def __init__(self, image_path: str): 
        assert os.path.exists(image_path), "Image path does not exist."
        assert image_path.endswith(('.png', '.jpeg')), "Image path must be a .png, or .jpeg file."
        self.image_path = image_path

        # Set Extension 
        if self.image_path.endswith('.png'):
            self.extension = 'png'
        elif self.image_path.endswith('.jpeg'):
            self.extension = 'jpeg'

        # Model 
        from openai import OpenAI 
        self.client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _process(self, model: str = "gpt-4o-mini"): 
        base64_image = self.encode_image(self.image_path)
        response = self.client.responses.create(
            model = model, 
            input = [
                {
                    "role": "user", 
                    "content": [
                        {"type": "input_text", "text": "This is an image of notes taken by student. Your task it to write down the text in the image. Only output the text, do not include any other information, explanation, or comments."},
                        {
                            "type": "input_image", 
                            "image_url": f"data:image/{self.extension};base64,{base64_image}",
                        },
                    ], 
                }
            ]
        )
        text = response.output_text
        # Check if the text is too short 
        if len(text.split()) < 10:
            raise ValueError("Text input is too short. Please provide a longer text.")
        return text


class ProcessAudioInput: 
    def __init__(self, audio_path: str):
        assert os.path.exists(audio_path), "Audio path does not exist."
        assert audio_path.endswith(('.mp3', '.wav')), "Audio path must be a .mp3, or .wav file."
        self.audio_path = audio_path

        # Model
        import whisper 
        self.client = whisper.load_model("base")
        
    def _process(self):
        transcript = self.client.transcribe(self.audio_path)
        text = transcript["text"]
        
        # Check if the text is too short
        if len(text.split()) < 10:
            raise ValueError("Text input is too short. Please provide a longer text.")
        # Check if its english 
        if transcript["language"] != "en":
            raise ValueError("Audio input is not in English. Please provide an English audio file.")
        return text


class ProcessPDF: 
    def __init__(self, pdf_path: str): 
        assert os.path.exists(pdf_path), "PDF path does not exist."
        assert pdf_path.endswith('.pdf'), "PDF path must be a .pdf file."
        self.pdf_path = pdf_path

        # PDF Processor and LLM 
        import pymupdf 
        from openai import OpenAI
        self.client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    
    def _process(self):
        pdf = pymupdf.open(self.pdf_path)
        page_content = []
        for page in pdf:
            page_content.append(page.get_text().encode('utf-8'))
        
        # Convert to python string
        page_content = [page.decode('utf-8') for page in page_content]
        # Check if the text is too short
        if len(page_content) == 1:
            if len(page_content[0].split()) < 10:
                raise ValueError("Text input is too short. Please provide a longer text.")
        # Check if the text is too long
        if len(page_content) > 1:
            combined_text = b''.join(page_content).decode('utf-8')
            if len(combined_text.split()) > 4000:
                # Strip the text to 4000 words 
                combined_text = ' '.join(combined_text.split()[:4000])
        return combined_text


class ProcessLink: 
    pass 


class ProcessTopic:
    pass 


class ProcessUserBackground: 
    pass




class FlashCardGenerator:
    pass