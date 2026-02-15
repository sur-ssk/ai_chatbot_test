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
        # クライアントの初期化
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
                    config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
                    
                    # 【重要】404対策：モデル名をフルパス「models/gemini-2.0-flash」で指定
                    # これにより、ライブラリがモデルを見失うのを防ぎます
                    response = client.models.generate_content(
                        model="models/gemini-2.0-flash", 
                        config=config,
                        contents=prompt
                    )
                    
                    if response.text:
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    else:
                        st.error("AIが回答を作れませんでした。")
                
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str:
                        st.error("混み合っています。1分待ってください。")
                    elif "404" in error_str:
                        # まだ404が出る場合の予備：別名で再試行
                        st.error("モデルが見つかりません。名前を models/gemini-1.5-flash に変えて試します...")
                        try:
                            response = client.models.generate_content(
                                model="models/gemini-1.5-flash", 
                                config=config,
                                contents=prompt
                            )
                            st.markdown(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
                        except:
                            st.error("やはり接続できません。APIキーの設定を確認してください。")
                    else:
                        st.error(f"エラーが発生しました: {error_str}")
                    
    except Exception as init_error:
        st.error(f"初期化エラー: {init_error}")
else:
    st.info("← 左のサイドバーに APIキーをいれてね！")
