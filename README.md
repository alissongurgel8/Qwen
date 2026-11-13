# 🧠 Qwen Studio - Interface Visual e Controle de Parâmetros

Aplicação visual completa e intuitiva para interagir, controlar o comportamento e criar modelos personalizados da família **Qwen (Qwen 2.5)** executados localmente.

O projeto traduz conceitos técnicos de inteligência artificial (como *temperatura*, *top_p*, *top_k* e contagem de parâmetros) para **controles amigáveis** (Criatividade, Riqueza de vocabulário, Foco e Velocidade vs. Inteligência), permitindo que qualquer pessoa utilize o modelo de forma personalizada e com respostas geradas em **tempo real (streaming)**.

---

## 🏛️ Estrutura do Repositório

O projeto possui arquitetura desacoplada, separando a lógica de backend da interface gráfica:

```text
├── app.py              # Interface visual em Streamlit (Frontend)
├── qwen_backend.py     # Lógica de integração com Ollama, streaming e parâmetros (Backend)
├── iniciar.sh          # Script bash para checagem e inicialização rápida
├── requirements.txt    # Dependências Python necessárias
└── README.md           # Documentação completa e guia de instalação
```

- **[qwen_backend.py](file:///home/alisson/TACC/qwen_backend.py)**: Responsável por comunicar com a API do Ollama (`http://localhost:11434`), listar modelos instalados, traduzir parâmetros amigáveis para parâmetros técnicos de LLM, gerenciar o gerador de streaming (`stream_chat`) e executar a criação/exclusão de modelos no Ollama.
- **[app.py](file:///home/alisson/TACC/app.py)**: Interface em Streamlit com chat com suporte a streaming, seletor de modelos, presets de uso, sliders intuitivos, modo JSON, semente fixa e aba de criação de modelos personalizados.
- **[iniciar.sh](file:///home/alisson/TACC/iniciar.sh)**: Valida se o serviço do Ollama está no ar e inicia o servidor web na porta `8501`.

---

## 💻 Requisitos de Sistema

- **Sistema Operacional**: Linux (Ubuntu, Debian, Fedora, etc.), macOS ou Windows (via WSL2 ou nativo).
- **Python**: Versão 3.10 ou superior.
- **Memória RAM recomendada**:
  - Modelo **0.5B (550M)**: Mínimo 4 GB de RAM.
  - Modelo **1.5B**: Mínimo 6 GB de RAM.
  - Modelo **3B**: Mínimo 8 GB de RAM (Recomendado para uso geral).
  - Modelo **7B**: Mínimo 16 GB de RAM (ou GPU dedicada com pelo menos 6-8 GB VRAM).

---

## 🚀 Guia Passo a Passo: Recriando o Ambiente do Zero

Siga as etapas abaixo caso esteja configurando a aplicação em uma máquina nova sem nenhuma dependência instalada.

### 1. Clonar ou Baixar os Arquivos do Projeto

Se estiver usando Git:
```bash
git clone <URL_DO_REPOSITORIO>
cd TACC
```

---

### 2. Configurar o Ambiente Python

É recomendado utilizar um ambiente virtual (`venv`):

```bash
# 1. Criar o ambiente virtual
python3 -m venv venv

# 2. Ativar o ambiente virtual
# No Linux/macOS:
source venv/bin/activate
# No Windows:
# .\venv\Scripts\activate

# 3. Instalar as dependências do projeto
pip install -r requirements.txt
```

---

### 3. Instalar o Ollama (Gerenciador de Modelos Locais)

O **Ollama** é o motor que roda os modelos Qwen localmente na sua máquina.

#### No Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### No macOS ou Windows:
Baixe o instalador oficial diretamente no site:
👉 [https://ollama.com/download](https://ollama.com/download)

---

### 4. Baixar os Modelos Qwen

Você pode baixar os modelos de acordo com a capacidade da sua máquina. O Qwen 2.5 oferece diferentes tamanhos:

```bash
# Opção 1: Modelo Ultrarrápido / 550 Milhões de parâmetros (~397 MB de download)
ollama pull qwen2.5:0.5b

# Opção 2: Modelo Rápido / 1.5 Bilhões de parâmetros (~986 MB de download)
ollama pull qwen2.5:1.5b

# Opção 3: Equilíbrio Ideal / 3 Bilhões de parâmetros (~1.9 GB de download) [RECOMENDADO]
ollama pull qwen2.5:3b

# Opção 4: Máxima Inteligência / 7 Bilhões de parâmetros (~4.7 GB de download)
ollama pull qwen2.5:7b
```

> [!TIP]
> **Dica**: Se sua máquina tiver menos de 8 GB de memória RAM, dê preferência ao `qwen2.5:0.5b` ou `qwen2.5:1.5b`. Para computadores com 8 a 16 GB de RAM, o `qwen2.5:3b` oferece a melhor relação entre inteligência e velocidade.

---

### 5. Iniciar o Serviço do Ollama

O Ollama precisa estar em execução em segundo plano para atender às solicitações da aplicação:

```bash
# Iniciar o servidor local do Ollama (caso já não esteja rodando como serviço do sistema)
ollama serve
```

Para testar se está funcionando, você pode abrir outra aba do terminal e rodar:
```bash
curl http://localhost:11434/api/tags
```
Se retornar um JSON com a lista de modelos, o serviço está operante.

---

### 6. Iniciar a Aplicação Visual

Com o ambiente Python ativo e o Ollama rodando, execute:

```bash
./iniciar.sh
```

Ou diretamente via Streamlit:
```bash
streamlit run app.py
```

A aplicação será aberta automaticamente no seu navegador padrão em:
👉 **http://localhost:8501**

---

## 🎛️ Guia de Parâmetros: Conceito Técnico vs. Tradução Amigável

A interface foi projetada para que termos complexos de engenharia de IA sejam compreendidos por qualquer pessoa:

| Parâmetro na Aplicação | Parâmetro Técnico | O que faz na prática |
| :--- | :--- | :--- |
| **Inteligência vs. Velocidade** | Quantidade de Parâmetros (`0.5B`, `1.5B`, `3B`, `7B`) | Escolhe entre rapidez imediata ou profundidade de raciocínio lógico. |
| **Criatividade & Espontaneidade** | `temperature` (`0.0` a `1.5`) | `0.0` gera respostas extremamente exatas e factuais. Acima de `1.0` estimula ideias originais e variadas. |
| **Riqueza de Vocabulário** | `top_p` (`0.1` a `1.0`) | Define a variedade do vocabulário considerado. Valores menores focam nas palavras mais óbvias; valores maiores usam palavras mais ricas. |
| **Foco nas Respostas** | `top_k` (`1` a `100`) | Limita quantas palavras alternativas são avaliadas a cada instante. Valores baixos mantêm o modelo focado no objetivo principal. |
| **Tamanho Máximo** | `num_predict` (`256` a `4096` tokens) | Limita a extensão do texto para evitar respostas incompletas ou excessivamente prolixas. |
| **Filtro Antirrepetição** | `repeat_penalty` (`1.0` a `1.5`) | Evita que o modelo fique repetindo as mesmas frases ou ideias em loop. *(Zero impacto de desempenho)*. |
| **Modo JSON Estruturado** | `format: "json"` | Força o modelo a responder exclusivamente em formato JSON válido para integrações e automações. |
| **Semente Fixa** | `seed` | Garante que uma mesma pergunta com os mesmos parâmetros resulte **sempre na exata mesma resposta**. |
| **Palavra de Parada** | `stop` | Interrompe imediatamente a digitação se o modelo gerar uma palavra ou símbolo especificado (ex: `FIM`, `---`). |

---

## 🛠️ Como Criar Modelos Personalizados

Na aba **"🛠️ Criar Qwen Personalizado"** da aplicação, você pode criar uma versão sob medida:

1. **Nome**: Defina um identificador simples (ex: `qwen-advogado`, `qwen-professor`, `qwen-redator`).
2. **Modelo Base**: Selecione o nível de inteligência (`0.5b`, `1.5b`, `3b` ou `7b`).
3. **Personalidade (System Prompt)**: Digite as regras de conduta que o modelo deve sempre obedecer. Exemplo:
   ```text
   Você é um tutor de programação para iniciantes. Sempre explique os erros de código usando metáforas simples do dia a dia e termine encorajando o estudante.
   ```
4. **Criatividade e Antirrepetição Padrão**: Fixe os valores ideais para o seu modelo.
5. Clique em **"🚀 Criar Modelo Personalizado"**.

O modelo será compilado pelo Ollama em poucos segundos e ficará disponível para uso imediato no chat e no terminal (`ollama run nome-do-modelo`).

---

## ❓ Resolução de Problemas Comuns (Troubleshooting)

### 1. `⚠️ Ollama Offline` na barra lateral
- O serviço do Ollama não está rodando na porta 11434.
- **Solução**: Abra o terminal e execute `ollama serve`. No Linux com systemd, você também pode usar `systemctl start ollama`.

### 2. Respostas demorando muito para serem geradas
- Se sua máquina não possui GPU dedicada (placa de vídeo NVIDIA), o processamento ocorre via CPU.
- **Solução**: Na barra lateral, selecione modelos mais leves como **`550M (0.5B)`** ou **`1.5B`**. Eles foram projetados especialmente para velocidade em processadores comuns.

### 3. Erro `Port 8501 is already in use`
- A porta padrão do Streamlit já está sendo usada por outra instância.
- **Solução**: Inicie especificando outra porta:
  ```bash
  streamlit run app.py --server.port 8502
  ```

---

## 📄 Licença e Créditos

- Desenvolvido para modelos **Qwen 2.5** (Alibaba Cloud / Qwen Team).
- Gerenciador de inferência: **Ollama**.
- Interface de usuário: **Streamlit**.
