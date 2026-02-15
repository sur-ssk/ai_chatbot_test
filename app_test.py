import streamlit as st
from google import genai
from google.genai import types

# 1. 画面の設定
st.set_page_config(page_title="こども質問箱", page_icon="🐣")
st.title("🐣 こども質問箱")
st.caption("3さい〜10さいのみんなの ぎもんに こたえるよ！")

# 2. APIキーの設定
# 画面左側のサイドバーに入力欄を表示します
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    try:
        # クライアントの初期化
        client = genai.Client(api_key=api_key)
        
        # 3. システムプロンプト（こども向けのルール）
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
            # ユーザーの質問を履歴に追加
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Geminiからの回答を生成
            with st.chat_message("assistant"):
                try:
                    # 429エラー対策として、最も安定した gemini-1.5-flash を採用
                    config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
                    response = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        config=config,
                        contents=prompt
                    )
                    
                    # 回答を表示して履歴に保存
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                except Exception as e:
                    # エラーが起きた時の表示
                    if "429" in str(e):
                        st.error("ごめんね。いま ほかの人も たくさん質問（しつもん）していて、AIがお疲れ（つかれ）みたい。1分（いっぷん）くらい まってから、もういちど 送ってね。")
                    else:
                        st.error("ごめんね、うまく 答えられなかったよ。もういちど きいてみてね！")
                    
                    # 開発者向けにエラー詳細を小さく表示
                    with st.expander("エラーのくわしい内容（ないよう）"):
                        st.write(e)
                    
    except Exception as init_error:
        st.error("APIキーが まちがっているか、うまく動（うご）いていないみたい。設定（せってい）を かくにんしてね！")
else:
    st.info("← 左がわのメニューに APIキーを いれてね！")
    st.markdown("""
    ### つかいかた
    1. [Google AI Studio](https://aistudio.google.com/app/apikey) でキーをもらってきます。
    2. 左の空欄（くうらん）に貼り付けます。
    3. 下の入力欄（にゅうりょくらん）で質問（しつもん）してみてね！
    """)