import streamlit as st
from google import genai
from google.genai import types

# 1. 画面の設定
st.set_page_config(page_title="こども質問箱", page_icon="🐣")
st.title("🐣 こども質問箱")
st.caption("3さい〜10さいのみんなの ぎもんに こたえるよ！")

# 2. APIキーの設定
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    try:
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
                try:
                    # モデルを安定版の「gemini-2.0-flash」に変更
                    config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
                    response = client.models.generate_content(
                        model="gemini-2.0-flash", 
                        config=config,
                        contents=prompt
                    )
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                except Exception as e:
                    # サーバーエラーなどが起きた場合の優しいフォロー
                    error_msg = "ごめんね、いま ちょっと かんがえ中（ちゅう）で 答えられないんだ。もういちど きいてみてね！"
                    st.error(error_msg)
                    # ログを確認したい場合は st.write(e) を追加してもOK
                    
    except Exception as init_error:
        st.error("APIキーが まちがっているみたいだよ。かくにんしてみてね！")
else:
    st.warning("左側のメニューに APIキーを いれてね！")