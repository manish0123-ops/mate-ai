
import streamlit as st
from ai_brain import ask_mate

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="MATE",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# CSS: DARK METALLIC / FROSTED GLASS INTERFACE
# --------------------------------------------------

st.markdown(
    """
    <style>
    /* Global reset */
    *,
    *::before,
    *::after {
        box-sizing: border-box;
    }

    html, body {
        margin: 0 !important;
        padding: 0 !important;
        min-height: 100% !important;
        background: #25292e !important;
        color: #e7e9ec !important;
    }

    /* Remove Streamlit chrome */
    #MainMenu,
    footer,
    header,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stSidebar"] {
        display: none !important;
    }

    /* Entire application background */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background-color: #25292e !important;
    }

    .stApp {
        min-height: 100vh !important;
        min-height: 100dvh !important;
        background:
            radial-gradient(
                ellipse at 50% 15%,
                rgba(173, 185, 197, 0.27) 0%,
                rgba(105, 116, 127, 0.13) 28%,
                transparent 62%
            ),
            repeating-linear-gradient(
                180deg,
                rgba(255,255,255,0.018) 0px,
                rgba(255,255,255,0.018) 1px,
                transparent 1px,
                transparent 4px
            ),
            linear-gradient(
                145deg,
                #202429 0%,
                #383e44 48%,
                #22262b 100%
            ) !important;
        background-attachment: fixed !important;
    }

    [data-testid="stMain"] {
        overflow-x: hidden !important;
    }

    [data-testid="stMainBlockContainer"] {
        width: 100% !important;
        max-width: none !important;
        min-height: 100vh !important;
        min-height: 100dvh !important;
        padding: 0 5vw 120px !important;
        margin: 0 auto !important;
    }

    /* Model badge */
    .model-badge {
        position: fixed;
        z-index: 1000;
        top: 22px;
        right: 24px;
        padding: 12px 18px;
        border: 1px solid rgba(225, 232, 240, 0.28);
        border-radius: 30px;
        background: rgba(210, 218, 226, 0.09);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        color: #e0e4e9;
        font-size: 13px;
        letter-spacing: 0.3px;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.08),
            0 5px 20px rgba(0,0,0,0.08);
    }

    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        margin-left: 8px;
        border-radius: 50%;
        background: #55d6a0;
        box-shadow: 0 0 9px rgba(85,214,160,0.55);
    }

    /* Welcome hero */
    .hero {
        min-height: 67vh;
        min-height: 67dvh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding-top: 10px;
        text-align: center;
    }

    .hero.compact {
        min-height: 160px;
        padding-top: 18px;
        padding-bottom: 10px;
    }

    /* Chrome orb */
    .orb {
        position: relative;
        width: 88px;
        height: 88px;
        border-radius: 50%;
        background:
            radial-gradient(
                circle at 28% 20%,
                #ffffff 0%,
                #dbe2e9 5%,
                #77838f 15%,
                #20262d 34%,
                #687480 48%,
                #151a20 66%,
                #5c6873 83%,
                #0d1116 100%
            );
        box-shadow:
            inset -8px -8px 16px rgba(0,0,0,0.75),
            inset 4px 4px 12px rgba(255,255,255,0.26),
            0 0 36px rgba(205,220,235,0.10),
            0 12px 28px rgba(0,0,0,0.28);
    }

    .orb::before {
        content: "";
        position: absolute;
        inset: 7px -2px;
        border: 2px solid transparent;
        border-top-color: rgba(245,249,255,0.90);
        border-left-color: rgba(192,211,229,0.55);
        border-bottom-color: rgba(112,151,187,0.70);
        border-radius: 50%;
        transform: rotate(-35deg) scale(1.03, 0.78);
        filter: drop-shadow(0 0 2px rgba(255,255,255,0.24));
    }

    .orb::after {
        content: "";
        position: absolute;
        width: 50px;
        height: 50px;
        left: -7px;
        top: 17px;
        border-top: 1px solid rgba(255,255,255,0.65);
        border-radius: 50%;
        transform: rotate(-52deg);
    }

    .hero.compact .orb {
        width: 49px;
        height: 49px;
    }

    .hero.compact .orb::after {
        width: 29px;
        height: 29px;
        top: 9px;
        left: -4px;
    }

    .hero.compact .orb::before {
        inset: 4px -1px;
        border-width: 1.5px;
    }

    .hello-title {
        margin-top: 22px;
        color: rgba(247,249,252,0.91);
        font-family: "Segoe UI Light", "Helvetica Neue", sans-serif;
        font-size: 35px;
        font-weight: 300;
        letter-spacing: -1.5px;
    }

    .hero.compact .hello-title {
        margin-top: 9px;
        font-size: 23px;
        letter-spacing: -0.5px;
    }

    /* Hide default avatars */
    [data-testid="stChatMessageAvatar"],
    [data-testid="chatAvatarIcon"],
    [data-testid="chatAvatarImage"] {
        display: none !important;
    }

    /* Chat message layout */
    [data-testid="stChatMessage"] {
        width: min(900px, 100%) !important;
        margin: 0 auto 16px auto !important;
        padding: 17px 22px !important;
        border: 1px solid rgba(220,230,240,0.15) !important;
        border-radius: 20px !important;
        background: rgba(205,216,228,0.075) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.035),
            0 8px 24px rgba(0,0,0,0.045);
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        color: #e8ebef !important;
        font-size: 15px;
        line-height: 1.75;
        overflow-wrap: anywhere;
    }

    [data-testid="stChatMessage"] p {
        color: #e8ebef !important;
    }

    /* Remove unnecessary chat container backgrounds */
    [data-testid="stVerticalBlock"] > div:has(> [data-testid="stChatMessage"]) {
        background: transparent !important;
    }

    /* Bottom input area */
    [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
        background-color: transparent !important;
        border-top: none !important;
        box-shadow: none !important;
    }

    [data-testid="stBottom"] {
        padding-top: 12px !important;
        padding-bottom: 16px !important;
    }

    [data-testid="stChatInput"] {
        width: min(850px, calc(100vw - 40px)) !important;
        margin: 0 auto !important;
        border: 1px solid rgba(226,233,242,0.48) !important;
        border-radius: 40px !important;
        background: rgba(40,45,53,0.78) !important;
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        box-shadow:
            inset 0 1px 2px rgba(255,255,255,0.10),
            0 8px 30px rgba(0,0,0,0.17) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #f0f2f5 !important;
        background: transparent !important;
        font-size: 15px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #b9bec6 !important;
    }

    [data-testid="stChatInput"] button {
        color: #e0e5eb !important;
        background: rgba(225,232,240,0.12) !important;
        border-radius: 12px !important;
    }

    /* Links and code */
    [data-testid="stChatMessage"] a {
        color: #c6dced !important;
    }

    [data-testid="stChatMessage"] pre {
        border: 1px solid rgba(220,230,240,0.12);
        border-radius: 12px;
        background: rgba(8,12,17,0.45) !important;
    }

    /* Responsive layout */
    @media (max-width: 900px) {
        [data-testid="stMainBlockContainer"] {
            padding-left: 22px !important;
            padding-right: 22px !important;
        }

        .model-badge {
            top: 14px;
            right: 14px;
            padding: 9px 12px;
            font-size: 11px;
        }

        .hero {
            min-height: 60vh;
            min-height: 60dvh;
        }
    }

    @media (max-width: 600px) {
        [data-testid="stMainBlockContainer"] {
            padding-left: 12px !important;
            padding-right: 12px !important;
            padding-bottom: 100px !important;
        }

        .orb {
            width: 70px;
            height: 70px;
        }

        .hello-title {
            font-size: 30px;
        }

        .hero.compact {
            min-height: 125px;
        }

        [data-testid="stChatMessage"] {
            padding: 12px 14px !important;
            border-radius: 16px !important;
        }

        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
            font-size: 14px;
        }

        [data-testid="stChatInput"] {
            width: calc(100vw - 24px) !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# MODEL BADGE
# --------------------------------------------------

st.markdown(
    """
    <div class="model-badge">
        Model: Llama 3.2 3B
        <span class="status-dot"></span>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------

has_messages = len(st.session_state.messages) > 0
hero_class = "hero compact" if has_messages else "hero"

st.markdown(
    f"""
    <div class="{hero_class}">
        <div class="orb"></div>
        <div class="hello-title">Hello</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# DISPLAY CONVERSATION
# --------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=None):
        st.markdown(message["content"])

# --------------------------------------------------
# CHAT INPUT AND LOCAL AI RESPONSE
# --------------------------------------------------

prompt = st.chat_input("Type a message...")

if prompt:
    # Display and save the user's message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    # Generate a response using the existing local Ollama brain
    try:
        response = ask_mate(prompt)

        if response is None:
            response = "I couldn't generate a response. Please try again."
        else:
            response = str(response)

    except Exception as error:
        response = (
            "I couldn't connect to the local AI model.\n\n"
            "Please check that Ollama is running and that "
            "your configured model is available.\n\n"
            f"Technical details: {error}"
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    st.rerun()
