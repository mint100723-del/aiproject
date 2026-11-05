
from pathlib import Path
import io
import math
import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="제주 연령별 인구 분석",
    page_icon="🌸",
    layout="wide"
)

PINK = "#FF1493"

# pages 폴더의 상위 폴더 경로
PROJECT_DIR = Path(__file__).resolve().parents[1]


# ==========================================
# 2. CSV 파일 읽기 및 한글 인코딩 처리
# ==========================================

@st.cache_data(show_spinner=False)
def load_csv(file_bytes):
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]

    for encoding in encodings:
        try:
            data = pd.read_csv(
                io.BytesIO(file_bytes),
                encoding=encoding,
                dtype=str
            )
            return data, encoding

        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인해주세요.")


def get_csv_bytes(uploaded_file):

    # 직접 업로드한 파일이 있으면 우선 사용
    if uploaded_file is not None:
        return uploaded_file.getvalue(), uploaded_file.name

    # pages 폴더의 상위 폴더에서 CSV 검색
    candidates = [
        PROJECT_DIR / "population.csv",
        PROJECT_DIR / "data" / "population.csv"
    ]

    for path in candidates:
        if path.is_file():
            return path.read_bytes(), path.name

    return None, None


# ==========================================
# 3. 화면 제목
# ==========================================

st.title("🌸 제주특별자치도 연령별 인구 분석")

st.write(
    "행정구역, 성별, 연도를 선택하면 "
    "연령대별 인구수를 핫핑크 꺾은선 그래프로 확인할 수 있어요!"
)

uploaded_file = st.file_uploader(
    "📂 population.csv 업로드 (선택사항)",
    type=["csv"]
)


# ==========================================
# 4. 데이터 불러오기
# ==========================================

try:
    file_bytes, file_name = get_csv_bytes(uploaded_file)

    if file_bytes is None:
        st.error(
            "population.csv 파일을 찾을 수 없습니다. "
            "프로젝트 상위 폴더에 넣어주세요."
        )
        st.stop()

    df, used_encoding = load_csv(file_bytes)

except Exception as e:
    st.error(f"파일 읽기 오류: {e}")
    st.stop()


# ==========================================
# 5. 데이터 전처리
# ==========================================

df.columns = df.columns.astype(str).str.strip()

if "행정구역" not in df.columns:
    st.error("'행정구역' 열을 찾을 수 없습니다.")
    st.stop()

df["행정구역"] = (
    df["행정구역"]
    .fillna("")
    .astype(str)
    .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)
    .str.strip()
)

areas = [
    area for area in df["행정구역"].drop_duplicates()
    if area
]

if not areas:
    st.error("행정구역 데이터가 없습니다.")
    st.stop()


# ==========================================
# 6. 연도 자동 추출
# ==========================================

year_pattern = re.compile(r"^(20\d{2})년_")

years = sorted({
    int(match.group(1))
    for col in df.columns
    if (match := year_pattern.match(col))
})

if not years:
    st.error("연도별 데이터 열을 찾지 못했습니다.")
    st.stop()


# ==========================================
# 7. 사이드바 선택
# ==========================================

st.sidebar.header("📊 분석 조건 선택")

selected_area = st.sidebar.selectbox(
    "행정구역 선택",
    areas
)

selected_gender = st.sidebar.selectbox(
    "성별 선택",
    ["전체", "남성", "여성"]
)

selected_year = st.sidebar.selectbox(
    "연도 선택",
    years,
    index=len(years) - 1
)

gender_prefix = {
    "전체": "",
    "남성": "남_",
    "여성": "여_"
}[selected_gender]


# ==========================================
# 8. 연령별 인구 데이터 추출
# ==========================================

age_labels = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]

selected_rows = df.loc[
    df["행정구역"] == selected_area
]

if selected_rows.empty:
    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

selected_row = selected_rows.iloc[0]

chart_data = []
missing_ages = []

