
from pathlib import Path
import io
import math
import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# 1. 페이지 기본 설정
# =========================================================
st.set_page_config(
    page_title="제주 연령별 인구 분석",
    page_icon="🌸",
    layout="wide",
)

PINK = "#FF1493"
NAVY = "#172554"

# pages 폴더의 상위 폴더
PROJECT_DIR = Path(__file__).resolve().parents[1]


# =========================================================
# 2. CSV 파일 읽기
# =========================================================
@st.cache_data(show_spinner=False)
def load_csv(file_bytes: bytes):
    for encoding in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            data = pd.read_csv(
                io.BytesIO(file_bytes),
                encoding=encoding,
                dtype=str,
            )
            return data, encoding
        except UnicodeDecodeError:
            continue

    raise ValueError(
        "CSV 인코딩을 확인할 수 없습니다. UTF-8 또는 CP949 파일을 사용해주세요."
    )


def to_number(value):
    if pd.isna(value) or str(value).strip() == "":
        return None

    number = pd.to_numeric(
        str(value).replace(",", "").strip(),
        errors="coerce",
    )

    if pd.isna(number):
        return None

    return int(number)


def get_age_population(row, year, gender_prefix, age):
    column_name = f"{year}년_{gender_prefix}거주자_{age}"

    if column_name not in row.index:
        return None

    return to_number(row[column_name])


# =========================================================
# 3. 화면 제목 및 CSV 자동 읽기
# =========================================================
st.title("🌸 제주특별자치도 연령별 인구 분석")
st.write(
    "연도와 행정구역을 선택해 남녀 인구를 비교하고, "
    "연령대별 인구가 많은 행정구역도 확인해 보세요!"
)

# 업로드 창 없이 population.csv를 자동으로 읽습니다.
candidates = [
    PROJECT_DIR / "population.csv",
    PROJECT_DIR / "data" / "population.csv",
]

csv_path = next(
    (path for path in candidates if path.is_file()),
    None,
)

if csv_path is None:
    st.error(
        "population.csv 파일을 찾을 수 없습니다. "
        "GitHub 저장소에서 app.py와 같은 최상위 폴더에 "
        "population.csv를 올려주세요."
    )
    st.stop()

try:
    df, used_encoding = load_csv(csv_path.read_bytes())
    file_name = csv_path.name
except Exception as error:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {error}")
    st.stop()


# =========================================================
# 4. 데이터 열과 행정구역 정리
# =========================================================
df.columns = df.columns.astype(str).str.strip()

if "행정구역" not in df.columns:
    st.error("CSV에서 '행정구역' 열을 찾지 못했습니다.")
    st.stop()

df["행정구역"] = (
    df["행정구역"]
    .fillna("")
    .astype(str)
    .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)
    .str.strip()
)

areas = [
    area
    for area in df["행정구역"].drop_duplicates().tolist()
    if area
]

if not areas:
    st.error("CSV에서 행정구역 정보를 찾지 못했습니다.")
    st.stop()

year_pattern = re.compile(r"^(20\d{2})년_")

years = sorted(
    {
        int(match.group(1))
        for column in df.columns
        for match in [year_pattern.match(column)]
        if match is not None
    }
)

if not years:
    st.error("연도별 데이터 열을 찾지 못했습니다.")
    st.stop()

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
    "100세 이상",
]


# =========================================================
# 5. 분석 조건 선택
# =========================================================
st.sidebar.header("📊 분석 조건 선택")

selected_year = st.sidebar.selectbox(
    "연도 선택",
    options=years,
    index=len(years) - 1,
)

selected_area = st.sidebar.selectbox(
    "남녀 인구를 확인할 행정구역",
    options=areas,
)

selected_age = st.sidebar.selectbox(
    "행정구역별로 비교할 연령대",
    options=age_labels,
)

selected_rows = df.loc[df["행정구역"] == selected_area]

if selected_rows.empty:
    st.error("선택한 행정구역의 데이터를 찾을 수 없습니다.")
    st.stop()

selected_row = selected_rows.iloc[0]


