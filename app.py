import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="家計消費 相関チェッカー", layout="wide")
st.title("📊 家計消費データ 相関分析ダッシュボード")
st.caption("SSDSE-C-2026（2023-2025年平均・47都道府県庁所在市）")

# 1. データの読み込み
@st.cache_data
def load_data():
    try:
        df_raw = pd.read_csv("SSDSE-C-2026.csv", header=None, encoding="cp932")
    except UnicodeDecodeError:
        df_raw = pd.read_csv("SSDSE-C-2026.csv", header=None, encoding="utf-8")

    codes = df_raw.iloc[0, 3:].values
    item_names = df_raw.iloc[1, 3:].values
    prefs = df_raw.iloc[2:, 1].values
    cities = df_raw.iloc[2:, 2].values
    city_labels = [f"{p} ({c})" if p != c else c for p, c in zip(prefs, cities)]
    data_values = df_raw.iloc[2:, 3:].astype(float).values

    df_clean = pd.DataFrame(data_values, index=city_labels, columns=item_names)
    if "全国" in df_clean.index:
        df_clean = df_clean.drop(index="全国")

    # 大分類マッピング
    category_map = {}
    for code, name in zip(codes, item_names):
        c = str(code).strip()
        if c.startswith("LA"):
            cat = "基本指標"
        elif c.startswith("LB00"):
            cat = "食料合計"
        elif c.startswith("LB01"):
            cat = "01 穀類"
        elif c.startswith("LB02"):
            cat = "02 魚介類"
        elif c.startswith("LB03"):
            cat = "03 肉類"
        elif c.startswith("LB04"):
            cat = "04 乳卵類"
        elif c.startswith("LB05"):
            cat = "05 野菜・海藻"
        elif c.startswith("LB06"):
            cat = "06 果物"
        elif c.startswith("LB07"):
            cat = "07 油脂・調味料"
        elif c.startswith("LB08"):
            cat = "08 菓子類"
        elif c.startswith("LB09"):
            cat = "09 調理食品"
        elif c.startswith("LB10"):
            cat = "10 飲料"
        elif c.startswith("LB11"):
            cat = "11 酒類"
        elif c.startswith("LB12"):
            cat = "12 外食・給食"
        else:
            cat = "その他"
        category_map[name] = cat

    return df_clean, category_map

df, cat_map = load_data()
all_items = list(df.columns)
categories = ["すべて"] + sorted(list(set(cat_map.values())))

# --- セッションステート初期化 ---
if "box_x" not in st.session_state:
    st.session_state.box_x = "米"
if "box_y" not in st.session_state:
    st.session_state.box_y = "食パン"
if "cat_x" not in st.session_state:
    st.session_state.cat_x = "すべて"
if "cat_y" not in st.session_state:
    st.session_state.cat_y = "すべて"

# プリセット反映用関数
def set_preset(x_val, y_val):
    st.session_state.cat_x = "すべて"
    st.session_state.cat_y = "すべて"
    st.session_state.box_x = x_val
    st.session_state.box_y = y_val
    st.rerun()

# --- プリセット（おすすめペア）ボタン ---
st.subheader("💡 おすすめの探究テーマ（ワンタップ選択）")
col_p1, col_p2, col_p3, col_p4 = st.columns(4)

with col_p1:
    if st.button("🍚 米 vs 🍞 食パン", use_container_width=True):
        set_preset("米", "食パン")
with col_p2:
    if st.button("🍜 中華麺 vs 🥟 ぎょうざ", use_container_width=True):
        set_preset("中華麺", "ぎょうざ")
with col_p3:
    if st.button("🍞 食パン vs 🧈マーガリン", use_container_width=True):
        set_preset("食パン", "マーガリン")
with col_p4:
    if st.button("☕ 喫茶代 vs 🍺 飲酒代", use_container_width=True):
        set_preset("喫茶代", "飲酒代")

st.markdown("---")

# --- 項目選択エリア ---
col_x, col_y = st.columns(2)

with col_x:
    st.write("### 🔵 X軸（横軸）の設定")
    cat_x = st.selectbox("X軸のカテゴリ絞り込み", categories, key="cat_x")
    items_x = [it for it in all_items if cat_x == "すべて" or cat_map.get(it) == cat_x]

    # 現在の選択値が絞り込みリストにない場合は先頭を選択
    if st.session_state.box_x not in items_x:
        st.session_state.box_x = items_x[0]
    
    idx_x = items_x.index(st.session_state.box_x)
    x_item = st.selectbox("X軸の項目を選択", items_x, index=idx_x, key="box_x")

with col_y:
    st.write("### 🔴 Y軸（縦軸）の設定")
    cat_y = st.selectbox("Y軸のカテゴリ絞り込み", categories, key="cat_y")
    items_y = [it for it in all_items if cat_y == "すべて" or cat_map.get(it) == cat_y]

    if st.session_state.box_y not in items_y:
        st.session_state.box_y = items_y[0]
    
    idx_y = items_y.index(st.session_state.box_y)
    y_item = st.selectbox("Y軸の項目を選択", items_y, index=idx_y, key="box_y")

# --- 相関係数の計算と判定 ---
corr = df[x_item].corr(df[y_item])

if abs(corr) >= 0.7:
    strength = "強い相関あり"
elif abs(corr) >= 0.4:
    strength = "中程度の相関あり"
elif abs(corr) >= 0.2:
    strength = "弱い相関あり"
else:
    strength = "ほとんど相関なし"

direction = "正の相関（右上がり）" if corr > 0 else "負の相関（右下がり）"
st.metric(
    label="相関係数 (r)", 
    value=f"{corr:.3f}", 
    delta=f"{strength}・{direction}" if abs(corr) >= 0.2 else strength,
    delta_color="off"
)

# --- 散布図の描画 ---
show_labels = st.checkbox("散布図にすべての都市名を表示する", value=False)

fig = px.scatter(
    df,
    x=x_item,
    y=y_item,
    hover_name=df.index,
    text=df.index if show_labels else None,
    trendline="ols",
    trendline_color_override="red",
    labels={x_item: f"{x_item} (円/人)", y_item: f"{y_item} (円/人)"},
    title=f"【{x_item}】 と 【{y_item}】 の散布図（47都道府県庁所在市）"
)
if show_labels:
    fig.update_traces(textposition="top right")

fig.update_layout(height=580)
st.plotly_chart(fig, use_container_width=True)
