import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import re

# --------------------------------------------------
# 기본 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="서울 월별 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 평균기온 예측")
st.write(
    "원하는 월과 예측 연도를 선택하면 "
    "과거 기온 데이터를 바탕으로 미래의 평균기온을 예측해 줘!"
)

st.divider()


# --------------------------------------------------
# CSV 파일 불러오기
# --------------------------------------------------
@st.cache_data
def load_temperature_data():
    current_folder = Path(__file__).resolve().parent

    # pages 폴더 또는 프로젝트 최상위 폴더에서 CSV 찾기
    possible_paths = [
        current_folder / "temperature.csv",
        current_folder.parent / "temperature.csv"
    ]

    csv_path = None

    for path in possible_paths:
        if path.exists():
            csv_path = path
            break

    if csv_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다. "
            "프로젝트 최상위 폴더에 temperature.csv를 넣어 주세요."
        )

    # CSV 인코딩 자동 시도
    data = None
    last_error = None

    for encoding in ["cp949", "utf-8-sig", "utf-8", "euc-kr"]:
        try:
            data = pd.read_csv(csv_path, encoding=encoding)
            break
        except Exception as error:
            last_error = error

    if data is None:
        raise ValueError(
            f"CSV 파일을 읽지 못했습니다: {last_error}"
        )

    required_columns = ["일시", "평균기온(℃)"]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                f"CSV에 '{column}' 열이 없습니다. "
                f"현재 열 이름: {list(data.columns)}"
            )

    # 월별 날짜 정보 처리
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    parsed_years = []
    parsed_months = []

    # 업로드된 자료는 1907년부터 시작하는 2자리 연도 형식
    century = 1900
    previous_short_year = None

    for value in data["일시"].astype(str):
        match = re.fullmatch(
            r"\s*([A-Za-z]{3})-(\d{2})\s*",
            value
        )

        if match is None:
            parsed_years.append(np.nan)
            parsed_months.append(np.nan)
            continue

        month_text = match.group(1).title()
        short_year = int(match.group(2))

        month_number = month_map.get(month_text)

        if month_number is None:
            parsed_years.append(np.nan)
            parsed_months.append(np.nan)
            continue

        # 99년 다음 00년처럼 연도가 바뀌면 세기 변경
        if (
            previous_short_year is not None
            and short_year < previous_short_year
        ):
            century += 100

        full_year = century + short_year

        parsed_years.append(full_year)
        parsed_months.append(month_number)

        previous_short_year = short_year

    data["연도"] = parsed_years
    data["월"] = parsed_months

    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    # 날짜 또는 평균기온이 없는 행 제거
    data = data.dropna(
        subset=["연도", "월", "평균기온(℃)"]
    ).copy()

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    data = data.sort_values(
        by=["연도", "월"]
    ).reset_index(drop=True)

    if data.empty:
        raise ValueError("분석할 수 있는 기온 데이터가 없습니다.")

    return data


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
try:
    df = load_temperature_data()

except Exception as error:
    st.error(f"데이터를 불러오는 중 문제가 발생했습니다.\n\n{error}")
    st.stop()


# --------------------------------------------------
# 사용자 입력
# --------------------------------------------------
st.subheader("🔎 예측 조건 선택")

col1, col2 = st.columns(2)

month_names = {
    1: "1월", 2: "2월", 3: "3월", 4: "4월",
    5: "5월", 6: "6월", 7: "7월", 8: "8월",
    9: "9월", 10: "10월", 11: "11월", 12: "12월"
}

with col1:
    selected_month = st.selectbox(
        "예측하고 싶은 월을 선택해 줘!",
        options=list(range(1, 13)),
        format_func=lambda x: month_names[x],
        index=0
    )

latest_year = int(df["연도"].max())

with col2:
    prediction_year = st.number_input(
        "예측할 연도를 입력해 줘!",
        min_value=latest_year + 1,
        max_value=2100,
        value=latest_year + 1,
        step=1
    )

st.info(
    f"📅 선택한 조건: **{month_names[selected_month]} / "
    f"{int(prediction_year)}년**"
)


# --------------------------------------------------
# 선택한 월의 과거 데이터 추출
# --------------------------------------------------
month_data = df[
    df["월"] == selected_month
].copy()

month_data = month_data.sort_values("연도")

if len(month_data) < 2:
    st.error(
        "선택한 월의 데이터가 2개 연도보다 적어서 "
        "선형회귀 예측을 할 수 없습니다."
    )
    st.stop()