# =========================================================
# 6. 남성·여성 연령별 인구 데이터 만들기
# =========================================================
gender_chart_data = []

for age in age_labels:
    male_count = get_age_population(
        selected_row,
        selected_year,
        "남_",
        age,
    )

    female_count = get_age_population(
        selected_row,
        selected_year,
        "여_",
        age,
    )

    if male_count is not None:
        gender_chart_data.append(
            {
                "연령대": age,
                "성별": "남성",
                "인구수": male_count,
            }
        )

    if female_count is not None:
        gender_chart_data.append(
            {
                "연령대": age,
                "성별": "여성",
                "인구수": female_count,
            }
        )

gender_df = pd.DataFrame(gender_chart_data)

if gender_df.empty:
    st.error("선택한 행정구역과 연도의 남녀 인구 데이터가 없습니다.")
    st.stop()

male_total = int(
    gender_df.loc[
        gender_df["성별"] == "남성",
        "인구수",
    ].sum()
)

female_total = int(
    gender_df.loc[
        gender_df["성별"] == "여성",
        "인구수",
    ].sum()
)

metric1, metric2, metric3 = st.columns(3)

metric1.metric("남성 인구 합계", f"{male_total:,}명")
metric2.metric("여성 인구 합계", f"{female_total:,}명")
metric3.metric(
    "남녀 인구 합계",
    f"{male_total + female_total:,}명",
)


# =========================================================
# 7. 남녀 연령대별 인구 비교 - 선 그래프 유지
# =========================================================
st.subheader("👫 남녀 연령대별 인구 비교")

st.caption(
    f"{selected_area} · {selected_year}년 기준 "
    "남성은 핫핑크 선, 여성은 남색 선으로 표시합니다."
)

male_df = gender_df[gender_df["성별"] == "남성"]
female_df = gender_df[gender_df["성별"] == "여성"]

all_gender_values = gender_df["인구수"].tolist()
max_population = max(all_gender_values) if all_gender_values else 0

y_axis_max = max(
    100_000,
    math.ceil(max_population / 100_000) * 100_000,
)

gender_fig = go.Figure()

gender_fig.add_trace(
    go.Scatter(
        x=male_df["연령대"],
        y=male_df["인구수"],
        name="남성",
        mode="lines+markers",
        line={"color": PINK, "width": 3},
        marker={"color": PINK, "size": 8},
        hovertemplate="남성 · %{x}<br>%{y:,.0f}명<extra></extra>",
    )
)

gender_fig.add_trace(
    go.Scatter(
        x=female_df["연령대"],
        y=female_df["인구수"],
        name="여성",
        mode="lines+markers",
        line={"color": NAVY, "width": 3},
        marker={"color": NAVY, "size": 8},
        hovertemplate="여성 · %{x}<br>%{y:,.0f}명<extra></extra>",
    )
)

gender_fig.update_layout(
    title=f"{selected_year}년 {selected_area} 남녀 연령별 인구",
    xaxis={
        "title": "연령대",
        "type": "category",
        "categoryorder": "array",
        "categoryarray": age_labels,
        "showgrid": True,
        "gridcolor": "#E6E6E6",
    },
    yaxis={
        "title": "인구수 (명)",
        "range": [0, y_axis_max],
        "tick0": 0,
        "dtick": 100_000,
        "tickformat": ",d",
        "showgrid": True,
        "gridcolor": "#D8D8D8",
    },
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    hovermode="x",
    height=570,
    margin={"l": 80, "r": 30, "t": 85, "b": 75},
    legend={"title": "성별"},
)

st.plotly_chart(
    gender_fig,
    use_container_width=True,
    config={"displaylogo": False, "responsive": True},
)


# =========================================================
# 8. 선택한 연령대의 행정구역별 인구 비교 - 막대그래프
# =========================================================
st.divider()
st.subheader("🏆 연령대별 인구가 가장 많은 행정구역")

st.write(
    f"**{selected_year}년 {selected_age}** 인구를 "
    "행정구역별로 비교합니다."
)

