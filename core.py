import os, json, sys 
import base64
import asyncio 
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from dotenv import load_dotenv 
import pymupdf 

load_dotenv()


class ProcessTextInput:
    """
    Class to process text input and check for length constraints.
    """
    def __init__(self, text: str): 
        assert text, "Text input cannot be empty."
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

    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _process(self, model: str = "gpt-4o-mini"): 
        base64_image = self.encode_image(self.image_path)
         # Model 
        import fireworks.client as image_client
        image_client.api_key = os.getenv("FIREWORKS_API_KEY")

        response = image_client.ChatCompletion.create(
            model = "accounts/fireworks/models/phi-3-vision-128k-instruct",
            messages = [{
                "role": "user",
                "content": [{
                "type": "text",
                "text": "Analyze the text in the image and write it as it is. output only the text and nothing else.",
                }, {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                },
                }, ],
            }],
        )

        text = response.choices[0].message.content
        # Check if the text is too short 
        if len(text.split()) < 10:
            raise ValueError("Text input is too short. Please provide a longer text.")
        return text


class ProcessAudioInput: 
    """
    Class to process an audio file and extract text content using Whisper model.
    """
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
    """
    Class to process a PDF file and extract text content. 
    """
    def __init__(self, pdf_path: str): 
        assert os.path.exists(pdf_path), "PDF path does not exist."
        assert pdf_path.endswith('.pdf'), "PDF path must be a .pdf file."
        self.pdf_path = pdf_path
    
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
            combined_text = ''.join(page_content)
            if len(combined_text.split()) > 4000:
                # Strip the text to 4000 words 
                combined_text = ' '.join(combined_text.split()[:4000])
        return combined_text


class ProcessLink: 
    """
    Class to process a web link and extract content using a web crawler. 
    """
    def __init__(self, link: str): 
        assert link.startswith("http"), "Link must start with http."
        self.link = link

    async def _process(self):
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        browser_conf = BrowserConfig(headless=True)
        run_conf = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            exclude_external_links=True,  # Don't follow external links
            excluded_tags=["header", "footer", "nav", "form"],  # Exclude these HTML elements
            exclude_social_media_links=True, 
            stream=False
        )
        async with AsyncWebCrawler(config=browser_conf) as crawler:
            result = await crawler.arun_many(
                urls=[self.link],
                config=run_conf
            )
            content = []
            for i, res in enumerate(result):
                if res.success: 
                    content.append(res.markdown)
                else: 
                    print(f"Error: {res.error}")

                return content
    

class ProcessTopic:
    """
    Class to generate knowledge context based on a given topic. 
    """
    def __init__(self, topic: str):
        assert topic, "Topic cannot be empty."
        self.topic = topic

        # Model
        from fireworks.client import Fireworks 
        self.client = Fireworks(api_key = os.getenv("FIREWORKS_API_KEY"))

    def _process(self, model: str = "accounts/fireworks/models/deepseek-v3"):
        response = self.client.chat.completions.create( 
            model = model, 
            messages = [{
                "role": "user", 
                "content": f"Write a 100-200 words essay on the topic '{self.topic}'. Make sure to describe various aspects of the topic. Only output the text, do not include any other information, explanation, or comments."
            }]
        )
        text = response.choices[0].message.content
        # Check if the text is too short
        if len(text.split()) < 10:
            raise ValueError("Text input is too short. Please provide a longer text.")
        # Check if the text is too long
        if len(text.split()) > 2000:
            raise ValueError("Text input is too long. Please provide a shorter text.")
        return text


class UserBio(BaseModel): 
        name: str = Field(..., description="Name of the user")
        age: int = Field(..., description="Age of the user")
        degree_name: str = Field(..., description="Degree name of the user")
        degree_year: int = Field(..., description="Year of the degree")
        course_name: str = Field(..., description="Course name of the user")
        interested_subjects: List[str] = Field(..., description="List of subjects the user is interested in")
class ProcessUserBackground: 
    def __init__(self, user_bio: UserBio):
        self.user_bio = user_bio

        # Model
        from fireworks.client import Fireworks 
        self.client = Fireworks(api_key = os.getenv("FIREWORKS_API_KEY"))
        self.user_bio = self.user_bio.dict()
    
    def _process(self, model: str = "accounts/fireworks/models/deepseek-v3"):
        response = self.client.chat.completions.create(
            model = model,
            messages = [{
                "role": "user",
                "content": f"Based on the following user bio, generate some study content for this user. If there are multiple subjects, write the core principals of each for user's education level. Do not exceed 1000 words of total. \n\n BIO: {self.user_bio}. Only output the text, do not include any other information, explanation, or comments."
            }]
        )
        text = response.choices[0].message.content
        # Check if the text is too short
        if len(text.split()) < 10:
            raise ValueError("Text input is too short. Please provide a longer text.")
        # Check if the text is too long
        if len(text.split()) > 2000: 
            raise ValueError("Text input is too long. Please provide a shorter text.")
        return text


