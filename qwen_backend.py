"""
qwen_backend.py - Camada de Backend para integração com o Ollama e modelos Qwen.

Este módulo encapsula:
- Comunicação com a API REST do Ollama (localhost:11434).
- Mapeamento de termos amigáveis para parâmetros técnicos de LLM (temperature, top_p, top_k, num_predict).
- Streaming de respostas token a token para consumo em tempo real.
- Criação e exclusão de modelos Qwen personalizados.
"""

import json
from typing import Any, Dict, Generator, List, Optional, Tuple
import requests

OLLAMA_BASE_URL = "http://localhost:11434"

# Mapeamento dos modelos Qwen conhecidos para explicações de Velocidade vs Inteligência
STANDARD_QWEN_MODELS = {
    "qwen2.5:0.5b": {
        "label": "550M (0.5B) - 🚀 Ultrarrápido",
        "params": "550 Milhões de parâmetros",
        "description": "Respostas quase instantâneas. Ideal para tarefas diretas, resumos simples e máquinas mais modestas.",
        "size_tier": "Ultraleve",
        "speed": "⭐⭐⭐⭐⭐ (Instantâneo)",
        "intelligence": "⭐⭐ (Básico)",
    },
    "qwen2.5:1.5b": {
        "label": "1.5B - ⚡ Rápido",
        "params": "1.5 Bilhões de parâmetros",
        "description": "Excelente velocidade com boa capacidade de escrita e entendimento de comandos diretos.",
        "size_tier": "Leve",
        "speed": "⭐⭐⭐⭐ (Muito Rápido)",
        "intelligence": "⭐⭐⭐ (Bom)",
    },
    "qwen2.5:3b": {
        "label": "3B - ⚖️ Equilíbrio Ideal",
        "params": "3 Bilhões de parâmetros",
        "description": "Melhor custo-benefício entre raciocínio lógico, qualidade de texto e fluidez de geração.",
        "size_tier": "Médio",
        "speed": "⭐⭐⭐ (Moderado)",
        "intelligence": "⭐⭐⭐⭐ (Muito Bom)",
    },
    "qwen2.5:7b": {
        "label": "7B - 🧠 Máxima Inteligência",
        "params": "7 Bilhões de parâmetros",
        "description": "Maior capacidade analítica, raciocínio aprofundado e respostas complexas. Exige mais do processador.",
        "size_tier": "Completo",
        "speed": "⭐⭐ (Exige mais tempo)",
        "intelligence": "⭐⭐⭐⭐⭐ (Excelente)",
    },
}

# Presets de uso com termos do dia a dia
PRESETS = {
    "💡 Equilíbrio Geral": {
        "description": "Ideal para conversas do dia a dia, explicações e dúvidas gerais.",
        "criatividade": 0.7,
        "vocabulario": 0.9,
        "foco": 40,
        "tamanho_maximo": 1024,
        "antirrepeticao": 1.1,
    },
    "🎯 Foco & Precisão": {
        "description": "Ideal para lógica, código, respostas objetivas e análises factuais.",
        "criatividade": 0.2,
        "vocabulario": 0.7,
        "foco": 20,
        "tamanho_maximo": 1024,
        "antirrepeticao": 1.15,
    },
    "🎨 Criatividade & Escrita": {
        "description": "Ideal para criar histórias, poesias, ideias de marketing e brainstorming.",
        "criatividade": 1.1,
        "vocabulario": 0.95,
        "foco": 60,
        "tamanho_maximo": 2048,
        "antirrepeticao": 1.05,
    },
    "⚙️ Ajuste Manual": {
        "description": "Permite que você defina individualmente cada um dos parâmetros.",
        "criatividade": 0.7,
        "vocabulario": 0.9,
        "foco": 40,
        "tamanho_maximo": 1024,
        "antirrepeticao": 1.1,
    },
}

# Modelos pré-definidos de comportamento / personalidade
PERSONALIDADES_PADRAO = {
    "🤖 Assistente Geral (Neutro & Prestativo)": "Você é um assistente prestativo, claro, cordial e objetivo. Responda em português com boa formatação.",
    "👨‍🏫 Professor Paciente (Didático)": "Você é um professor paciente e acolhedor. Explique os conceitos passo a passo com exemplos práticos e analogias simples.",
    "💻 Especialista Técnico (Direto ao ponto)": "Você é um engenheiro de software sênior. Forneça respostas concisas, código limpo, direto ao ponto e sem enrolação.",
    "✍️ Escritor Criativo (Elegante & Expressivo)": "Você é um escritor e roteirista habilidoso. Use linguagem expressiva, rica em metáforas e criatividade.",
    "🎯 Revisor Crítico (Focado em Detalhes)": "Você é um revisor minucioso. Analise o que for enviado apontando melhorias, falhas de lógica e sugestões práticas de aprimoramento.",
    "✏️ Personalizado": "",
}