# 제주특별자치도 전체 행은 합계이므로
# 제주시·서귀포시끼리 비교할 때 제외합니다.
district_df = df[
    df["행정구역"].str.contains("시", regex=False)
    & (df["행정구역"] != "제주특별자치도")
].copy()

district_data = []

for _, district_row in district_df.iterrows():
    district_name = district_row["행정구역"]

    population = get_age_population(
        district_row,
        selected_year,
        "",
        selected_age,
    )

    if population is not None:
        district_data.append(
            {
                "행정구역": district_name,
                "인구수": population,
            }
        )

district_chart_df = pd.DataFrame(district_data)

if district_chart_df.empty:
    st.warning(
        "선택한 연도와 연령대의 행정구역 데이터가 없습니다."
    )
else:
    district_chart_df = district_chart_df.sort_values(
        "인구수",
        ascending=False,
    ).reset_index(drop=True)

    winner = district_chart_df.iloc[0]

    winner_col, count_col = st.columns(2)

    winner_col.metric(
        f"{selected_age} 인구 1위",
        winner["행정구역"],
    )

    count_col.metric(
        "1위 인구수",
        f"{int(winner['인구수']):,}명",
    )

    bar_colors = [
        PINK if index == 0 else NAVY
        for index in range(len(district_chart_df))
    ]

    district_fig = go.Figure(
        data=[
            go.Bar(
                x=district_chart_df["행정구역"],
                y=district_chart_df["인구수"],
                marker_color=bar_colors,
                text=[
                    f"{int(value):,}명"
                    for value in district_chart_df["인구수"]
                ],
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "%{x}<br>인구수: %{y:,.0f}명<extra></extra>"
                ),
            )
        ]
    )

    district_max = int(district_chart_df["인구수"].max())

    district_y_max = max(
        10,
        math.ceil(district_max * 1.18 / 10) * 10,
    )

    district_fig.update_layout(
        title=f"{selected_year}년 {selected_age} 행정구역별 인구",
        xaxis={
            "title": "행정구역",
            "showgrid": False,
        },
        yaxis={
            "title": "인구수 (명)",
            "range": [0, district_y_max],
            "tickformat": ",d",
            "showgrid": True,
            "gridcolor": "#D8D8D8",
        },
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=450,
        margin={"l": 80, "r": 30, "t": 85, "b": 75},
        showlegend=False,
    )

    st.plotly_chart(
        district_fig,
        use_container_width=True,
        config={"displaylogo": False, "responsive": True},
    )

    st.caption(
        "인구가 가장 많은 행정구역은 핫핑크, "
        "나머지는 남색으로 표시했습니다. "
        "제주특별자치도 전체 합계 행은 비교에서 제외했습니다."
    )

    with st.expander("📋 행정구역별 인구 순위표"):
        rank_df = district_chart_df.copy()

        rank_df.insert(
            0,
            "순위",
            range(1, len(rank_df) + 1),
        )

        st.dataframe(
            rank_df,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# 9. 추가 기능: 연도별 남녀 인구 변화 추이 - 선 그래프
# =========================================================
st.divider()
st.subheader("📈 추가 분석: 연도별 남녀 인구 변화")

st.write(
    f"**{selected_area}**의 연도별 남녀 전체 인구 변화를 "
    "선 그래프로 확인해 보세요."
)

trend_rows = []

for year in years:
    for gender_name, gender_prefix in [
        ("남성", "남_"),
        ("여성", "여_"),
    ]:
        yearly_total = 0
        has_value = False

        for age in age_labels:
            value = get_age_population(
                selected_row,
                year,
                gender_prefix,
                age,
            )

            if value is not None:
                yearly_total += value
                has_value = True

        if has_value:
            trend_rows.append(
                {
                    "연도": str(year),
                    "성별": gender_name,
                    "인구수": yearly_total,
                }
            )

trend_df = pd.DataFrame(trend_rows)

if trend_df.empty:
    st.info("연도별 남녀 인구 변화 데이터를 만들 수 없습니다.")
else:
    trend_male = trend_df[trend_df["성별"] == "남성"]
    trend_female = trend_df[trend_df["성별"] == "여성"]

    trend_fig = go.Figure()

    trend_fig.add_trace(
        go.Scatter(
            x=trend_male["연도"],
            y=trend_male["인구수"],
            name="남성",
            mode="lines+markers",
            line={"color": PINK, "width": 3},
            marker={"color": PINK, "size": 8},
            hovertemplate="남성 · %{x}년<br>%{y:,.0f}명<extra></extra>",
        )
    )

    trend_fig.add_trace(
        go.Scatter(
            x=trend_female["연도"],
            y=trend_female["인구수"],
            name="여성",
            mode="lines+markers",
            line={"color": NAVY, "width": 3},
            marker={"color": NAVY, "size": 8},
            hovertemplate="여성 · %{x}년<br>%{y:,.0f}명<extra></extra>",
        )
    )

    trend_max = int(trend_df["인구수"].max())

    trend_y_max = max(
        100_000,
        math.ceil(trend_max / 100_000) * 100_000,
    )

    trend_fig.update_layout(
        title=f"{selected_area} 연도별 남녀 인구 변화",
        xaxis={
            "title": "연도",
            "type": "category",
            "showgrid": True,
            "gridcolor": "#E6E6E6",
        },
        yaxis={
            "title": "인구수 (명)",
            "range": [0, trend_y_max],
            "dtick": 100_000,
            "tickformat": ",d",
            "showgrid": True,
            "gridcolor": "#D8D8D8",
        },
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        hovermode="x",
        height=480,
        margin={"l": 80, "r": 30, "t": 80, "b": 65},
        legend={"title": "성별"},
    )

    st.plotly_chart(
        trend_fig,
        use_container_width=True,
        config={"displaylogo": False, "responsive": True},
    )

    # 첫 연도와 마지막 연도의 인구 차이 계산
    trend_summary = []

    for gender_name in ["남성", "여성"]:
        part = trend_df[
            trend_df["성별"] == gender_name
        ].copy()

        if len(part) >= 2:
            part["연도숫자"] = part["연도"].astype(int)
            part = part.sort_values("연도숫자")

            first_value = int(part.iloc[0]["인구수"])
            last_value = int(part.iloc[-1]["인구수"])
            difference = last_value - first_value

            trend_summary.append(
                {
                    "성별": gender_name,
                    "첫해 인구": first_value,
                    "최근 연도 인구": last_value,
                    "증감 인구": difference,
                }
            )

    if trend_summary:
        summary_df = pd.DataFrame(trend_summary)
        summary_cols = st.columns(len(summary_df))

        for index, row in summary_df.iterrows():
            with summary_cols[index]:
                st.metric(
                    f"{row['성별']} 인구 변화 ({years[0]}~{years[-1]}년)",
                    f"{int(row['증감 인구']):+,}명",
                    help=(
                        f"첫해 {int(row['첫해 인구']):,}명 → "
                        f"최근 연도 {int(row['최근 연도 인구']):,}명"
                    ),
                )

    with st.expander("📋 연도별 남녀 인구 데이터 보기"):
        st.dataframe(
            trend_df,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# 10. 그래프 데이터 확인 및 다운로드
# =========================================================
with st.expander("📋 남녀 그래프 데이터 확인 및 다운로드"):
    st.dataframe(
        gender_df,
        use_container_width=True,
        hide_index=True,
    )

    csv_bytes = gender_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 남녀 인구 데이터 CSV 다운로드",
        data=csv_bytes,
        file_name=f"jeju_{selected_year}_male_female_population.csv",
        mime="text/csv",
    )


# =========================================================
# 11. 데이터 파일 정보
# =========================================================
with st.expander("ℹ️ 데이터 파일 정보"):
    st.write(f"파일 이름: {file_name}")
    st.write(f"감지된 인코딩: {used_encoding}")
    st.write(f"전체 행정구역 수: {len(areas)}개")
    st.write(f"분석 가능한 연도: {', '.join(map(str, years))}")
    st.write(
        f"원본 데이터 결측치: {int(df.isna().sum().sum()):,}개"
    )

st.success("남녀 비교와 연령대별 행정구역 분석이 완료됐어요! 🌸")
