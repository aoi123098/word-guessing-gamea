import streamlit as st
import pandas as pd

@st.cache_data
def load_words():
    try:
        df = pd.read_excel("words.xlsx") 
        raw_list = df["単語"].dropna().astype(str).tolist()
        
        # 【新機能】入力された単語から「代表名」を探し出すための辞書（マップ）を作ります
        word_mapping = {}
        
        for item in raw_list:
            # カンマで区切られた複数の呼び名をバラバラにする
            # （「、」全角カンマが混ざっていても大丈夫なように変換してから分割）
            parts = [p.strip().lower() for p in item.replace('、', ',').split(',')]
            
            if not parts or not parts[0]:
                continue
            
            # リストの1番目に書かれているものを「代表名」とする
            main_word = parts[0]
            
            # 略称を含め、すべての呼び名を代表名に紐付ける
            for p in parts:
                if p:
                    word_mapping[p] = main_word
                    
        return word_mapping
        
    except Exception as e:
        st.error("エラー: ファイルが見つからないか、読み込めません。")
        return {}

# 辞書データを読み込む
valid_words_dict = load_words()

# 状態の保存
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'used_words' not in st.session_state:
    st.session_state.used_words = set()
if 'results' not in st.session_state:
    st.session_state.results = []

st.title("🎮 単語判定ゲーム")
st.write("リストにある単語を入力してポイントをゲットしよう！大文字・小文字はどちらでもOKです。略称でも正解になります！")
st.info("💡 ヒント: 複数入力する場合は、**改行（Enter）**をして1行に1つずつ入力してください。")

# 現在のスコアを大きく表示
st.metric(label="現在のスコア", value=f"{st.session_state.score} ポイント")

# 直近の判定結果をまとめて表示
if st.session_state.results:
    for res in st.session_state.results:
        if "⭕️" in res:
            st.success(res)
        elif "❌" in res:
            st.error(res)
        else:
            st.warning(res)

# 入力フォーム
with st.form(key='word_form', clear_on_submit=True):
    user_input = st.text_area("単語を入力してください（複数入力OK！）:")
    submit_button = st.form_submit_button(label='まとめて判定！')

# まとめて判定するロジック
if submit_button:
    if user_input.strip():
        # 改行で分割
        raw_words = user_input.split('\n')
        
        st.session_state.results = []
        
        for word in raw_words:
            original_input = word.strip()
            if not original_input:
                continue 
                
            check_word = original_input.lower()

            # 【新機能】入力された単語が辞書（リスト）にあるかチェック
            if check_word in valid_words_dict:
                # 入力された単語に紐づく「代表名」を取得
                main_word = valid_words_dict[check_word]
                
                # 代表名がすでに回答済みかチェック（二重取り防止）
                if main_word in st.session_state.used_words:
                     st.session_state.results.append(f"⚠️ '{original_input}'（またはその別名）はすでに入力済みです！")
                else:
                    st.session_state.score += 1
                    # 回答済みの箱には「代表名」を入れる
                    st.session_state.used_words.add(main_word)
                    st.session_state.results.append(f"⭕️ 正解！ '{original_input}' で1ポイント追加！")
            else:
                st.session_state.results.append(f"❌ 残念！ '{original_input}' はリストにありません。")
        
        st.rerun()