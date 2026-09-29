import pandas as pd
import plotly.express as px
import streamlit as st

# ページ基本設定
st.set_page_config(page_title="家計消費 相関チェッカー", layout="wide")
st.title("📊 家計消費データ 相関分析ダッシュボード")
st.caption("SSDSE-C-2026（2023-2025年平均・47都道府県庁所在市）")

# 1. 正しい列・行の位置からデータを読み込む
@st.cache_data
def load_data():
    # 文字コードの自動判定読み込み
    try:
        df_raw = pd.read_csv("SSDSE-C-2026.csv", header=None, encoding="cp932")
    except UnicodeDecodeError:
        df_raw = pd.read_csv("SSDSE-C-2026.csv", header=None, encoding="utf-8")

    # 項目名: 2行目(index 1)の D列以降(index 3:)
    item_names = df_raw.iloc[1, 3:].values

    # 都道府県・都市名: 3行目以降(index 2:)の B列(都道府県)と C列(市)
    prefs = df_raw.iloc[2:, 1].values
    cities = df_raw.iloc[2:, 2].values
    city_labels = [f"{p} ({c})" if p != c else c for p, c in zip(prefs, cities)]

    # 数値データ: 3行目以降(index 2:)の D列以降(index 3:)
    data_values = df_raw.iloc[2:, 3:].astype(float).values

    # DataFrame作成（行: 都市ラベル、列: 品目名）
    df_clean = pd.DataFrame(data_values, index=city_labels, columns=item_names)

    # 47都道府県比較のため、「全国」データ行は除外
    if "全国" in df_clean.index:
        df_clean = df_clean.drop(index="全国")

    return df_clean

df = load_data()
item_list = list(df.columns)

# 2. 項目選択（UI）
col1, col2 = st.columns(2)
with col1:
    default_x = item_list.index("米") if "米" in item_list else 0
    x_item = st.selectbox("X軸にする項目", item_list, index=default_x)
with col2:
    default_y = item_list.index("みそ") if "みそ" in item_list else (1 if len(item_list) > 1 else 0)
    y_item = st.selectbox("Y軸にする項目", item_list, index=default_y)

# 3. 相関係数の計算と判定
corr = df[x_item].corr(df[y_item])

if abs(corr) >= 0.7:
    strength = "強い相関あり"
elif abs(corr) >= 0.4:
    strength = "中程度の相関あり"
elif abs(corr) >= 0.2:
    strength = "弱い相関あり"
else:
    strength = "ほとんど相関なし"

st.metric(label="相関係数 (r)", value=f"{corr:.3f}", delta=strength, delta_color="off")

# 4. インタラクティブな散布図と近似直線（Plotly）
fig = px.scatter(
    df,
    x=x_item,
    y=y_item,
    hover_name=df.index,
    trendline="ols",
    trendline_color_override="red",
    labels={x_item: f"{x_item} (円/人)", y_item: f"{y_item} (円/人)"},
    title=f"【{x_item}】 と 【{y_item}】 の散布図（47都道府県庁所在市）"
)
fig.update_layout(height=550)
st.plotly_chart(fig, use_container_width=True)
