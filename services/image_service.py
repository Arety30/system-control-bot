import ollama

class ImageAnalysisService:
    @staticmethod
    def analyze_image(image_path):
        # Using LLaVA/Llama 3.2 via local Ollama
        response = ollama.chat(model='llama3.2:1b', messages=[
            {
                'role': 'user',
                'content': 'Describe this image',
                'images': [image_path]
            }
        ])
        return response['message']['content']
