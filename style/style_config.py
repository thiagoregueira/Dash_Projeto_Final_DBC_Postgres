import streamlit as st

# Cores do tema
COLORS = {
    "text": "#FFFFFF",
    "background": "#04314A",
    "background_graph": "#1E1E1E",
    "primary": "#00BFA5",
    "secondary": "#0288D1",
    "accent": "#0277BD",
    "dark_blue": "#1E1E1E",
}

# Fonte
FONT = "Montserrat"


def apply_custom_style():
    # Adicionar logo na sidebar antes de qualquer outro conteúdo
    import streamlit as st

    st.sidebar.image("images/logo/logo_branca.png", width=150)
    st.sidebar.markdown("---")

    # Aplicar CSS customizado
    st.markdown(
        f"""
        <style>
        /* Fonte principal */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Estilo global */
        body {{
            font-family: '{FONT}', sans-serif;
            background-color: {COLORS["background"]};
            color: {COLORS["text"]};
        }}
        
        /* Títulos */
        h1, h2, h3 {{
            font-family: 'Inter', sans-serif;
            color: {COLORS["text"]};
        }}
        
        /* Links */
        a {{
            color: {COLORS["primary"]} !important;
        }}
        
        /* Botões */
        .stButton > button {{
            background-color: {COLORS["primary"]};
            color: {COLORS["text"]};
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-family: '{FONT}', sans-serif;
        }}
        
        .stButton > button:hover {{
            background-color: {COLORS["secondary"]};
        }}
        
        /* Selectbox */
        .stSelectbox > div > div {{
            background-color: {COLORS["background"]};
            color: {COLORS["text"]};
            border-color: {COLORS["primary"]};
        }}
        
        /* Cards/Métricas */
        [data-testid="stMetricValue"] {{
            font-family: '{FONT}', sans-serif;
            color: {COLORS["text"]};
            background-color: {COLORS["dark_blue"]};
            padding: 0.5rem;
            border-radius: 4px;
        }}
        
        [data-testid="stMetricLabel"] {{
            font-family: '{FONT}', sans-serif;
            color: {COLORS["text"]};
        }}
        
        /* Gráficos */
        .js-plotly-plot {{
            background-color: {COLORS["background_graph"]};
        }}
        
        .js-plotly-plot .plotly .modebar {{
            background-color: {COLORS["background_graph"]};
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {COLORS["background"]};
            border-right: 1px solid {COLORS["primary"]};
        }}
        
        /* Cabeçalho da página */
        .stApp header {{
            background-color: {COLORS["background"]};
            border-bottom: 1px solid {COLORS["primary"]};
        }}
        
        /* Rodapé */
        footer {{
            border-top: 1px solid {COLORS["primary"]};
            padding-top: 1rem;
            margin-top: 2rem;
            color: {COLORS["text"]};
        }}
        </style>
    """,
        unsafe_allow_html=True,
    )


def add_footer():
    """
    Adiciona um footer padronizado.
    Inclui informações de contato, termos de uso, privacidade e links úteis.
    """

    # CSS para ajustar o posicionamento
    st.markdown(
        """
    <style>
    .footer-container {
        display: flex;
        justify-content: space-between;
        padding: 20px;
        background-color: #002F6C;
        color: white;
    }

    .footer-section {
        flex: 1;
        padding: 10px;
        align-items: center;
        align-text: center;
        justify-content: center;
        display: flex;
    }
    
    .language-container {
        margin-right: 100px;
        display: flex;
        gap: 10px;
        justify-content: flex-end;
        margin-top: 10px;
        align-items: flex-start;
    }

    .language-button {
        background-color: #04314A;
        padding: 5px 15px;
        border-radius: 12px;
        color: white;
        text-decoration: none;
        text-align: center;
        min-width: 40px;
    }

    .footer-title1 {
        font-size: 20px;
        margin-bottom: 15px;
        margin-left: 250px;
        margin-top: 50px;
        display: flex;
    }

    .footer-title2 {
        font-size: 20px;
        margin-bottom: 15px;
        margin-left: 275px;
        margin-top: 1px;
        display: flex;
    }

    .footer-texttermo {
        margin-left: 100px;
    }

    .footer-textseg {
        margin-left: 100px;
    }

    .footer-textajuda {
        margin-left: 100px;
    }
    
    .footer-textcap {
        margin-bottom: 1px;
        margin-left: 100px;
    }

    .footer-textfone {
        margin-bottom: 25px;
        margin-left: 100px;
    }

    .footer-textloc {
        margin-top: 20px;
        margin-left: 100px;
    }

    .footer-texttel {
        margin-left: 100px;
        margin-bottom: 30px;
    }

    .footer-texttermo {
        margin-bottom: 30px;
    }

    .footer-textseg {
        margin-bottom: 30px;
    }

    .footer-textajuda {
        margin-bottom: 30px;
    }

    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")



    st.markdown(
            '<div class="footer-section">', unsafe_allow_html=True
        )
    
    # Criar três colunas para o footer
    col1, col2, col3, col4 = st.columns(4)
            
        
    # Primeira coluna: Termos e Privacidade
    with col1:

        st.markdown(
            '<div class="footer-section">',
            unsafe_allow_html=True,
        )
        
        st.markdown(
            '<div class="footer-texttermo">Termos de uso e privacidade</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="footer-textseg">Segurança</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="footer-textajuda">Precisa de ajuda?</div>', unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Segunda coluna: Contato
    with col2:
        st.markdown(
            '<div class="footer-section">',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="footer-textcap">Capitais e regiões metropolitanas</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="footer-textfone">4003 2341</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="footer-textloc">Demais localidades</div>', unsafe_allow_html=True
        )
        st.markdown(
            '<div class="footer-texttel">0800 545 2341</div>', unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Terceira coluna: Acompanhe
    with col3:
        st.markdown(
            '<div class="footer-section">',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="footer-title1">Acompanhe</div>', unsafe_allow_html=True)
        st.markdown('<div class="footer-title2">FAQ 🕾</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown(
            '<div class="footer-section">',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="language-container">
            <a href="#" class="language-button" style="color: white !important;">PT</a>
            <a href="#" class="language-button" style="color: white !important;">EN</a>
            <a href="#" class="language-button" style="color: white !important;">ES</a>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Informações da empresa
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; font-size: 12px;'>2025 FinUp Finanças S.A CNPJ: 54.123.654/0001-23</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align: center; font-size: 12px;'>Rua dos Sonhos, 123, Bairro Esperança, Cidade Horizonte, Estado Luminar, CEP 45678-901.</div>",
        unsafe_allow_html=True,
    )


def get_theme():
    return {
        "primaryColor": COLORS["primary"],
        "backgroundColor": COLORS["background"],
        "secondaryBackgroundColor": COLORS["dark_blue"],
        "textColor": COLORS["text"],
        "font": FONT,
    }