class FlashCardGenerator:    
    """
    Class to generate educational flash cards from content.
    """

    # Prompt 
    DEFAULT_PROMPT = """
        You are an expert educational flash card creator. Your task is to generate high-quality, educational flash cards based on the content provided. 
        The flash cards should be concise, clear, and cover the most important concepts from the content.

        INPUT CONTENT:
        {content}
        
        Number of Cards: Specified->{num_cards} (or 5 if not specified)
        
        INSTRUCTIONS: 
        1. Analyze the provided content thoroughly, identifying key concepts, facts, definitions, formulas, and relationships.
        2. Create {num_cards} flash cards that:
            - Cover the most important information in the content
            - Progress from fundamental to more advanced concepts
            - Are clear, concise, and self-contained
            - Include a mix of factual recall, conceptual understanding, and application questions
            - Are tailored to the specified user demographics when provided
        3. For each flash card, include:
            - A clear, specific question on the front
            - A concise but complete answer on the back
            - A category/topic label
            - An importance rating (1-5, with 5 being most important)
        4. Ensure questions are formulated in a way that tests understanding, not just memorization.
        5. For mathematical or scientific content, include relevant formulas, equations, or processes.
        6. For historical or procedural content, focus on key events, sequences, or steps.
        7. For definition-based content, focus on precise terminology and meanings.
        8. For content with multiple themes, ensure balanced coverage across important topics.

        OUTPUT FORMAT:
        Return the flash cards as a JSON object strictly following this Pydantic model definition:
        title, subject, cards (list of card objects), total_cards, difficulty level 
    """

    def __init__(self, num_cards: int): 
        self.num_cards = num_cards

        # Model init 
        from fireworks.client import Fireworks 
        self.client = Fireworks(api_key = os.getenv("FIREWORKS_API_KEY"))

    def _generate(self, content: str, model: str = "accounts/fireworks/models/deepseek-v3"):
        # Output Schemas 
        class FlashCard(BaseModel):
            question: str = Field(..., description="Question of the flash card")    
            answer: str = Field(..., description="Answer of the flash card")
            category: Optional[str] = Field(..., description="Category of the flash card")
            importance: int = Field(..., description="Importance level from 1-5, with 5 being most important")

        class FlashCardSet(BaseModel):
            title: str = Field(description="Title for the set of flash cards")
            subject: str = Field(description="The general subject area")
            cards: List[FlashCard] = Field(description="List of flash cards")
            total_cards: int = Field(description="Total number of flash cards in the set")
            difficulty_level: str = Field(description="Overall difficulty level (Beginner, Intermediate, Advanced)")
        
        # Prompt 
        prompt = self.DEFAULT_PROMPT.format(content=content, num_cards=self.num_cards)

        # Run Model
        completion = self.client.chat.completions.create(
            model=model,
            response_format={"type": "json_object", "schema": FlashCardSet.model_json_schema()},
            messages=[
                {"role": "system", "content": "You are a flash cards generator for educational purposes."},
                {"role": "user", "content": prompt}
            ],
            
        )
        # Parse to dict 
        try:
            generated_text = completion.choices[0].message.content
            response = json.loads(generated_text)
        except Exception as e:
            raise ValueError(f"Failed to parse response: {e}")
        
        return response


class ContentProcessorFactory:
    """
    Factory class to create content processors based on input type.
    """
    @staticmethod
    def create_processor(input_type: str, **kwargs):
        if input_type == "text":
            return ProcessTextInput(text=kwargs.get("text", ""))
        
        elif input_type == "image":
            return ProcessImageInput(image_path=kwargs.get("image_path", ""))
        
        elif input_type == "audio":
            return ProcessAudioInput(audio_path=kwargs.get("audio_path", ""))
        
        elif input_type == "pdf":
            return ProcessPDF(pdf_path=kwargs.get("pdf_path", ""))
        
        elif input_type == "link":
            return ProcessLink(link=kwargs.get("link", ""))
        
        elif input_type == "topic":
            return ProcessTopic(topic=kwargs.get("topic", ""))
        
        elif input_type == "user_bio":
            user_bio = kwargs.get("user_bio")
            if not isinstance(user_bio, UserBio):
                raise ValueError("user_bio must be an instance of UserBio")
            return ProcessUserBackground(user_bio=user_bio)
        
        else:
            raise ValueError(f"Unknown input type: {input_type}")

    @staticmethod
    async def process_content(input_type: str, **kwargs):
        processor = ContentProcessorFactory.create_processor(input_type, **kwargs)
        
        # Special case for link which uses async
        if input_type == "link":
            content = await processor._process()
            # ProcessLink returns a list of markdowns, join them
            return "\n\n".join(content) if content else ""
        else:
            # All other processors use synchronous processing
            return processor._process()


class FlashCardService:
    """
    Service class to generate flash cards from various input types
    """
    def __init__(self, num_cards: int = 5):
        self.generator = FlashCardGenerator(num_cards=num_cards)
    
    async def generate_from_input(self, input_type: str, **kwargs):
        """
        Process content from the specified input and generate flash cards.
        
        Parameters:
        - input_type: Type of input ('text', 'image', 'audio', 'pdf', 'link', 'topic', 'user_bio')
        - **kwargs: Arguments specific to each processor type
        
        Returns:
        - Generated flash cards
        """
        content = await ContentProcessorFactory.process_content(input_type, **kwargs)
        if not content:
            raise ValueError(f"Failed to process {input_type} input or no content was extracted")
        
        return self.generator._generate(content=content)