import streamlit as st
import pandas as pd
import streamlit.components.v1 as components


# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="🌎 국가별 MBTI 분석",
    page_icon="🌎",
    layout="wide"
)


# =========================================================
# MBTI 목록
# =========================================================
MBTI_TYPES = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]


# =========================================================
# 전체 기본 스타일
# =========================================================
st.markdown("""
<style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }

    .main-subtitle {
        text-align: center;
        color: #666;
        font-size: 17px;
        margin-bottom: 30px;
    }

    .first-card {
        background: linear-gradient(135deg, #fff0f7, #ffe1ef);
        border-radius: 18px;
        padding: 20px;
        text-align: center;
        border: 2px solid #ff1493;
        margin: 15px 0 25px 0;
    }

    .first-title {
        font-size: 18px;
        color: #555;
    }

    .first-name {
        font-size: 32px;
        font-weight: 800;
        color: #ff1493;
        margin: 5px 0;
    }

    .first-value {
        font-size: 22px;
        font-weight: 700;
        color: #172554;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 제목
# =========================================================
st.markdown(
    '<div class="main-title">🌎 국가별 MBTI 분석</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    '나라별 MBTI 비율을 재미있게 비교해보세요! 🧠✨'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 데이터 불러오기
# =========================================================
@st.cache_data
def load_data():

    df = pd.read_csv("countriesMBTI_16types.csv")

    df.columns = df.columns.str.strip()

    df["Country"] = (
        df["Country"]
        .astype(str)
        .str.strip()
    )

    for mbti in MBTI_TYPES:
        df[mbti] = pd.to_numeric(
            df[mbti],
            errors="coerce"
        )

    return df


try:

    df = load_data()

except FileNotFoundError:

    st.error(
        "❌ countriesMBTI_16types.csv 파일을 찾을 수 없습니다."
    )

    st.info(
        "CSV 파일을 app.py와 같은 최상위 폴더에 넣어주세요."
    )

    st.stop()

except Exception as e:

    st.error(
        f"❌ CSV 파일을 읽는 중 오류가 발생했습니다: {e}"
    )

    st.stop()


# =========================================================
# 데이터 검증
# =========================================================
if "Country" not in df.columns:

    st.error(
        "❌ CSV 파일에 Country 컬럼이 없습니다."
    )

    st.stop()


missing = [
    mbti
    for mbti in MBTI_TYPES
    if mbti not in df.columns
]

if missing:

    st.error(
        "❌ 다음 MBTI 컬럼이 없습니다: "
        + ", ".join(missing)
    )

    st.stop()


# =========================================================
# 막대그래프 HTML 생성 함수
# =========================================================
def make_bar_chart(
    labels,
    values,
    title="",
    max_height=320
):

    if len(labels) == 0:

        return "<p>표시할 데이터가 없습니다.</p>"


    # 최대값
    max_value = max(values)

    if max_value <= 0:
        max_value = 1


    # 막대 HTML
    bars_html = ""

    total = len(labels)


    for i, (label, value) in enumerate(
        zip(labels, values)
    ):

        # 첫 번째 = 핫핑크
        if i == 0:

            color = "#FF1493"

        else:

            # 네이비 계열 그라데이션
            if total <= 1:
                ratio = 1
            else:
                ratio = i / (total - 1)

            r = int(
                15 + (115 - 15) * ratio
            )

            g = int(
                35 + (140 - 35) * ratio
            )

            b = int(
                80 + (195 - 80) * ratio
            )

            color = f"rgb({r},{g},{b})"


        # 막대 높이
        height = (
            value / max_value
        ) * max_height


        # 너무 작은 막대도 보이도록
        if height < 4 and value > 0:
            height = 4


        bars_html += f"""
        <div class="bar-item">

            <div class="bar-value">
                {value:.2f}%
            </div>

            <div class="bar-area">

                <div
                    class="bar"
                    style="
                        height:{height}px;
                        background:{color};
                    "
                ></div>

            </div>

            <div class="bar-label">
                {label}
            </div>

        </div>
        """


    html = f"""
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
            font-family:
                Arial,
                "Noto Sans KR",
                sans-serif;
            background: transparent;
        }}

        .chart-title {{
            text-align: center;
            font-size: 20px;
            font-weight: 700;
            color: #172554;
            margin-bottom: 20px;
        }}

        .scroll {{
            width: 100%;
            overflow-x: auto;
            overflow-y: hidden;
            padding: 10px 5px 20px 5px;
        }}

        .chart {{
            display: flex;
            align-items: flex-end;
            gap: 12px;
            min-width: max-content;
            height: {max_height + 100}px;
            padding: 10px 15px 0 15px;
            border-bottom: 2px solid #172554;
        }}

        .bar-item {{
            width: 58px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
        }}

        .bar-value {{
            font-size: 12px;
            font-weight: 700;
            color: #172554;
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
            min-height: 3px;
            border-radius: 7px 7px 0 0;
            transition: all 0.2s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.12);
        }}

        .bar:hover {{
            opacity: 0.75;
            transform: scaleX(1.08);
        }}

        .bar-label {{
            margin-top: 9px;
            font-size: 12px;
            font-weight: 700;
            color: #172554;
            text-align: center;
            width: 70px;
            word-break: break-word;
        }}

    </style>

    </head>

    <body>

        <div class="chart-title">
            {title}
        </div>

        <div class="scroll">

            <div class="chart">

                {bars_html}

            </div>

        </div>

    </body>

    </html>
    """

    return html


# =========================================================
# 탭
# =========================================================
tab1, tab2 = st.tabs(
    [
        "🌍 국가 → MBTI",
        "🧠 MBTI → 국가"
    ]
)


# =========================================================
# TAB 1
# 국가 선택 → MBTI 비율
# =========================================================
with tab1:

    st.subheader(
        "🌍 국가별 MBTI 비율"
    )


    countries = sorted(
        df["Country"]
        .dropna()
        .unique()
        .tolist()
    )


    selected_country = st.selectbox(
        "국가를 선택하세요 👇",
        countries
    )


    # 선택 국가 데이터
    country_row = df[
        df["Country"] == selected_country
    ].iloc[0]


    data = []


    for mbti in MBTI_TYPES:

        value = country_row[mbti]

        if pd.notna(value):

            data.append(
                {
                    "MBTI": mbti,
                    "비율": float(value) * 100
                }
            )


    country_chart_df = pd.DataFrame(data)


    country_chart_df = (
        country_chart_df
        .sort_values(
            "비율",
            ascending=False
        )
        .reset_index(drop=True)
    )


    # -----------------------------------------------------
    # 1위
    # -----------------------------------------------------
    first_mbti = (
        country_chart_df.iloc[0]["MBTI"]
    )

    first_value = (
        country_chart_df.iloc[0]["비율"]
    )


    st.markdown(
        f"""
        <div class="first-card">

            <div class="first-title">
                🏆 {selected_country}에서 가장 높은 MBTI
            </div>

            <div class="first-name">
                {first_mbti}
            </div>

            <div class="first-value">
                {first_value:.2f}%
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # TOP 3
    # -----------------------------------------------------
    st.markdown("### 🏆 TOP 3")


    top1, top2, top3 = st.columns(3)


    top3_data = country_chart_df.head(3)


    if len(top3_data) >= 1:

        row = top3_data.iloc[0]

        with top1:

            st.metric(
                "🥇 1위",
                row["MBTI"],
                f'{row["비율"]:.2f}%'
            )


    if len(top3_data) >= 2:

        row = top3_data.iloc[1]

        with top2:

            st.metric(
                "🥈 2위",
                row["MBTI"],
                f'{row["비율"]:.2f}%'
            )


    if len(top3_data) >= 3:

        row = top3_data.iloc[2]

        with top3:

            st.metric(
                "🥉 3위",
                row["MBTI"],
                f'{row["비율"]:.2f}%'
            )


    st.markdown("---")


    # -----------------------------------------------------
    # MBTI 막대그래프
    # -----------------------------------------------------
    labels = (
        country_chart_df["MBTI"]
        .tolist()
    )

    values = (
        country_chart_df["비율"]
        .tolist()
    )


    chart_html = make_bar_chart(
        labels,
        values,
        title=f"📊 {selected_country}의 MBTI 비율",
        max_height=330
    )


    components.html(
        chart_html,
        height=500,
        scrolling=True
    )


