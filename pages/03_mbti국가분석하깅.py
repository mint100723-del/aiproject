import streamlit as st
import pandas as pd

# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="🌎 국가별 MBTI 분석",
    page_icon="🌎",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 5px;
}

.sub-title {
    text-align: center;
    color: #777777;
    font-size: 18px;
    margin-bottom: 30px;
}

.section-title {
    font-size: 25px;
    font-weight: 800;
    margin-top: 25px;
    margin-bottom: 15px;
}

.info-box {
    background: linear-gradient(135deg, #fff0f8, #f3f6ff);
    border-radius: 20px;
    padding: 25px;
    text-align: center;
    margin: 20px 0 30px 0;
}

.country-name {
    font-size: 22px;
    font-weight: 700;
}

.top-mbti {
    font-size: 42px;
    font-weight: 900;
    color: #ff1493;
    margin: 5px 0;
}

.top-percent {
    font-size: 22px;
    font-weight: 700;
}

.chart-area {
    margin-top: 20px;
    overflow-x: auto;
}

.vertical-chart {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    height: 420px;
    padding: 20px 10px 0 10px;
    border-bottom: 2px solid #d9dce3;
    min-width: 850px;
}

.bar-item {
    flex: 1;
    min-width: 45px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
}

.bar-value {
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 5px;
    white-space: nowrap;
}

.vertical-bar {
    width: 100%;
    max-width: 52px;
    min-height: 4px;
    border-radius: 8px 8px 0 0;
}

.bar-label {
    margin-top: 8px;
    font-size: 12px;
    font-weight: 700;
    text-align: center;
}

.rank-label {
    font-size: 10px;
    color: #888888;
    margin-top: 3px;
}

.country-chart {
    display: flex;
    align-items: flex-end;
    gap: 5px;
    height: 460px;
    padding: 20px 10px 0 10px;
    border-bottom: 2px solid #d9dce3;
    min-width: 1500px;
}

.country-bar-item {
    flex: 1;
    min-width: 45px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
}

.country-bar {
    width: 100%;
    max-width: 42px;
    min-height: 3px;
    border-radius: 7px 7px 0 0;
}

.country-label {
    margin-top: 7px;
    font-size: 9px;
    font-weight: 600;
    text-align: center;
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    height: 75px;
    overflow: hidden;
}

.country-value {
    font-size: 9px;
    font-weight: 700;
    margin-bottom: 3px;
    white-space: nowrap;
}

.tip-box {
    background: #f7f8fc;
    border-radius: 14px;
    padding: 15px;
    margin-top: 15px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 데이터 불러오기
# =========================================================
@st.cache_data
def load_data():
    data = pd.read_csv("countriesMBTI_16types.csv")

    # 숫자 데이터 변환
    for column in data.columns[1:]:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    return data


try:
    df = load_data()
except Exception as e:
    st.error(
        "❌ CSV 파일을 불러오지 못했어요. "
        "'countriesMBTI_16types.csv'가 앱과 같은 프로젝트에 있는지 확인해주세요."
    )
    st.stop()


# =========================================================
# MBTI 목록
# =========================================================
mbti_types = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]


# 실제 데이터에 존재하는 MBTI만 사용
mbti_types = [
    mbti for mbti in mbti_types
    if mbti in df.columns
]


# =========================================================
# 제목
# =========================================================
st.markdown(
    '<div class="main-title">🌎 국가별 MBTI 분석</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '국가와 MBTI를 자유롭게 선택해서 세계의 MBTI 비율을 살펴보세요! ✨'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 탭
# =========================================================
tab1, tab2 = st.tabs([
    "🌍 국가 → MBTI",
    "🧠 MBTI → 국가"
])


# =========================================================
# TAB 1
# 국가를 선택하면 MBTI 비율
# =========================================================
with tab1:

    st.markdown(
        '<div class="section-title">🌍 국가를 선택해보세요</div>',
        unsafe_allow_html=True
    )

    selected_country = st.selectbox(
        "분석할 국가",
        df["Country"].tolist(),
        key="country_select"
    )

    # 선택한 국가
    country_row = df[
        df["Country"] == selected_country
    ].iloc[0]

    # MBTI 데이터
    country_mbti = country_row[mbti_types].astype(float)

    # 높은 순서
    country_sorted = country_mbti.sort_values(
        ascending=False
    )

    # 1위
    top_mbti = country_sorted.index[0]
    top_value = country_sorted.iloc[0] * 100

    # -----------------------------------------------------
    # 1위 박스
    # -----------------------------------------------------
    st.markdown(
        f"""
        <div class="info-box">

            <div class="country-name">
                🌍 {selected_country}
            </div>

            <div style="font-size:17px; margin-top:8px;">
                가장 높은 MBTI
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

    # -----------------------------------------------------
    # 세로 막대그래프
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">📊 MBTI 비율</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "높은 비율부터 정렬했습니다. "
        "1위는 핫핑크, 나머지는 남색 계열로 표시됩니다."
    )

    max_value = country_sorted.max()

    chart_html = '<div class="chart-area"><div class="vertical-chart">'

    total = len(country_sorted)

    for rank, (mbti, value) in enumerate(
        country_sorted.items(),
        start=1
    ):

        percent = value * 100

        # 막대 높이
        height = (value / max_value) * 85

        # -------------------------------------------------
        # 색상
        # -------------------------------------------------
        if rank == 1:

            color = "#FF1493"

        else:

            ratio = (rank - 2) / max(total - 2, 1)

            start_r, start_g, start_b = 20, 43, 90
            end_r, end_g, end_b = 175, 195, 225

            r = int(
                start_r +
                (end_r - start_r) * ratio
            )

            g = int(
                start_g +
                (end_g - start_g) * ratio
            )

            b = int(
                start_b +
                (end_b - start_b) * ratio
            )

            color = f"rgb({r},{g},{b})"

        chart_html += f"""
        <div class="bar-item">

            <div class="bar-value">
                {percent:.1f}%
            </div>

            <div
                class="vertical-bar"
                style="
                    height:{height:.1f}%;
                    background:{color};
                ">
            </div>

            <div class="bar-label">
                {mbti}
            </div>

            <div class="rank-label">
                {rank}위
            </div>

        </div>
        """

    chart_html += """
        </div>
        </div>
    """

    st.markdown(
        chart_html,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # TOP 3
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">🏆 TOP 3</div>',
        unsafe_allow_html=True
    )

    top3 = country_sorted.head(3)

    col1, col2, col3 = st.columns(3)

    columns = [col1, col2, col3]
    medals = ["🥇", "🥈", "🥉"]

    for i, (mbti, value) in enumerate(top3.items()):

        with columns[i]:

            st.metric(
                label=f"{medals[i]} {i + 1}위",
                value=mbti,
                delta=f"{value * 100:.2f}%"
            )


# =========================================================
# TAB 2
# MBTI를 선택하면 국가 순위
# =========================================================
with tab2:

    st.markdown(
        '<div class="section-title">🧠 MBTI를 선택해보세요</div>',
        unsafe_allow_html=True
    )

    selected_mbti = st.selectbox(
        "분석할 MBTI",
        mbti_types,
        key="mbti_select"
    )

    # -----------------------------------------------------
    # 선택한 MBTI의 국가별 데이터
    # -----------------------------------------------------
    country_ranking = df[
        ["Country", selected_mbti]
    ].copy()

    country_ranking[selected_mbti] = pd.to_numeric(
        country_ranking[selected_mbti],
        errors="coerce"
    )

    # 결측값 제거
    country_ranking = country_ranking.dropna(
        subset=[selected_mbti]
    )

    # 높은 순서
    country_ranking = country_ranking.sort_values(
        by=selected_mbti,
        ascending=False
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # 1위 국가
    # -----------------------------------------------------
    first_country = country_ranking.iloc[0]["Country"]
    first_value = (
        country_ranking.iloc[0][selected_mbti] * 100
    )

    st.markdown(
        f"""
        <div class="info-box">

            <div class="country-name">
                🧠 {selected_mbti}
            </div>

            <div style="font-size:17px; margin-top:8px;">
                {selected_mbti} 비율이 가장 높은 국가
            </div>

            <div class="top-mbti">
                {first_country}
            </div>

            <div class="top-percent">
                {first_value:.2f}%
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # 국가 세로 막대그래프
    # -----------------------------------------------------
    st.markdown(
        f'<div class="section-title">🏆 {selected_mbti} 국가별 순위</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"{selected_mbti} 비율이 높은 국가부터 1위 → 158위 순서로 표시됩니다."
    )

    max_country_value = country_ranking[
        selected_mbti
    ].max()

    chart_html = '<div class="chart-area"><div class="country-chart">'

    total_countries = len(country_ranking)

    for rank, row in country_ranking.iterrows():

        country = row["Country"]

        value = row[selected_mbti]

        percent = value * 100

        # 막대 높이
        if max_country_value > 0:
            height = (
                value /
                max_country_value
            ) * 85
        else:
            height = 0

        # -------------------------------------------------
        # 색상
        # 1위 = 핫핑크
        # 나머지 = 남색 그라데이션
        # -------------------------------------------------
        if rank == 0:

            color = "#FF1493"

        else:

            ratio = rank / max(
                total_countries - 1,
                1
            )

            start_r, start_g, start_b = 20, 43, 90
            end_r, end_g, end_b = 175, 195, 225

            r = int(
                start_r +
                (end_r - start_r) * ratio
            )

            g = int(
                start_g +
                (end_g - start_g) * ratio
            )

            b = int(
                start_b +
                (end_b - start_b) * ratio
            )

            color = f"rgb({r},{g},{b})"

        chart_html += f"""
        <div
            class="country-bar-item"
            title="{rank + 1}위 {country} : {percent:.2f}%"
        >

            <div class="country-value">
                {percent:.1f}%
            </div>

            <div
                class="country-bar"
                style="
                    height:{height:.1f}%;
                    background:{color};
                ">
            </div>

            <div class="country-label">
                {country}
            </div>

        </div>
        """

    chart_html += """
        </div>
        </div>
    """

    st.markdown(
        chart_html,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # TOP 10 표
    # -----------------------------------------------------
    st.markdown(
        f'<div class="section-title">🥇 {selected_mbti} TOP 10 국가</div>',
        unsafe_allow_html=True
    )

    top10 = country_ranking.head(10).copy()

    top10.insert(
        0,
        "순위",
        range(1, len(top10) + 1)
    )

    top10["비율"] = (
        top10[selected_mbti] * 100
    ).round(2)

    top10 = top10[
        ["순위", "Country", "비율"]
    ]

    top10.columns = [
        "순위",
        "국가",
        "비율 (%)"
    ]

    st.dataframe(
        top10,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 안내
# =========================================================
st.markdown("---")

st.markdown(
    """
    <div class="tip-box">
    💡 <b>데이터 안내</b><br>
    이 앱은 제공된 CSV의 국가별 MBTI 비율을 시각화합니다.
    실제 국가 전체 인구의 MBTI를 대표하는 통계로 해석하기보다는
    제공된 데이터 안에서 국가별·유형별 비율을 비교하는 용도로
    이용해주세요.
    </div>
    """,
    unsafe_allow_html=True
)
