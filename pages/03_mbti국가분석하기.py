import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from pathlib import Path
import html


# ==================================================
# 페이지 설정
# ==================================================
st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌎",
    layout="wide"
)


# ==================================================
# MBTI 목록
# ==================================================
MBTI_TYPES = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]


# ==================================================
# CSS 디자인
# HTML 카드 사용하지 않음
# ==================================================
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 36px;
        font-weight: 800;
        color: #17345E;
        padding: 15px 0 5px 0;
    }

    .main-subtitle {
        text-align: center;
        color: gray;
        font-size: 16px;
        margin-bottom: 25px;
    }

    h2, h3 {
        color: #17345E;
    }
</style>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="main-title">🌎 국가별 MBTI 분석</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">16가지 MBTI로 세계 여러 나라를 비교해 보세요! 🧠</div>',
    unsafe_allow_html=True
)


# ==================================================
# CSV 파일 경로
# pages 폴더의 상위 폴더에서 CSV 찾기
# ==================================================
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "countriesMBTI_16types.csv"


# ==================================================
# 데이터 불러오기
# ==================================================
@st.cache_data
def load_data(file_path):

    data = pd.read_csv(file_path)

    data.columns = data.columns.str.strip()

    if "Country" not in data.columns:
        raise ValueError("CSV에 Country 컬럼이 없습니다.")

    data["Country"] = data["Country"].astype(str).str.strip()

    for mbti in MBTI_TYPES:
        if mbti not in data.columns:
            raise ValueError(f"{mbti} 컬럼이 CSV에 없습니다.")

        data[mbti] = pd.to_numeric(
            data[mbti],
            errors="coerce"
        )

    return data


try:
    df = load_data(str(CSV_PATH))

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info("countriesMBTI_16types.csv 파일을 최상위 폴더에 넣어주세요.")
    st.stop()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()


