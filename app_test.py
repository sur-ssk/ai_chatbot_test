import streamlit as st
from google import genai
from google.genai import types

# 1. 画面の設定
st.set_page_config(page_title="こども質問箱", page_icon="🐣")
st.title("🐣 こども質問箱")
st.caption("3さい〜10さいのみんなの ぎもんに こたえるよ！")

# 2. APIキーの設定（公開時はStreamlitの管理画面で設定します）
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
    
    # 3. システムプロンプト（ボットの性格を決める）
    SYSTEM_PROMPT = """
    あなたは「こども質問箱」の優しい先生です。
    - 3歳から10歳の子供が理解できる言葉を使ってください。
    - 漢字には（）で読みがなを振るか、平仮名を多めにしてください。
    - 回答は短く、3文以内で答えてください。
    - 例え話を使い、ワクワクするような教え方をしてください。
    - 危険なことや悪いことについては、優しく諭してください。
    """

    # チャット履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザーの入力
    if prompt := st.chat_input("なにが しりたい？"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Geminiからの回答
        with st.chat_message("assistant"):
            config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                config=config,
                contents=prompt
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
else:
    st.warning("左側のメニューに APIキーを いれてね！")