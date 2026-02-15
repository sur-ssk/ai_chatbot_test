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
        
        # 3. システムプロンプト（子供向けのふるまいを定義）
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
                    # モデル名を最新ライブラリが最も認識しやすい形式に変更
                    config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
                    
                    response = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        config=config,
                        contents=prompt
                    )
                    
                    # 回答を表示して履歴に保存
                    if response.text:
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    else:
                        st.error("AIがうまく言葉を見つけられなかったみたい。別の聞き方をしてね。")
                
                except Exception as e:
                    # エラーメッセージの分岐
                    error_str = str(e)
                    if "429" in error_str:
                        st.error("ごめんね。いま ほかの人も たくさん質問していて、AIがお疲れみたい。1分くらい まってから、もういちど 送ってね。")
                    elif "404" in error_str:
                        st.error("モデルが見つかりませんでした。APIの設定を確認してください。")
                    else:
                        st.error("ごめんね、うまく 答えられなかったよ。もういちど きいてみてね！")
                    
                    # 開発者デバッグ用の詳細（不要になったら消してもOK）
                    with st.expander("エラーの詳細を確認する"):
                        st.write(e)
                    
    except Exception as init_error:
        st.error("アプリの準備中にエラーが起きました。APIキーが正しいか確認してね！")
else:
    st.info("← 左がわのメニューに APIキーを いれてね！")
    st.markdown("""
    ### つかいかた
    1. [Google AI Studio](https://aistudio.google.com/app/apikey) でキーをもらってきます。
    2. 左の空欄（サイドバー）に貼り付けます。
    3. 下の入力欄（チャット欄）で質問してみてね！
    """)