for age in age_labels:

    column_name = (
        f"{selected_year}년_"
        f"{gender_prefix}거주자_{age}"
    )

    if column_name not in df.columns:
        missing_ages.append(age)
        continue

    raw_value = selected_row[column_name]

    if pd.isna(raw_value) or str(raw_value).strip() == "":
        missing_ages.append(age)
        continue

    value = pd.to_numeric(
        str(raw_value).replace(",", "").strip(),
        errors="coerce"
    )

    if pd.isna(value):
        missing_ages.append(age)
        continue

    chart_data.append({
        "연령대": age,
        "인구수": int(value)
    })

chart_df = pd.DataFrame(chart_data)

if chart_df.empty:
    st.error(
        "선택한 조건에 해당하는 연령별 인구 데이터가 없습니다."
    )
    st.stop()

if missing_ages:
    st.warning(
        "다음 연령대는 데이터가 없거나 숫자로 변환되지 않았습니다: "
        + ", ".join(missing_ages)
    )


# ==========================================
# 9. 주요 통계
# ==========================================

total_population = int(chart_df["인구수"].sum())

max_index = chart_df["인구수"].idxmax()

largest_age = chart_df.loc[max_index, "연령대"]

largest_population = int(
    chart_df.loc[max_index, "인구수"]
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "전체 연령 인구 합계",
    f"{total_population:,}명"
)

col2.metric(
    "인구가 가장 많은 연령대",
    largest_age
)

col3.metric(
    "해당 연령대 인구",
    f"{largest_population:,}명"
)


# ==========================================
# 10. 핫핑크 꺾은선 그래프
# ==========================================

max_population = int(chart_df["인구수"].max())

y_axis_max = max(
    100000,
    math.ceil(max_population / 100000) * 100000
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=chart_df["연령대"],
        y=chart_df["인구수"],

        mode="lines+markers",

        name="인구수",

        line={
            "color": PINK,
            "width": 4
        },

        marker={
            "color": PINK,
            "size": 9,
            "line": {
                "color": "#FFFFFF",
                "width": 1
            }
        },

        hovertemplate=(
            "나이: %{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)

fig.update_layout(

    title={
        "text": (
            f"{selected_area} · {selected_year}년 · "
            f"{selected_gender} 연령별 인구"
        ),
        "x": 0.02,
        "xanchor": "left"
    },

    xaxis={
        "title": "나이",
        "type": "category",
        "categoryorder": "array",
        "categoryarray": age_labels,
        "showgrid": True,
        "gridcolor": "#E6E6E6",
        "gridwidth": 1,
        "tickangle": 0
    },

    yaxis={
        "title": "인구수 (명)",
        "range": [0, y_axis_max],
        "tick0": 0,
        "dtick": 100000,
        "tickformat": ",d",
        "showgrid": True,
        "gridcolor": "#D8D8D8",
        "gridwidth": 1,
        "zeroline": True,
        "zerolinecolor": "#999999"
    },

    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",

    hovermode="x unified",

    height=570,

    margin={
        "l": 80,
        "r": 30,
        "t": 85,
        "b": 75
    },

    font={
        "family": "Arial, sans-serif",
        "size": 13,
        "color": "#333333"
    },

    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displaylogo": False,
        "responsive": True
    }
)

st.caption(
    "가로축: 10살 단위 / 세로축: 100,000명 단위 / "
    "그래프 색상: 핫핑크 #FF1493"
)


# ==========================================
# 11. 데이터 표 확인
# ==========================================

with st.expander("📋 그래프에 사용된 데이터 확인"):

    st.dataframe(
        chart_df,
        use_container_width=True,
        hide_index=True
    )

    csv_bytes = chart_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 분석 데이터 다운로드",
        data=csv_bytes,
        file_name="jeju_age_population.csv",
        mime="text/csv"
    )


# ==========================================
# 12. 데이터 정보
# ==========================================

with st.expander("ℹ️ 데이터 파일 정보"):

    st.write(f"파일 이름: {file_name}")
    st.write(f"감지된 인코딩: {used_encoding}")
    st.write(f"행정구역 수: {len(areas)}개")
    st.write(f"분석 연도: {years}")
    st.write(
        f"원본 결측치: {int(df.isna().sum().sum()):,}개"
    )

st.success("🌸 인구 분석 그래프 생성 완료!")