# ==================================================
# 그래프 HTML 생성
# ==================================================
def make_bar_chart(labels, values, title, max_height=330):

    if not labels:
        return "<p>표시할 데이터가 없습니다.</p>"

    max_value = max(values) if max(values) > 0 else 1
    total = len(labels)

    bars = []

    for i, (label, value) in enumerate(zip(labels, values)):

        # 1위 핫핑크
        if i == 0:
            color = "#FF1493"

        # 나머지 네이비 그라데이션
        else:
            ratio = i / max(total - 1, 1)

            r = int(15 + (120 - 15) * ratio)
            g = int(35 + (145 - 35) * ratio)
            b = int(80 + (205 - 80) * ratio)

            color = f"rgb({r},{g},{b})"

        height = max((value / max_value) * max_height, 3)

        safe_label = html.escape(str(label))

        bars.append(f"""
            <div class="bar-item">
                <div class="bar-value">{value:.2f}%</div>

                <div class="bar-area">
                    <div class="bar"
                         style="height:{height:.1f}px;
                                background:{color};">
                    </div>
                </div>

                <div class="bar-label">{safe_label}</div>
            </div>
        """)

    bars_html = "".join(bars)
    safe_title = html.escape(title)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 15px 5px;
            font-family: Arial, sans-serif;
            background: transparent;
        }}

        .chart-title {{
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            color: #17345E;
            margin-bottom: 20px;
        }}

        .scroll {{
            width: 100%;
            overflow-x: auto;
            padding: 10px 5px 20px 5px;
        }}

        .chart {{
            display: flex;
            align-items: flex-end;
            gap: 12px;
            min-width: max-content;
            height: {max_height + 100}px;
            padding: 10px 15px 0 15px;
            border-bottom: 2px solid #17345E;
        }}

        .bar-item {{
            width: 62px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
        }}

        .bar-value {{
            font-size: 12px;
            font-weight: bold;
            color: #17345E;
            height: 22px;
            white-space: nowrap;
        }}

        .bar-area {{
            height: {max_height}px;
            width: 44px;
            display: flex;
            align-items: flex-end;
            justify-content: center;
        }}

        .bar {{
            width: 38px;
            border-radius: 7px 7px 0 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.15);
            transition: opacity 0.2s;
        }}

        .bar:hover {{
            opacity: 0.7;
        }}

        .bar-label {{
            margin-top: 9px;
            font-size: 12px;
            font-weight: bold;
            color: #17345E;
            text-align: center;
            width: 70px;
            overflow-wrap: anywhere;
        }}
    </style>
    </head>

    <body>
        <div class="chart-title">{safe_title}</div>

        <div class="scroll">
            <div class="chart">
                {bars_html}
            </div>
        </div>
    </body>
    </html>
    """


# ==================================================
# 탭 구성
# ==================================================
tab1, tab2 = st.tabs([
    "🌍 국가 → MBTI",
    "🧠 MBTI → 국가"
])


# ==================================================
# TAB 1
# 국가별 MBTI 분석
# ==================================================
with tab1:

    st.subheader("🌍 국가별 MBTI 비율")

    countries = sorted(
        df["Country"].dropna().unique().tolist()
    )

    if not countries:
        st.warning("국가 데이터가 없습니다.")
        st.stop()

    selected_country = st.selectbox(
        "국가를 선택하세요 👇",
        countries
    )

    country_row = df[
        df["Country"] == selected_country
    ].iloc[0]

    country_data = pd.DataFrame({
        "MBTI": MBTI_TYPES,
        "비율": [
            country_row[mbti] * 100
            if pd.notna(country_row[mbti])
            else None
            for mbti in MBTI_TYPES
        ]
    })

    country_data = country_data.dropna(
        subset=["비율"]
    )

    country_data = country_data.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    if country_data.empty:
        st.warning("선택한 국가의 MBTI 데이터가 없습니다.")
        st.stop()

    first = country_data.iloc[0]

    st.markdown("### 🏆 이 국가의 1위 MBTI")

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric(
            "🥇 1위 MBTI",
            first["MBTI"]
        )

    with metric2:
        st.metric(
            "📊 비율",
            f'{first["비율"]:.2f}%'
        )

    st.markdown("### 🥇 TOP 3")

    top3 = st.columns(3)

    medals = ["🥇", "🥈", "🥉"]

    for i in range(min(3, len(country_data))):

        row = country_data.iloc[i]

        with top3[i]:
            st.metric(
                f'{medals[i]} {i + 1}위',
                row["MBTI"],
                f'{row["비율"]:.2f}%'
            )

    st.divider()

    st.markdown("### 📊 국가별 MBTI 막대그래프")

    chart_html = make_bar_chart(
        country_data["MBTI"].tolist(),
        country_data["비율"].tolist(),
        f"{selected_country}의 MBTI 분포",
        330
    )

    components.html(
        chart_html,
        height=500,
        scrolling=True
    )


# ==================================================
# TAB 2
# MBTI별 국가 분석
# ==================================================
with tab2:

    st.subheader("🧠 MBTI별 국가 순위")

    selected_mbti = st.selectbox(
        "MBTI를 선택하세요 👇",
        MBTI_TYPES,
        key="selected_mbti"
    )

    ranking_df = df[
        ["Country", selected_mbti]
    ].copy()

    ranking_df["비율"] = (
        ranking_df[selected_mbti] * 100
    )

    ranking_df = ranking_df[
        ["Country", "비율"]
    ].dropna(subset=["비율"])

    ranking_df = ranking_df.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    if ranking_df.empty:
        st.warning("해당 MBTI의 국가별 데이터가 없습니다.")
        st.stop()

    ranking_df.insert(
        0,
        "순위",
        range(1, len(ranking_df) + 1)
    )

    first_country = ranking_df.iloc[0]

    st.markdown("### 🏆 1위 국가")

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric(
            "🌎 국가",
            first_country["Country"]
        )

    with metric2:
        st.metric(
            "📊 비율",
            f'{first_country["비율"]:.2f}%'
        )

    st.divider()

    st.markdown(
        f"### 📊 {selected_mbti} 국가별 TOP 20"
    )

    top20 = ranking_df.head(20)

    chart_html = make_bar_chart(
        top20["Country"].tolist(),
        top20["비율"].tolist(),
        f"{selected_mbti} 국가별 순위",
        330
    )

    components.html(
        chart_html,
        height=560,
        scrolling=True
    )

    st.caption(
        "💡 그래프는 상위 20개 국가를 보여줍니다. "
        "아래 표에서 전체 국가 순위를 확인할 수 있어요."
    )

    st.markdown("### 🏆 전체 국가 순위")

    display_df = ranking_df.copy()

    display_df["비율"] = display_df["비율"].map(
        lambda x: f"{x:.2f}%"
    )

    display_df.columns = [
        "순위",
        "국가",
        "비율"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=600
    )
