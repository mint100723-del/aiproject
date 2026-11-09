import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# =====================================
# 페이지 설정
# =====================================
st.set_page_config(
    page_title="서울 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 기온 분석")
st.write("서울의 장기적인 기온 변화를 그래프로 살펴보세요!")

# =====================================
# CSV 파일 경로
# =====================================
current_dir = Path(__file__).resolve().parent

possible_paths = [
    current_dir / "temperature.csv",
    current_dir.parent / "temperature.csv"
]

csv_path = next(
    (p for p in possible_paths if p.exists()),
    None
)

if csv_path is None:
    st.error(
        "temperature.csv 파일을 찾을 수 없습니다. "
        "프로젝트 최상위 폴더에 CSV 파일을 넣어주세요."
    )
    st.stop()


# =====================================
# 데이터 불러오기
# =====================================
@st.cache_data
def load_data(file_path):

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    data = None

    for encoding in encodings:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError("CSV 인코딩을 확인해주세요.")

    data.columns = (
        data.columns.astype(str).str.strip()
    )

    required_columns = [
        "일시",
        "평균기온(℃)",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(
                f"'{col}' 열이 CSV에 없습니다."
            )

    # 기온 숫자 변환
    for col in [
        "평균기온(℃)",
        "최고기온(℃)",
        "최저기온(℃)"
    ]:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    # 날짜 변환
    data["날짜"] = pd.to_datetime(
        data["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    # 날짜 형식이 다른 경우 추가 처리
    missing = data["날짜"].isna()

    if missing.any():
        data.loc[missing, "날짜"] = pd.to_datetime(
            data.loc[missing, "일시"],
            errors="coerce"
        )

    data = data.dropna(
        subset=["날짜"]
    ).copy()

    data["연도"] = data["날짜"].dt.year
    data["월"] = data["날짜"].dt.month

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    return data.sort_values(
        ["연도", "월"]
    )


# =====================================
# 데이터 실행
# =====================================
try:
    df = load_data(str(csv_path))

except Exception as e:
    st.error("데이터 처리 중 오류가 발생했습니다.")
    st.code(str(e))
    st.stop()

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()


month_names = [
    f"{i}월" for i in range(1, 13)
]

# =====================================
# 그래프 공통 설정
# =====================================
def graph_layout(fig, title):

    fig.update_layout(
        title=title,
        xaxis_title="월",
        yaxis_title="온도 (℃)",
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=month_names
        ),
        hovermode="x unified",
        template="plotly_white",
        font=dict(
            family="Malgun Gothic, sans-serif",
            size=13
        ),
        height=500,
        legend=dict(
            orientation="h",
            y=1.12,
            x=1,
            xanchor="right"
        )
    )

    return fig


# =====================================
# 1. 월별 평균기온 그래프
# =====================================
st.divider()

st.header("📊 1. 서울의 월별 평균기온")

st.write(
    "전체 연도 데이터를 이용하여 "
    "1월부터 12월까지의 평균기온을 계산합니다."
)

monthly_avg = (
    df.dropna(subset=["평균기온(℃)"])
      .groupby("월")["평균기온(℃)"]
      .mean()
      .reindex(range(1, 13))
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=list(range(1, 13)),
        y=monthly_avg.values,
        mode="lines+markers",
        name="월별 평균기온",
        line=dict(
            color="#2A9D8F",
            width=3
        ),
        marker=dict(size=9),
        connectgaps=False
    )
)

graph_layout(
    fig1,
    "서울의 월별 평균기온"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# =====================================
# 2. 연도 선택
# =====================================
st.divider()

st.header("📈 2. 연도별 최고기온과 최저기온")

st.write(
    "연도를 1개 선택하면 해당 연도의 기온을, "
    "2개 선택하면 두 연도의 기온을 비교합니다."
)

years = sorted(
    df["연도"].unique().tolist()
)

selected_years = st.multiselect(
    "비교할 연도를 선택하세요.",
    options=years,
    default=[years[-1]],
    max_selections=2,
    format_func=lambda x: f"{x}년"
)

if len(selected_years) == 0:

    st.info("연도를 하나 이상 선택해주세요.")

else:

    selected_years = sorted(selected_years)

    fig2 = go.Figure()

    # 연도별 그래프
    for index, year in enumerate(selected_years):

        year_data = df[
            df["연도"] == year
        ].copy()

        # 월별 자료 정리
        year_data = (
            year_data.groupby("월")[
                ["최고기온(℃)", "최저기온(℃)"]
            ].mean()
        )

        year_data = year_data.reindex(
            range(1, 13)
        )

        # 연도별 선 모양
        line_style = (
            "solid" if index == 0 else "dash"
        )

        # 최고기온
        fig2.add_trace(
            go.Scatter(
                x=list(range(1, 13)),
                y=year_data["최고기온(℃)"],
                mode="lines+markers",
                name=f"{year}년 최고기온",
                line=dict(
                    color="#FF1493",
                    width=3,
                    dash=line_style
                ),
                marker=dict(size=8),
                connectgaps=False
            )
        )

        # 최저기온
        fig2.add_trace(
            go.Scatter(
                x=list(range(1, 13)),
                y=year_data["최저기온(℃)"],
                mode="lines+markers",
                name=f"{year}년 최저기온",
                line=dict(
                    color="#191970",
                    width=3,
                    dash=line_style
                ),
                marker=dict(size=8),
                connectgaps=False
            )
        )

    # 제목 설정
    if len(selected_years) == 1:

        title = (
            f"{selected_years[0]}년 "
            "월별 최고기온과 최저기온"
        )

    else:

        title = (
            f"{selected_years[0]}년과 "
            f"{selected_years[1]}년 기온 비교"
        )

    graph_layout(fig2, title)

    fig2.update_layout(
        yaxis_title="온도 (℃)"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# =====================================
# 3. 데이터 표
# =====================================
st.divider()

with st.expander("📋 선택한 연도의 기온 데이터 보기"):

    if len(selected_years) > 0:

        table = df[
            df["연도"].isin(selected_years)
        ][
            [
                "연도",
                "월",
                "평균기온(℃)",
                "최고기온(℃)",
                "최저기온(℃)"
            ]
        ].copy()

        table["월"] = table["월"].astype(str) + "월"

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True
        )


st.caption(
    f"분석 데이터: {df['연도'].min()}년 ~ "
    f"{df['연도'].max()}년"
)
