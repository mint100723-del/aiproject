import streamlit as st
import pandas as pd

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="🌎 국가별 MBTI 분석",
    page_icon="🌎",
    layout="wide"
)

# --------------------------------------------------
# CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 17px;
        color: #666666;
        margin-bottom: 25px;
    }

    .info-card {
        background: #f7f8fc;
        border-radius: 18px;
        padding: 22px;
        text-align: center;
        border: 1px solid #eeeeee;
        margin-bottom: 15px;
    }

    .info-title {
        font-size: 16px;
        color: #555555;
        margin-bottom: 8px;
    }

    .info-value {
        font-size: 30px;
        font-weight: 800;
        color: #141f3d;
    }

    .rank-card {
        background: #fff4fa;
        border: 1px solid #ffd1e8;
        border-radius: 18px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }

    .rank-number {
        font-size: 17px;
        color: #666666;
    }

    .rank-country {
        font-size: 28px;
        font-weight: 800;
        color: #141f3d;
        margin: 5px 0;
    }

    .rank-percent {
        font-size: 25px;
        font-weight: 800;
        color: #ff1493;
    }

    .chart-box {
        width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        padding: 25px 10px 10px 10px;
        border-radius: 18px;
        background: #fafafa;
        border: 1px solid #eeeeee;
    }

    .chart {
        display: flex;
        align-items: flex-end;
        gap: 10px;
        height: 420px;
        min-width: max-content;
        padding: 20px 20px 70px 20px;
    }

    .bar-item {
        width: 55px;
        height: 330px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        align-items: center;
        position: relative;
        flex-shrink: 0;
    }

    .bar-value {
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 6px;
        color: #333333;
        white-space: nowrap;
    }

    .bar {
        width: 38px;
        min-height: 4px;
        border-radius: 8px 8px 0 0;
        transition: 0.2s;
    }

    .bar:hover {
        transform: scaleX(1.08);
        opacity: 0.85;
    }

    .bar-label {
        position: absolute;
        bottom: -60px;
        width: 90px;
        text-align: center;
        font-size: 11px;
        color: #333333;
        transform: rotate(-45deg);
        transform-origin: center;
        white-space: nowrap;
    }

    .rank-badge {
        position: absolute;
        top: -22px;
        font-size: 10px;
        color: #777777;
        white-space: nowrap;
    }

    .description-box {
        background: #f4f6fb;
        border-radius: 15px;
        padding: 16px 20px;
        margin-top: 15px;
        color: #555555;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# 제목
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🌎 국가별 MBTI 분석</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">나라별 MBTI 분포와 특정 MBTI의 국가별 순위를 한눈에 확인해보세요!</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# CSV 불러오기
# --------------------------------------------------

@st.cache_data
def load_data():

    # 현재 Streamlit 앱의 기본 위치에서 CSV 찾기
    file_path = "countriesMBTI_16types.csv"

    df = pd.read_csv(file_path)

    # 앞뒤 공백 제거
    df.columns = df.columns.str.strip()

    # 국가명 문자열 처리
    if "Country" in df.columns:
        df["Country"] = df["Country"].astype(str).str.strip()

    # MBTI 데이터 숫자로 변환
    for column in df.columns:
        if column != "Country":
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


# --------------------------------------------------
# 데이터 불러오기 오류 처리
# --------------------------------------------------

try:
    df = load_data()

except FileNotFoundError:

    st.error(
        "❌ countriesMBTI_16types.csv 파일을 찾을 수 없어요."
    )

    st.info(
        "📁 CSV 파일을 app.py와 같은 프로젝트 폴더에 넣어주세요."
    )

    st.stop()

except Exception as e:

    st.error("❌ CSV 파일을 읽는 중 문제가 발생했어요.")

    st.code(str(e))

    st.stop()


# --------------------------------------------------
# MBTI 목록
# --------------------------------------------------

mbti_types = [
    "INFJ",
    "ISFJ",
    "INTP",
    "ISFP",
    "ENTP",
    "INFP",
    "ENTJ",
    "ISTP",
    "INTJ",
    "ESFP",
    "ESTJ",
    "ENFP",
    "ESTP",
    "ISTJ",
    "ENFJ",
    "ESFJ"
]

# 실제 CSV에 존재하는 MBTI만 사용
available_mbti = [
    mbti for mbti in mbti_types
    if mbti in df.columns
]

# 국가명 확인
if "Country" not in df.columns:

    st.error(
        "❌ CSV에 Country 열이 없습니다."
    )

    st.stop()

# 국가 목록
countries = (
    df["Country"]
    .dropna()
    .astype(str)
    .tolist()
)

if len(countries) == 0:

    st.error(
        "❌ 국가 데이터가 없습니다."
    )

    st.stop()


# --------------------------------------------------
# 탭
# --------------------------------------------------

tab1, tab2 = st.tabs(
    [
        "🌍 국가 → MBTI",
        "🧠 MBTI → 국가"
    ]
)


# ==================================================
# TAB 1
# 국가를 선택하면 MBTI 순위
# ==================================================

with tab1:

    st.subheader("🌍 국가별 MBTI 분석")

    selected_country = st.selectbox(
        "국가를 선택하세요 👇",
        countries,
        key="country_select"
    )

    # 선택 국가 데이터
    selected_data = df[
        df["Country"] == selected_country
    ]

    if selected_data.empty:

        st.warning(
            "⚠️ 선택한 국가의 데이터를 찾을 수 없습니다."
        )

    else:

        country_row = selected_data.iloc[0]

        # MBTI 데이터 만들기
        country_mbti = {}

        for mbti in available_mbti:

            value = country_row[mbti]

            if pd.notna(value):

                country_mbti[mbti] = float(value)

        # 내림차순 정렬
        country_sorted = sorted(
            country_mbti.items(),
            key=lambda x: x[1],
            reverse=True
        )

        if len(country_sorted) == 0:

            st.warning(
                "⚠️ 이 국가의 MBTI 데이터가 없습니다."
            )

        else:

            # ------------------------------------------
            # 1위 정보
            # ------------------------------------------

            first_mbti = country_sorted[0][0]
            first_value = country_sorted[0][1]

            st.markdown(
                f"""
                <div class="rank-card">

                    <div class="rank-number">
                        🏆 {selected_country}의 1위 MBTI
                    </div>

                    <div class="rank-country">
                        🧠 {first_mbti}
                    </div>

                    <div class="rank-percent">
                        {first_value * 100:.2f}%
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            # ------------------------------------------
            # TOP 3
            # ------------------------------------------

            col1, col2, col3 = st.columns(3)

            top3 = country_sorted[:3]

            for i, col in enumerate(
                [col1, col2, col3]
            ):

                if i < len(top3):

                    mbti_name = top3[i][0]
                    mbti_value = top3[i][1]

                    col.markdown(
                        f"""
                        <div class="info-card">

                            <div class="info-title">
                                {i + 1}위
                            </div>

                            <div class="info-value">
                                {mbti_name}
                            </div>

                            <div style="margin-top:5px;">
                                {mbti_value * 100:.2f}%
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # ------------------------------------------
            # 그래프 제목
            # ------------------------------------------

            st.markdown(
                f"### 📊 {selected_country}의 MBTI 분포"
            )

            st.caption(
                "높은 비율의 MBTI부터 순서대로 표시됩니다."
            )

            # ------------------------------------------
            # 세로 막대 그래프
            # ------------------------------------------

            max_value = max(
                value for _, value in country_sorted
            )

            chart_html = """
            <div class="chart-box">
                <div class="chart">
            """

            total = len(country_sorted)

            for rank, (mbti, value) in enumerate(
                country_sorted,
                start=1
            ):

                # 막대 높이
                if max_value > 0:
                    height = (
                        value / max_value
                    ) * 300
                else:
                    height = 4

                if height < 4:
                    height = 4

                # 1위 핫핑크
                if rank == 1:

                    background = "#FF1493"

                else:

                    # 네이비 그라데이션
                    if total > 1:

                        ratio = (
                            (rank - 2)
                            / (total - 2)
                            if total > 2
                            else 0
                        )

                    else:

                        ratio = 0

                    # 진한 네이비 → 연한 네이비
                    r = int(
                        20 + (130 - 20) * ratio
                    )

                    g = int(
                        43 + (150 - 43) * ratio
                    )

                    b = int(
                        90 + (200 - 90) * ratio
                    )

                    background = (
                        f"rgb({r},{g},{b})"
                    )

                chart_html += f"""
                    <div class="bar-item">

                        <div class="rank-badge">
                            {rank}위
                        </div>

                        <div class="bar-value">
                            {value * 100:.1f}%
                        </div>

                        <div
                            class="bar"
                            style="
                                height:{height:.1f}px;
                                background:{background};
                            "
                            title="{rank}위 {mbti} : {value * 100:.2f}%"
                        >
                        </div>

                        <div class="bar-label">
                            {mbti}
                        </div>

                    </div>
                """

            chart_html += """
                </div>
            </div>
            """

            # ★ 중요 ★
            # 코드블록(```)을 사용하지 않고
            # HTML을 바로 렌더링
            st.markdown(
                chart_html,
                unsafe_allow_html=True
            )


# ==================================================
# TAB 2
# MBTI를 선택하면 국가 순위
# ==================================================

with tab2:

    st.subheader("🧠 MBTI별 국가 순위")

    selected_mbti = st.selectbox(
        "MBTI를 선택하세요 👇",
        available_mbti,
        key="mbti_select"
    )

    # ----------------------------------------------
    # 국가별 데이터
    # ----------------------------------------------

    ranking_df = df[
        ["Country", selected_mbti]
    ].copy()

    ranking_df[selected_mbti] = pd.to_numeric(
        ranking_df[selected_mbti],
        errors="coerce"
    )

    # 결측치 제거
    ranking_df = ranking_df.dropna(
        subset=[selected_mbti]
    )

    # 내림차순 정렬
    ranking_df = ranking_df.sort_values(
        by=selected_mbti,
        ascending=False
    ).reset_index(drop=True)

    # ----------------------------------------------
    # 데이터가 없는 경우
    # ----------------------------------------------

    if ranking_df.empty:

        st.warning(
            "⚠️ 해당 MBTI의 국가 데이터가 없습니다."
        )

    else:

        # ------------------------------------------
        # 1위 국가
        # ------------------------------------------

        first_country = ranking_df.iloc[0]["Country"]
        first_value = ranking_df.iloc[0][selected_mbti]

        st.markdown(
            f"""
            <div class="rank-card">

                <div class="rank-number">
                    🏆 {selected_mbti} 비율 1위 국가
                </div>

                <div class="rank-country">
                    {first_country}
                </div>

                <div class="rank-percent">
                    {first_value * 100:.2f}%
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        # ------------------------------------------
        # 전체 국가 수
        # ------------------------------------------

        st.markdown(
            f"""
            <div class="info-card">

                <div class="info-title">
                    🌎 분석 국가 수
                </div>

                <div class="info-value">
                    {len(ranking_df)}개국
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        # ------------------------------------------
        # 그래프
        # ------------------------------------------

        st.markdown(
            f"### 🏆 {selected_mbti} 국가별 순위"
        )

        st.caption(
            f"{selected_mbti} 비율이 높은 국가부터 1위 → {len(ranking_df)}위 순서입니다."
        )

        # 최대값
        max_country_value = ranking_df[
            selected_mbti
        ].max()

        # ------------------------------------------
        # 가로 스크롤 가능한 그래프
        # ------------------------------------------

        chart_html = """
        <div class="chart-box">
            <div class="chart">
        """

        total_countries = len(ranking_df)

        for index, row in ranking_df.iterrows():

            rank = index + 1

            country = str(row["Country"])

            value = float(
                row[selected_mbti]
            )

            # 막대 높이
            if max_country_value > 0:

                height = (
                    value / max_country_value
                ) * 300

            else:

                height = 4

            if height < 4:
                height = 4

            # 1위 핫핑크
            if rank == 1:

                background = "#FF1493"

            else:

                # 네이비 그라데이션
                if total_countries > 2:

                    ratio = (
                        (rank - 2)
                        / (total_countries - 2)
                    )

                else:

                    ratio = 0

                r = int(
                    20 + (130 - 20) * ratio
                )

                g = int(
                    43 + (150 - 43) * ratio
                )

                b = int(
                    90 + (200 - 90) * ratio
                )

                background = (
                    f"rgb({r},{g},{b})"
                )

            chart_html += f"""
                <div class="bar-item">

                    <div class="rank-badge">
                        {rank}위
                    </div>

                    <div class="bar-value">
                        {value * 100:.1f}%
                    </div>

                    <div
                        class="bar"
                        style="
                            height:{height:.1f}px;
                            background:{background};
                        "
                        title="{rank}위 {country} : {value * 100:.2f}%"
                    >
                    </div>

                    <div class="bar-label">
                        {country}
                    </div>

                </div>
            """

        chart_html += """
            </div>
        </div>
        """

        # ★ HTML을 코드블록으로 감싸지 않음
        st.markdown(
            chart_html,
            unsafe_allow_html=True
        )

        # ------------------------------------------
        # TOP 10 표
        # ------------------------------------------

        st.markdown(
            f"### 📋 {selected_mbti} TOP 10"
        )

        top10 = ranking_df.head(10).copy()

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


# --------------------------------------------------
# 하단 안내
# --------------------------------------------------

st.markdown("---")

st.info(
    "💡 참고: 이 자료의 MBTI 비율은 제공된 데이터셋을 기준으로 한 것이며, "
    "각 국가의 모든 사람을 대표한다고 볼 수는 없습니다."
)