def check_ollama_status() -> bool:
    """Verifica se o serviço local do Ollama está em execução e respondendo."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def get_available_models() -> List[Dict[str, Any]]:
    """
    Retorna a lista de modelos instalados no Ollama, categorizados entre
    modelos Qwen padrão e modelos personalizados criados pelo usuário.
    """
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code != 200:
            return []

        data = resp.json()
        models = data.get("models", [])
        classified_models = []

        for m in models:
            raw_name = m.get("name", "")
            # Remove a tag :latest para comparação quando aplicável
            normalized_name = raw_name.replace(":latest", "") if raw_name.endswith(":latest") and ":" not in raw_name.replace(":latest", "") else raw_name

            # Verifica se é um dos modelos Qwen padrão
            is_standard = raw_name in STANDARD_QWEN_MODELS or normalized_name in STANDARD_QWEN_MODELS
            
            label = raw_name
            description = "Modelo instalado localmente no Ollama"
            info = {}

            if raw_name in STANDARD_QWEN_MODELS:
                info = STANDARD_QWEN_MODELS[raw_name]
                label = info["label"]
                description = info["description"]
            elif normalized_name in STANDARD_QWEN_MODELS:
                info = STANDARD_QWEN_MODELS[normalized_name]
                label = info["label"]
                description = info["description"]
            elif "qwen" in raw_name.lower():
                label = f"✨ {raw_name} (Customizado)"
                description = "Modelo Qwen personalizado pelo usuário."

            size_gb = round(m.get("size", 0) / (1024 ** 3), 2)

            classified_models.append({
                "name": raw_name,
                "label": label,
                "description": description,
                "size_gb": size_gb,
                "is_standard": is_standard,
                "is_qwen": "qwen" in raw_name.lower(),
                "info": info
            })

        return classified_models
    except Exception as e:
        print(f"Erro ao listar modelos: {e}")
        return []


def map_friendly_to_options(
    criatividade: float,
    vocabulario: float,
    foco: int,
    tamanho_maximo: int,
    antirrepeticao: float = 1.1,
    seed: Optional[int] = None,
    stop_sequences: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Converte parâmetros amigáveis da interface para as opções técnicas do Ollama:
    - criatividade -> temperature (0.0 a 1.5)
    - vocabulario -> top_p (0.1 a 1.0)
    - foco -> top_k (1 a 100)
    - tamanho_maximo -> num_predict (tokens máximos gerados)
    - antirrepeticao -> repeat_penalty (1.0 a 1.5 - sem custo de desempenho)
    - seed -> semente para reproduzibilidade idêntica de respostas
    - stop_sequences -> lista de palavras de parada
    """
    options: Dict[str, Any] = {
        "temperature": float(criatividade),
        "top_p": float(vocabulario),
        "top_k": int(foco),
        "num_predict": int(tamanho_maximo),
        "repeat_penalty": float(antirrepeticao),
    }
    if seed is not None:
        options["seed"] = int(seed)
    if stop_sequences:
        options["stop"] = stop_sequences

    return options


def stream_chat(
    model: str,
    messages: List[Dict[str, str]],
    options: Dict[str, Any],
    system_prompt: Optional[str] = None,
    json_mode: bool = False,
) -> Generator[str, None, None]:
    """
    Envia uma conversa para o Ollama via POST /api/chat com stream=True
    e faz yield do conteúdo de cada token conforme chega em tempo real.
    """
    url = f"{OLLAMA_BASE_URL}/api/chat"

    full_messages = []
    if system_prompt and system_prompt.strip():
        full_messages.append({"role": "system", "content": system_prompt.strip()})
    full_messages.extend(messages)

    payload: Dict[str, Any] = {
        "model": model,
        "messages": full_messages,
        "stream": True,
        "options": options,
    }
    if json_mode:
        payload["format"] = "json"

    try:
        with requests.post(url, json=payload, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    # Verifica se há mensagem no chunk
                    delta = chunk.get("message", {}).get("content", "")
                    if delta:
                        yield delta
                    # Se concluído
                    if chunk.get("done", False):
                        break
    except requests.exceptions.ConnectionError:
        yield "\n\n❌ **Erro de conexão**: O Ollama não parece estar em execução na porta 11434. Verifique se o serviço está ativo."
    except Exception as e:
        yield f"\n\n❌ **Erro na geração**: {str(e)}"


def create_custom_model(
    name: str,
    base_model: str,
    system_prompt: str,
    parameters: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, str]:
    """
    Cria um novo modelo personalizado no Ollama a partir de um modelo base
    utilizando a API /api/create.
    """
    if not name or not name.strip():
        return False, "O nome do modelo personalizado não pode ficar vazio."

    clean_name = name.strip().lower().replace(" ", "-")

    url = f"{OLLAMA_BASE_URL}/api/create"
    payload = {
        "name": clean_name,
        "from": base_model,
        "system": system_prompt.strip() if system_prompt else "",
        "parameters": parameters or {},
        "stream": False,
    }

    try:
        resp = requests.post(url, json=payload, timeout=180)
        if resp.status_code == 200:
            return True, f"Modelo '{clean_name}' criado com sucesso a partir de '{base_model}'!"
        else:
            try:
                err_data = resp.json()
                err_msg = err_data.get("error", resp.text)
            except Exception:
                err_msg = resp.text
            return False, f"Falha ao criar modelo: {err_msg}"
    except Exception as e:
        return False, f"Erro ao solicitar criação: {str(e)}"


def delete_custom_model(name: str) -> Tuple[bool, str]:
    """Exclui um modelo customizado do Ollama via DELETE /api/delete."""
    url = f"{OLLAMA_BASE_URL}/api/delete"
    payload = {"name": name}
    try:
        resp = requests.delete(url, json=payload, timeout=30)
        if resp.status_code == 200:
            return True, f"Modelo '{name}' excluído com sucesso."
        else:
            return False, f"Falha ao excluir: {resp.text}"
    except Exception as e:
        return False, f"Erro ao excluir: {str(e)}"
