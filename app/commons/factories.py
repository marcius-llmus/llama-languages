from llama_index.llms.google_genai import GoogleGenAI
from app.settings.services import SettingsService


class LLMFactory:
    """
    A factory for creating LLM clients with dynamic configurations from settings.
    """

    def __init__(self, settings_service: SettingsService):
        self.settings_service = settings_service

    def create(self, model: str, temperature: float) -> GoogleGenAI:
        """Creates a GoogleGenAI instance with the specified model and temperature."""
        app_settings = self.settings_service.get_settings()
        if not app_settings.gemini_api_key:
            raise ValueError("Gemini API key is not configured in settings.")

        return GoogleGenAI(
            model=model, api_key=app_settings.gemini_api_key, temperature=temperature
        )