# =========================================================
# TAB 2
# MBTI 선택 → 국가 순위
# =========================================================
with tab2:

    st.subheader(
        "🧠 MBTI별 국가 순위"
    )


    selected_mbti = st.selectbox(
        "MBTI를 선택하세요 👇",
        MBTI_TYPES
    )


    ranking_df = df[
        ["Country", selected_mbti]
    ].copy()


    ranking_df["비율"] = (
        ranking_df[selected_mbti] * 100
    )


    ranking_df = ranking_df[
        ["Country", "비율"]
    ]


    ranking_df = ranking_df.dropna(
        subset=["비율"]
    )


    ranking_df = (
        ranking_df
        .sort_values(
            "비율",
            ascending=False
        )
        .reset_index(drop=True)
    )


    ranking_df.insert(
        0,
        "순위",
        range(
            1,
            len(ranking_df) + 1
        )
    )


    # -----------------------------------------------------
    # 1위 국가
    # -----------------------------------------------------
    first_country = (
        ranking_df.iloc[0]["Country"]
    )

    first_value = (
        ranking_df.iloc[0]["비율"]
    )


    st.markdown(
        f"""
        <div class="first-card">

            <div class="first-title">
                🏆 {selected_mbti} 비율이 가장 높은 국가
            </div>

            <div class="first-name">
                {first_country}
            </div>

            <div class="first-value">
                {first_value:.2f}%
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # 기본 정보
    # -----------------------------------------------------
    info1, info2 = st.columns(2)


    with info1:

        st.metric(
            "🌎 조사 국가 수",
            f"{len(ranking_df)}개"
        )


    with info2:

        st.metric(
            f"🧠 {selected_mbti} 최고 비율",
            f"{first_value:.2f}%"
        )


    st.markdown("---")


    # -----------------------------------------------------
    # 상위 20개 국가 그래프
    # -----------------------------------------------------
    top20 = ranking_df.head(20)


    labels = (
        top20["Country"]
        .tolist()
    )

    values = (
        top20["비율"]
        .tolist()
    )


    chart_html = make_bar_chart(
        labels,
        values,
        title=f"📊 {selected_mbti} 국가별 TOP 20",
        max_height=330
    )


    components.html(
        chart_html,
        height=560,
        scrolling=True
    )


    st.caption(
        "💡 그래프는 상위 20개 국가를 보여주며, "
        "아래 표에서 전체 국가 순위를 확인할 수 있어요."
    )


    # -----------------------------------------------------
    # 전체 순위표
    # -----------------------------------------------------
    st.markdown(
        f"### 🏆 {selected_mbti} 전체 국가 순위"
    )


    display_df = ranking_df.copy()


    display_df["비율"] = (
        display_df["비율"]
        .map(
            lambda x: f"{x:.2f}%"
        )
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
