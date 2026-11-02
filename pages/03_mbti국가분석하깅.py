import streamlit as st
import pandas as pd


# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="🌎 국가별 MBTI 분석",
    page_icon="🌎",
    layout="wide"
)


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
MBTI_TYPES = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("🌎 국가별 MBTI 분석")
st.caption("나라별 MBTI 비율을 한눈에 비교해보세요! 🧠✨")


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")

    # 컬럼명 정리
    df.columns = df.columns.str.strip()

    # 국가명 정리
    df["Country"] = df["Country"].astype(str).str.strip()

    # MBTI 값 숫자로 변환
    for mbti in MBTI_TYPES:
        df[mbti] = pd.to_numeric(df[mbti], errors="coerce")

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "❌ countriesMBTI_16types.csv 파일을 찾을 수 없습니다.\n\n"
        "CSV 파일이 Streamlit 프로젝트의 최상위 폴더에 있는지 확인해주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"❌ 데이터를 불러오는 중 문제가 발생했습니다: {e}")
    st.stop()


# --------------------------------------------------
# 데이터 확인
# --------------------------------------------------
if "Country" not in df.columns:
    st.error("❌ CSV 파일에 Country 컬럼이 없습니다.")
    st.stop()

missing_columns = [
    mbti for mbti in MBTI_TYPES
    if mbti not in df.columns
]

if missing_columns:
    st.error(
        f"❌ 다음 MBTI 컬럼이 CSV에 없습니다: {', '.join(missing_columns)}"
    )
    st.stop()


# --------------------------------------------------
# 탭
# --------------------------------------------------
tab1, tab2 = st.tabs([
    "🌍 국가 → MBTI",
    "🧠 MBTI → 국가"
])


# ==================================================
# TAB 1
# 국가를 선택하면 MBTI 비율 보여주기
# ==================================================
with tab1:

    st.subheader("🌍 국가별 MBTI 비율")

    countries = sorted(df["Country"].dropna().unique().tolist())

    if not countries:
        st.warning("국가 데이터가 없습니다.")
        st.stop()

    selected_country = st.selectbox(
        "국가를 선택하세요 👇",
        countries
    )

    country_data = df[
        df["Country"] == selected_country
    ].iloc[0]

    # MBTI별 비율 데이터
    mbti_values = []

    for mbti in MBTI_TYPES:
        value = country_data[mbti]

        if pd.notna(value):
            mbti_values.append({
                "MBTI": mbti,
                "비율": float(value) * 100
            })

    chart_df = pd.DataFrame(mbti_values)

    # 높은 순으로 정렬
    chart_df = chart_df.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    # --------------------------------------------------
    # 1위 MBTI
    # --------------------------------------------------
    first_mbti = chart_df.iloc[0]["MBTI"]
    first_value = chart_df.iloc[0]["비율"]

    st.success(
        f"🏆 **{selected_country}**에서 가장 높은 MBTI는 "
        f"**{first_mbti} ({first_value:.2f}%)** 입니다!"
    )

    # --------------------------------------------------
    # TOP 3
    # --------------------------------------------------
    st.markdown("### 🥇 TOP 3")

    col1, col2, col3 = st.columns(3)

    top3 = chart_df.head(3)

    for i, (_, row) in enumerate(top3.iterrows()):

        if i == 0:
            col = col1
            emoji = "🥇"
        elif i == 1:
            col = col2
            emoji = "🥈"
        else:
            col = col3
            emoji = "🥉"

        with col:
            st.metric(
                f"{emoji} {row['MBTI']}",
                f"{row['비율']:.2f}%"
            )

    st.markdown("---")

    # --------------------------------------------------
    # 세로 막대그래프
    # --------------------------------------------------
    st.markdown(
        f"### 📊 {selected_country}의 MBTI 분포"
    )

    st.bar_chart(
        chart_df.set_index("MBTI"),
        y="비율",
        height=500
    )

    st.caption(
        "※ 막대가 높을수록 해당 국가에서 그 MBTI의 비율이 높습니다."
    )


# ==================================================
# TAB 2
# MBTI를 선택하면 국가별 순위 보여주기
# ==================================================
with tab2:

    st.subheader("🧠 MBTI별 국가 순위")

    selected_mbti = st.selectbox(
        "MBTI를 선택하세요 👇",
        MBTI_TYPES
    )

    # 선택한 MBTI 기준 국가별 정렬
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

    ranking_df = ranking_df.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    # 순위
    ranking_df.insert(
        0,
        "순위",
        range(1, len(ranking_df) + 1)
    )

    # --------------------------------------------------
    # 1위 국가
    # --------------------------------------------------
    first_country = ranking_df.iloc[0]["Country"]
    first_value = ranking_df.iloc[0]["비율"]

    st.success(
        f"🏆 **{selected_mbti} 비율이 가장 높은 국가는 "
        f"{first_country} ({first_value:.2f}%)** 입니다!"
    )

    # --------------------------------------------------
    # 기본 정보
    # --------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "🌎 조사된 국가 수",
            f"{len(ranking_df)}개"
        )

    with col2:
        st.metric(
            f"🧠 {selected_mbti} 최고 비율",
            f"{first_value:.2f}%"
        )

    st.markdown("---")

    # --------------------------------------------------
    # 국가별 막대그래프
    # --------------------------------------------------
    st.markdown(
        f"### 📊 {selected_mbti} 국가별 순위"
    )

    # Streamlit 기본 bar chart
    # 국가가 많기 때문에 상위 20개만 그래프로 표시
    top20 = ranking_df.head(20).copy()

    chart_country_df = top20[
        ["Country", "비율"]
    ].set_index("Country")

    st.bar_chart(
        chart_country_df,
        y="비율",
        height=600
    )

    st.caption(
        "※ 국가가 많아 그래프는 상위 20개 국가를 표시합니다."
    )

    # --------------------------------------------------
    # 전체 순위표
    # --------------------------------------------------
    st.markdown(
        f"### 🏆 {selected_mbti} 전체 국가 순위"
    )

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
