import requests
import json

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="llama3"):
        self.base_url = base_url
        self.model = model

    def generate_explanation(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("response", "Sem resposta gerada pelo modelo.")
        except Exception as e:
            pass
        
        # Fallback resiliente se o Ollama não estiver ativo
        return f"[Modo Fallback Resiliente] Ollama indisponível. Análise básica do evento detetada para o prompt: {prompt[:50]}..."

if __name__ == "__main__":
    client = OllamaClient()
    res = client.generate_explanation("Explicar anomalia de segurança no log.")
    print(res)
