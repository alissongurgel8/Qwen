"""
app.py - Interface visual (Frontend) em Streamlit para o Qwen.

Oferece:
- Chat interativo com streaming em tempo real (token a token).
- Controles de parâmetros traduzidos para linguagem amigável (sem jargões técnicos).
- Seletor de Velocidade vs. Inteligência baseado nos parâmetros (550M, 1.5B, 3B, 7B).
- Criação e gerenciamento de modelos Qwen personalizados sob demanda.
"""

import time
import streamlit as st
import qwen_backend

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Qwen Studio - Controle Visual & Personalização",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS personalizados para refinamento visual
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .badge-card {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 15px;
        border-left: 4px solid #4f46e5;
    }
    .stAlert {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Inicialização de Session States
if "messages" not in st.session_state:
    st.session_state.messages = []

if "preset_selected" not in st.session_state:
    st.session_state.preset_selected = "💡 Equilíbrio Geral"

if "system_prompt_custom" not in st.session_state:
    st.session_state.system_prompt_custom = qwen_backend.PERSONALIDADES_PADRAO["🤖 Assistente Geral (Neutro & Prestativo)"]

# Verifica conectividade com o Ollama
ollama_online = qwen_backend.check_ollama_status()
available_models = qwen_backend.get_available_models() if ollama_online else []

# -------------------------------------------------------------
# BARRA LATERAL: CONTROLES E CONFIGURAÇÕES AMIGÁVEIS
# -------------------------------------------------------------
with st.sidebar:
    st.title("🎛️ Painel de Controle")

    if not ollama_online:
        st.error("⚠️ **Ollama Offline**\nO serviço local do Ollama não foi detectado em `localhost:11434`.")
        st.info("Execute `ollama serve` no terminal para iniciar o serviço.")
    else:
        st.success("🟢 **Ollama Conectado**", icon="✅")

    st.markdown("---")

    # 1. ESCOLHA DE INTELIGÊNCIA vs. VELOCIDADE
    st.subheader("⚡ Inteligência vs. Velocidade")
    st.caption("Escolha o tamanho do modelo Qwen conforme sua necessidade de rapidez ou poder de raciocínio:")

    # Opções padrão organizadas por tamanho
    standard_names = list(qwen_backend.STANDARD_QWEN_MODELS.keys())
    standard_labels = [qwen_backend.STANDARD_QWEN_MODELS[k]["label"] for k in standard_names]

    # Modelos customizados existentes
    custom_models = [m for m in available_models if not m["is_standard"]]

    # Modo de seleção: Modelos Padrão ou Personalizados
    selection_mode = st.radio(
        "Origem do Modelo:",
        ["Modelos Qwen Oficiais", f"Modelos Personalizados ({len(custom_models)})"] if custom_models else ["Modelos Qwen Oficiais"],
        index=0,
        horizontal=True,
    )

    if selection_mode == "Modelos Qwen Oficiais":
        # Seletor baseado nos modelos padrão
        selected_index = 2  # Padrão: 3B (Equilíbrio)
        selected_label = st.selectbox(
            "Tamanho do Modelo:",
            options=standard_labels,
            index=selected_index,
            help="Modelos menores são ultra rápidos; modelos maiores raciocinam melhor.",
        )
        selected_model = standard_names[standard_labels.index(selected_label)]
        model_info = qwen_backend.STANDARD_QWEN_MODELS[selected_model]

        st.caption(f"ℹ️ **{model_info['params']}**")
        col_v, col_i = st.columns(2)
        with col_v:
            st.metric("Velocidade", model_info["speed"].split()[0])
        with col_i:
            st.metric("Inteligência", model_info["intelligence"].split()[0])
        st.info(model_info["description"])

    else:
        custom_names = [m["name"] for m in custom_models]
        custom_labels = [m["label"] for m in custom_models]
        selected_label = st.selectbox("Escolha seu modelo personalizado:", custom_labels, index=0)
        selected_model = custom_names[custom_labels.index(selected_label)]
        st.info(f"Modelo customizado selecionado: **{selected_model}**")

    st.markdown("---")

    # 2. PRESETS PRONTOS
    st.subheader("🎯 Estilo de Resposta (Presets)")
    selected_preset_name = st.selectbox(
        "Configuração rápida:",
        list(qwen_backend.PRESETS.keys()),
        index=list(qwen_backend.PRESETS.keys()).index(st.session_state.preset_selected),
        help="Escolha um estilo pronto para ajustar automaticamente os controles abaixo.",
    )
    preset_data = qwen_backend.PRESETS[selected_preset_name]
    st.caption(preset_data["description"])

    # 3. CONTROLES AMIGÁVEIS (SLIDERS)
    is_custom_mode = selected_preset_name == "⚙️ Ajuste Manual"

    with st.expander("🛠️ Ajustar Parâmetros em Detalhes", expanded=is_custom_mode):
        criatividade = st.slider(
            "🎨 Criatividade & Espontaneidade",
            min_value=0.0,
            max_value=1.5,
            value=float(preset_data["criatividade"]),
            step=0.05,
            disabled=not is_custom_mode,
            help="Técnico: 'temperature'. 0.0 produz respostas exatas e diretas. Valores altos (1.0+) tornam as respostas mais criativas e imprevisíveis.",
        )
        st.caption("⬅️ Mais Lógico / Factual | Mais Criativo / Imaginativo ➡️")

        vocabulario = st.slider(
            "📚 Variedade de Vocabulário",
            min_value=0.1,
            max_value=1.0,
            value=float(preset_data["vocabulario"]),
            step=0.05,
            disabled=not is_custom_mode,
            help="Técnico: 'top_p'. Controla a diversidade de palavras consideradas. Valores menores usam palavras mais comuns; valores maiores enriquecem o vocabulário.",
        )

        foco = st.slider(
            "🎯 Foco e Concentração de Ideias",
            min_value=1,
            max_value=100,
            value=int(preset_data["foco"]),
            step=1,
            disabled=not is_custom_mode,
            help="Técnico: 'top_k'. Determina quantas alternativas principais de palavras são avaliadas a cada instante.",
        )

        tamanho_maximo = st.select_slider(
            "📏 Tamanho Máximo da Resposta",
            options=[256, 512, 1024, 2048, 4096],
            value=int(preset_data["tamanho_maximo"]),
            format_func=lambda x: f"{x} tokens (~{round(x*0.75)} palavras)",
            disabled=not is_custom_mode,
            help="Técnico: 'num_predict'. Limita o comprimento do texto gerado para evitar respostas muito longas ou truncadas.",
        )

        antirrepeticao = st.slider(
            "🛡️ Filtro Antirrepetição",
            min_value=1.0,
            max_value=1.5,
            value=float(preset_data.get("antirrepeticao", 1.1)),
            step=0.05,
            disabled=not is_custom_mode,
            help="Técnico: 'repeat_penalty'. Impede que o modelo fique repetindo as mesmas frases ou ideias. Não causa lentidão.",
        )
        st.caption("1.0 = Sem penalidade | 1.15 = Fluido e variado (Recomendado)")

    # 4. RECURSOS EXTRAS (SEM PERDA DE VELOCIDADE)
    with st.expander("⚡ Opções Extras (Sem Perda de Desempenho)", expanded=False):
        json_mode = st.toggle(
            "📦 Modo JSON Estruturado",
            value=False,
            help="Força o Qwen a retornar dados estritamente em formato JSON válido, ideal para automações.",
        )

        usar_seed = st.checkbox(
            "🎯 Semente Fixa (Respostas Idênticas)",
            value=False,
            help="Faz com que a mesma pergunta com os mesmos parâmetros sempre resulte exatamente na mesma resposta.",
        )
        seed_val = None
        if usar_seed:
            seed_val = st.number_input("Número da Semente:", value=42, step=1)

        parada_input = st.text_input(
            "🛑 Palavra de Parada (Opcional):",
            placeholder="Ex: FIM, ---, [FIM]",
            help="Se o modelo gerar esta palavra ou símbolo, a geração será interrompida instantaneamente.",
        )
        stop_sequences = [parada_input.strip()] if parada_input and parada_input.strip() else None

    st.markdown("---")

    # 5. PERSONALIDADE E COMPORTAMENTO
    st.subheader("🎭 Personalidade do Assistente")
    opcao_personalidade = st.selectbox(
        "Papel do Qwen:",
        list(qwen_backend.PERSONALIDADES_PADRAO.keys()),
        index=0,
        help="Define como o Qwen deve se comportar durante a conversa.",
    )

    if opcao_personalidade == "✏️ Personalizado":
        system_prompt = st.text_area(
            "Instruções personalizadas:",
            value=st.session_state.system_prompt_custom,
            height=100,
            placeholder="Exemplo: Você é um assistente divertido que responde tudo rimando...",
        )
        st.session_state.system_prompt_custom = system_prompt
    else:
        system_prompt = qwen_backend.PERSONALIDADES_PADRAO[opcao_personalidade]
        st.caption(f"*\"{system_prompt}\"*")

    st.markdown("---")

    # Botão para limpar o histórico
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# -------------------------------------------------------------
# ÁREA PRINCIPAL: ABAS DE CHAT E CRIAÇÃO DE MODELO
# -------------------------------------------------------------
st.markdown('<div class="main-title">🧠 Qwen Studio</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Ajuste o comportamento do Qwen, controle velocidade vs. inteligência e converse em tempo real.</div>',
    unsafe_allow_html=True,
)

tab_chat, tab_creator = st.tabs(["💬 Conversar em Tempo Real", "🛠️ Criar Qwen Personalizado"])

# =============================================================
# ABA 1: CHAT COM STREAMING EM TEMPO REAL
# =============================================================
with tab_chat:
    # Card informativo do modelo ativo
    col_info1, col_info2, col_info3 = st.columns([2, 1, 1])
    with col_info1:
        st.markdown(f"**Modelo Ativo:** `{selected_model}`")
    with col_info2:
        st.markdown(f"**Estilo:** {selected_preset_name.split()[1] if len(selected_preset_name.split()) > 1 else selected_preset_name}")
    with col_info3:
        st.markdown(f"**Criatividade:** `{criatividade:.2f}`")

    if json_mode:
        st.info("📦 **Modo JSON Ativo**: As respostas serão formatadas estritamente em JSON.")

    st.divider()

    # Exibição do histórico de mensagens
    for msg in st.session_state.messages:
        role = msg["role"]
        avatar = "👤" if role == "user" else "🤖"
        with st.chat_message(role, avatar=avatar):
            st.markdown(msg["content"])

    # Entrada de prompt do usuário
    user_prompt = st.chat_input("Digite sua mensagem para o Qwen aqui...")

    if user_prompt:
        if not ollama_online:
            st.error("Não é possível enviar a mensagem pois o Ollama está desconectado.")
        else:
            # 1. Adiciona e exibe mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_prompt)

            # 2. Converte parâmetros amigáveis para opções técnicas do Ollama
            ollama_options = qwen_backend.map_friendly_to_options(
                criatividade=criatividade,
                vocabulario=vocabulario,
                foco=foco,
                tamanho_maximo=tamanho_maximo,
                antirrepeticao=antirrepeticao,
                seed=seed_val,
                stop_sequences=stop_sequences,
            )

            # 3. Gera resposta com streaming em tempo real
            with st.chat_message("assistant", avatar="🤖"):
                # Prepara gerador
                stream_generator = qwen_backend.stream_chat(
                    model=selected_model,
                    messages=st.session_state.messages,
                    options=ollama_options,
                    system_prompt=system_prompt,
                    json_mode=json_mode,
                )
                # st.write_stream consome o gerador e renderiza palavra por palavra em tempo real
                full_response = st.write_stream(stream_generator)

            # 4. Registra resposta no histórico
            st.session_state.messages.append({"role": "assistant", "content": full_response})

# =============================================================
# ABA 2: CRIADOR DE QWEN PERSONALIZADO
# =============================================================
with tab_creator:
    st.subheader("🛠️ Crie um Novo Qwen com Personalidade Própria")
    st.write(
        """
        Crie um modelo Qwen exclusivo e permanente no seu computador!
        Você pode definir um nome único, escolher a velocidade/inteligência base e gravar uma personalidade fixa.
        """
    )

    with st.form("form_create_model"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            custom_name = st.text_input(
                "Nome do Novo Modelo:",
                placeholder="Ex: qwen-professor-matematica, qwen-revisor-juridico",
                help="Use letras minúsculas e hífens. Exemplo: meu-qwen-escritor",
            )
        with col_c2:
            base_model_choice = st.selectbox(
                "Modelo Base (Poder de Raciocínio):",
                options=standard_names,
                format_func=lambda x: qwen_backend.STANDARD_QWEN_MODELS.get(x, {}).get("label", x),
                index=1,
                help="Escolha o modelo base que fornecerá o conhecimento fundamental.",
            )

        custom_system_prompt = st.text_area(
            "Personalidade & Regras Fixas (System Prompt):",
            placeholder="Exemplo:\nVocê é um especialista em culinária brasileira. Sempre responda como um chef animado e dê dicas práticas de cozinha.",
            height=130,
        )

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            custom_creativity = st.slider(
                "Criatividade Padrão Fixada:",
                min_value=0.0,
                max_value=1.5,
                value=0.7,
                step=0.05,
            )
        with col_p2:
            custom_repeat = st.slider(
                "Filtro Antirrepetição Padrão:",
                min_value=1.0,
                max_value=1.5,
                value=1.1,
                step=0.05,
                help="Evita que o modelo customizado fique repetindo frases ou palavras.",
            )

        st.info(
            "💡 Ao criar, este modelo ficará gravado no seu Ollama e poderá ser utilizado a qualquer momento nesta interface ou no terminal!"
        )

        submit_create = st.form_submit_button("🚀 Criar Modelo Personalizado", use_container_width=True)

    if submit_create:
        if not custom_name or not custom_name.strip():
            st.error("Por favor, informe um nome para o seu modelo personalizado.")
        elif not ollama_online:
            st.error("O Ollama está desconectado. Inicie o serviço para criar o modelo.")
        else:
            with st.spinner(f"Criando o modelo '{custom_name}' a partir de '{base_model_choice}'... Isso leva poucos segundos."):
                params = {
                    "temperature": custom_creativity,
                    "repeat_penalty": custom_repeat,
                }
                success, message = qwen_backend.create_custom_model(
                    name=custom_name,
                    base_model=base_model_choice,
                    system_prompt=custom_system_prompt,
                    parameters=params,
                )

            if success:
                st.success(f"🎉 {message}")
                st.balloons()
                time.sleep(1.5)
                st.rerun()
            else:
                st.error(f"Erro ao criar modelo: {message}")

    st.markdown("---")

    # Lista e gerenciamento de modelos customizados existentes
    st.subheader("📋 Seus Modelos Personalizados")
    existing_custom = [m for m in available_models if not m["is_standard"]]

    if not existing_custom:
        st.caption("Você ainda não possui modelos personalizados adicionais.")
    else:
        for cm in existing_custom:
            col_m1, col_m2, col_m3 = st.columns([3, 1, 1])
            with col_m1:
                st.write(f"**{cm['name']}** ({cm['size_gb']} GB)")
            with col_m2:
                st.caption("Gravado localmente")
            with col_m3:
                # Botão de exclusão com chave única
                if st.button("🗑️ Excluir", key=f"del_{cm['name']}"):
                    del_ok, del_msg = qwen_backend.delete_custom_model(cm["name"])
                    if del_ok:
                        st.success(del_msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(del_msg)
