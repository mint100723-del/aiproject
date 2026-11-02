import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="🌎 국가별 MBTI 탐험",
    page_icon="🌎",
    layout="wide"
)

# --------------------------------------------------
# 스타일
# --------------------------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 18px;
        color: #666666;
        text-align: center;
        margin-bottom: 30px;
    }

    .info-box {
        background-color: #f7f7fb;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    }

    .top-mbti {
        font-size: 32px;
        font-weight: 800;
        color: #ff1493;
    }

    .top-percent {
        font-size: 22px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df


df = load_data()

# MBTI 16개 유형
mbti_types = df.columns[1:].tolist()

# --------------------------------------------------
# 제목
# --------------------------------------------------
st.markdown(
    '<div class="main-title">🌎 국가별 MBTI 탐험</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '나라별 MBTI 비율을 한눈에 비교해보세요! ✨'
    '</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# 국가 선택
# --------------------------------------------------
st.subheader("🌍 국가를 선택해주세요")

selected_country = st.selectbox(
    "국가",
    df["Country"].tolist()
)

# --------------------------------------------------
# 선택한 국가 데이터 가져오기
# --------------------------------------------------
country_row = df[df["Country"] == selected_country].iloc[0]

mbti_data = country_row[mbti_types].astype(float)

# 높은 비율 순으로 정렬
mbti_sorted = mbti_data.sort_values(ascending=True)

# 1위 MBTI
top_mbti = mbti_data.idxmax()
top_value = mbti_data.max() * 100

# --------------------------------------------------
# 1위 정보 표시
# --------------------------------------------------
st.markdown(
    f"""
    <div class="info-box">
        <div style="font-size:20px;">
            🇺🇳 <b>{selected_country}</b>의 가장 높은 MBTI
        </div>
        <div class="top-mbti">
            {top_mbti}
        </div>
        <div class="top-percent">
            {top_value:.2f}%
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# 그래프
# --------------------------------------------------
st.subheader("📊 MBTI 비율")

fig, ax = plt.subplots(figsize=(11, 8))

# 값
values = mbti_sorted.values * 100
labels = mbti_sorted.index

# --------------------------------------------------
# 색상 만들기
# --------------------------------------------------
# 1위 = 핫핑크
hot_pink = "#FF1493"

# 나머지 = 남색 계열 그라데이션
dark_navy = np.array([18, 45, 90]) / 255
light_navy = np.array([180, 200, 230]) / 255

colors = []

# 현재 정렬은 낮은 값 → 높은 값
# 마지막 막대가 1위
for i in range(len(values)):
    if i == len(values) - 1:
        colors.append(hot_pink)
    else:
        ratio = i / (len(values) - 2) if len(values) > 2 else 0

        color = (
            dark_navy * (1 - ratio)
            + light_navy * ratio
        )

        colors.append(color)

# --------------------------------------------------
# 막대그래프
# --------------------------------------------------
bars = ax.barh(
    labels,
    values,
    color=colors,
    edgecolor="none",
    height=0.68
)

# --------------------------------------------------
# 퍼센트 표시
# --------------------------------------------------
max_value = max(values)

for bar, value in zip(bars, values):
    ax.text(
        value + max_value * 0.015,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.2f}%",
        va="center",
        fontsize=10,
        fontweight="bold"
    )

# --------------------------------------------------
# 그래프 디자인
# --------------------------------------------------
ax.set_xlabel(
    "MBTI 비율 (%)",
    fontsize=12,
    fontweight="bold"
)

ax.set_ylabel("")

ax.set_title(
    f"{selected_country}의 MBTI 비율",
    fontsize=20,
    fontweight="bold",
    pad=20
)

# 위쪽/오른쪽 테두리 제거
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# 왼쪽/아래쪽 테두리도 약하게
ax.spines["left"].set_alpha(0.3)
ax.spines["bottom"].set_alpha(0.3)

# 격자
ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.2
)

ax.set_axisbelow(True)

# x축 여백
ax.set_xlim(0, max_value * 1.18)

# 글자 크기
ax.tick_params(
    axis="y",
    labelsize=11
)

ax.tick_params(
    axis="x",
    labelsize=10
)

plt.tight_layout()

st.pyplot(fig)

# --------------------------------------------------
# TOP 3
# --------------------------------------------------
st.subheader("🏆 이 나라의 MBTI TOP 3")

top3 = mbti_data.sort_values(ascending=False).head(3)

col1, col2, col3 = st.columns(3)

medals = ["🥇", "🥈", "🥉"]

for i, (mbti, value) in enumerate(top3.items()):
    with [col1, col2, col3][i]:
        st.metric(
            f"{medals[i]} {i + 1}위",
            mbti,
            f"{value * 100:.2f}%"
        )

# --------------------------------------------------
# 데이터 표
# --------------------------------------------------
with st.expander("📋 전체 MBTI 비율 보기"):
    table = pd.DataFrame({
        "MBTI": mbti_data.sort_values(ascending=False).index,
        "비율": [
            f"{value * 100:.2f}%"
            for value in mbti_data.sort_values(ascending=False).values
        ]
    })

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# 안내 문구
# --------------------------------------------------
st.caption(
    "💡 이 결과는 제공된 데이터의 국가별 MBTI 비율을 시각화한 것입니다. "
    "특정 국가의 모든 사람을 대표하는 통계로 해석하지 않는 것이 좋아요."
)