# --------------------------------------------------
# 선형회귀 계산
# y = a*x + b
# --------------------------------------------------
x = month_data["연도"].to_numpy(dtype=float)
y = month_data["평균기온(℃)"].to_numpy(dtype=float)

# 평균을 이용한 최소제곱 선형회귀
x_mean = np.mean(x)
y_mean = np.mean(y)

denominator = np.sum((x - x_mean) ** 2)

if denominator == 0:
    st.error("연도 데이터가 충분하지 않아 회귀선을 계산할 수 없습니다.")
    st.stop()

slope = np.sum(
    (x - x_mean) * (y - y_mean)
) / denominator

intercept = y_mean - slope * x_mean

# 입력한 연도의 예측 기온
predicted_temperature = (
    slope * float(prediction_year) + intercept
)

# 과거 데이터에 대한 회귀선 예측값
fitted_values = slope * x + intercept

# 결정계수 R² 계산
ss_total = np.sum((y - y_mean) ** 2)
ss_residual = np.sum((y - fitted_values) ** 2)

if ss_total == 0:
    r_squared = 0.0
else:
    r_squared = 1 - (ss_residual / ss_total)


# --------------------------------------------------
# 예측 결과 표시
# --------------------------------------------------
st.divider()
st.subheader("🎯 기온 예측 결과")

result_col1, result_col2, result_col3 = st.columns(3)

with result_col1:
    st.metric(
        label="예측 연도",
        value=f"{int(prediction_year)}년 {month_names[selected_month]}"
    )

with result_col2:
    st.metric(
        label="예측 평균기온",
        value=f"{predicted_temperature:.1f} ℃"
    )

with result_col3:
    st.metric(
        label="결정계수 (R²)",
        value=f"{r_squared:.3f}"
    )

if slope > 0:
    st.success(
        f"📈 선택한 월의 장기적인 기온 추세는 "
        f"1년에 약 {slope:.3f}℃ 상승하는 방향이야."
    )
elif slope < 0:
    st.info(
        f"📉 선택한 월의 장기적인 기온 추세는 "
        f"1년에 약 {abs(slope):.3f}℃ 하락하는 방향이야."
    )
else:
    st.info("선택한 월의 장기적인 기온 추세는 거의 일정해.")


# --------------------------------------------------
# 그래프 만들기
# --------------------------------------------------
st.divider()
st.subheader("📊 과거 기온과 선형회귀 예측 그래프")

# 관측 기간의 회귀선
historical_line_x = np.linspace(
    float(x.min()),
    float(x.max()),
    200
)

historical_line_y = (
    slope * historical_line_x + intercept
)

# 마지막 관측 연도부터 예측 연도까지 회귀선 연장
forecast_line_x = np.linspace(
    float(x.max()),
    float(prediction_year),
    100
)

forecast_line_y = (
    slope * forecast_line_x + intercept
)

fig = go.Figure()

