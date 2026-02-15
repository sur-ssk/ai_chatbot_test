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
        # SDK v1.0.0以降の書き方に準拠
        client = genai.Client(api_key=api_key)
        
        # 3. システムプロンプト
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

        # 4. ユーザーの入力
        if prompt := st.chat_input("なにが しりたい？"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Geminiからの回答を生成
            with st.chat_message("assistant"):
                try:
                    # 最新SDKではモデル名に 'models/' を含めないのが正解な場合があります
                    # また、configの指定方法をよりシンプルにしています
                    response = client.models.generate_content(
                        model='gemini-1.5-flash', 
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=0.7
                        )
                    )
                    
                    if response.text:
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    else:
                        st.error("AIが回答を作れませんでした。")
                
                except Exception as e:
                    # 404が出た場合、自動で別パターンを試す
                    if "404" in str(e):
                        try:
                            # パターン2: models/ を付与した形式でリトライ
                            response = client.models.generate_content(
                                model='models/gemini-1.5-flash',
                                contents=prompt,
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
                            )
                            st.markdown(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
                        except Exception as e2:
                            st.error(f"モデルが見つかりません。APIキーの種類を確認してください。\n{e2}")
                    else:
                        st.error(f"エラー: {e}")
                    
    except Exception as init_error:
        st.error(f"初期化エラー: {init_error}")
else:
    st.info("← 左のサイドバーに APIキーをいれてね！")