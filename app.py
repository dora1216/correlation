import pandas as pd
import plotly.express as px
import streamlit as st

# ページ設定
st.set_page_config(page_title="家計消費 相関チェッカー", layout="wide")
st.title("📊 家計消費データ 相関分析ダッシュボード")
st.caption("SSDSE-C-2026（2023-2025年平均・都道府県庁所在市）")

# 1. データの読み込みと整形
@st.cache_data
def load_data():
    # CSV読み込み（2行目の市名をヘッダーとして利用）
    df_raw = pd.read_csv("SSDSE-C-2026.csv", header=None)
    cities = df_raw.iloc[0, 2:].values  # 札幌市, 青森市, ...
    items = df_raw.iloc[1:, 1].values   # 世帯人員, 食料（合計）, 米, ...
    data = df_raw.iloc[1:, 2:].astype(float).values

    # 都市を行、品目を列にしたテーブルを作成（全国は除く場合は cities[1:] などで調整可能）
    df_tidy = pd.DataFrame(data.T, index=cities, columns=items)
    return df_tidy

df = load_data()
item_list = list(df.columns)

# 2. 項目選択（UI）
col1, col2 = st.columns(2)
with col1:
    x_item = st.selectbox("X軸にする項目", item_list, index=item_list.index("米") if "米" in item_list else 0)
with col2:
    y_item = st.selectbox("Y軸にする項目", item_list, index=item_list.index("みそ") if "みそ" in item_list else 1)

# 3. 相関係数の計算
corr = df[x_item].corr(df[y_item])

# 相関の強さの目安判定
if abs(corr) >= 0.7:
    strength = "強い相関あり"
elif abs(corr) >= 0.4:
    strength = "中程度の相関あり"
elif abs(corr) >= 0.2:
    strength = "弱い相関あり"
else:
    strength = "ほとんど相関なし"

# 指標の表示
st.metric(label=f"相関係数 (r)", value=f"{corr:.3f}", delta=strength, delta_color="off")

# 4. 散布図と近似直線の描画（Plotlyでインタラクティブに）
fig = px.scatter(
    df,
    x=x_item,
    y=y_item,
    hover_name=df.index,  # 点の上に都市名を表示
    trendline="ols",       # 最小二乗法による近似直線
    trendline_color_override="red",
    labels={x_item: f"{x_item} (円/人)", y_item: f"{y_item} (円/人)"},
    title=f"【{x_item}】 と 【{y_item}】 の散布図"
)
fig.update_layout(height=550)
st.plotly_chart(fig, use_container_width=True)