# 1. 실제 과거 평균기온
fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="#2878B5",
            size=8,
            opacity=0.75
        ),
        hovertemplate=(
            "%{x:.0f}년<br>"
            "실제 평균기온: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

# 2. 과거 데이터에 맞춘 선형회귀 직선
fig.add_trace(
    go.Scatter(
        x=historical_line_x,
        y=historical_line_y,
        mode="lines",
        name="선형회귀 직선",
        line=dict(
            color="#E85D75",
            width=3
        ),
        hovertemplate=(
            "%{x:.0f}년<br>"
            "회귀선 기온: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

# 3. 미래 예측 구간
fig.add_trace(
    go.Scatter(
        x=forecast_line_x,
        y=forecast_line_y,
        mode="lines",
        name="미래 예측 추세",
        line=dict(
            color="#F39C12",
            width=3,
            dash="dash"
        ),
        hovertemplate=(
            "%{x:.0f}년<br>"
            "예측 추세: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

# 4. 최종 예측 지점
fig.add_trace(
    go.Scatter(
        x=[prediction_year],
        y=[predicted_temperature],
        mode="markers+text",
        name="최종 예측 기온",
        marker=dict(
            color="#8E44AD",
            size=17,
            symbol="star",
            line=dict(
                color="white",
                width=1
            )
        ),
        text=[f"{predicted_temperature:.1f}℃"],
        textposition="top center",
        textfont=dict(
            size=14,
            color="#8E44AD"
        ),
        hovertemplate=(
            "%{x:.0f}년<br>"
            "예측 평균기온: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

# 예측 연도 표시
fig.add_vline(
    x=prediction_year,
    line_width=1,
    line_dash="dot",
    line_color="gray"
)

fig.update_layout(
    title=dict(
        text=(
            f"{month_names[selected_month]} 서울 평균기온 "
            f"선형회귀 분석"
        ),
        x=0.5
    ),
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    height=600,
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    margin=dict(
        l=30,
        r=30,
        t=100,
        b=50
    )
)

fig.update_xaxes(
    showgrid=True,
    gridcolor="lightgray",
    tickformat="d"
)

fig.update_yaxes(
    showgrid=True,
    gridcolor="lightgray",
    ticksuffix="℃"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 그래프 해석
# --------------------------------------------------
st.markdown("### 🧭 그래프 보는 방법")

st.markdown(
    """
    - 🔵 **파란 점:** temperature.csv에 기록된 실제 월별 평균기온이야.
    - 🌸 **분홍색 실선:** 과거의 모든 관측값에 가장 잘 맞도록 계산한 선형회귀 직선이야.
    - 🟠 **주황색 점선:** 과거의 회귀 추세를 예측 연도까지 연장한 선이야.
    - 💜 **보라색 별:** 선택한 연도의 최종 예측 평균기온이야.

    점들이 회귀선 주변에 얼마나 가까이 모여 있는지 살펴보면
    직선이 과거 데이터의 경향을 얼마나 잘 설명하는지 확인할 수 있어.
    """
)


# --------------------------------------------------
# 선형회귀 알고리즘 설명
# --------------------------------------------------
st.divider()
st.subheader("📚 선형회귀 알고리즘이란?")

st.markdown(
    """
    **선형회귀(Linear Regression)**는 과거 데이터의 관계를
    하나의 직선으로 나타내고, 그 직선을 이용해 새로운 값을 예측하는 방법이야.

    이번 프로그램에서는 다음과 같이 사용했어.

    1. **과거 데이터 수집:** 선택한 월의 모든 연도별 평균기온을 모아.
    2. **관계 찾기:** 연도를 가로축, 평균기온을 세로축으로 놓고 점을 찍어.
    3. **회귀선 계산:** 실제 점들과 직선 사이의 차이가 전체적으로 작아지도록 직선을 계산해.
    4. **미래 예측:** 계산한 직선에 입력한 예측 연도를 넣어 평균기온을 구해.

    ### 📐 선형회귀의 기본 원리

    예측 직선은 다음과 같은 형태야.

    """
)

st.latex(r"\hat{y} = ax + b")

st.markdown(
    """
    - **x:** 연도
    - **ŷ:** 선형회귀가 예측한 평균기온
    - **a:** 기울기. 연도가 1년 증가할 때 기온이 얼마나 변하는지 나타내.
    - **b:** y절편. 직선의 위치를 결정하는 값이야.

    ### 🔍 이번 예측에 사용된 계산 결과
    """
)

st.code(
    f"예측 직선: y = {slope:.5f} × 연도 + ({intercept:.5f})\n"
    f"기울기: {slope:.5f}\n"
    f"y절편: {intercept:.5f}\n"
    f"결정계수 R²: {r_squared:.5f}",
    language="text"
)

st.markdown(
    """
    **결정계수(R²)**는 회귀선이 과거 기온 데이터의 변화를
    얼마나 설명하는지 보여주는 값이야.

    - 1에 가까울수록 과거 데이터의 변화를 직선이 잘 설명해.
    - 0에 가까울수록 직선만으로 과거 데이터의 변화를 설명하기 어려워.

    ⚠️ **꼭 알아둘 점!**

    기온은 여러 기후 요인의 영향을 받기 때문에 선형회귀 예측값이
    실제 미래 기온과 정확히 일치하는 것은 아니야.
    이 결과는 과거의 장기적인 경향을 직선으로 연장한 통계적 추정값이야.
    """
)


# --------------------------------------------------
# 데이터 확인
# --------------------------------------------------
with st.expander("📋 선택한 월의 실제 데이터 확인하기"):
    display_data = month_data[
        ["연도", "월", "평균기온(℃)"]
    ].copy()

    display_data["월"] = display_data["월"].map(month_names)

    st.dataframe(
        display_data.rename(
            columns={
                "연도": "연도",
                "월": "월",
                "평균기온(℃)": "평균기온 (℃)"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "자료: temperature.csv | 분석 방법: 최소제곱법 기반 단순 선형회귀"
)
