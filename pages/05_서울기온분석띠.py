import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
from pathlib import Path
from datetime import datetime
from matplotlib.ticker import MaxNLocator

# 페이지 설정
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)


# CSV 읽기 및 전처리
@st.cache_data
def load_temperature_data(file_path):

    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]
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
        raise ValueError("CSV 인코딩을 확인해 주세요.")

    data.columns = data.columns.astype(str).str.strip()

    required = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    missing = [
        col for col in required
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            f"필요한 열이 없습니다: {missing}"
        )

    for col in ["최고기온(℃)", "최저기온(℃)"]:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    # 연도 및 월 변환
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    dates = []
    century = 1900
    previous_year = None

    for value in data["일시"]:

        try:
            month, year = str(value).strip().split("-")
            year = int(year)

            if previous_year is not None:
                if year < previous_year:
                    century += 100

            full_year = century + year

            dates.append(
                datetime(
                    full_year,
                    month_map[month.title()],
                    1
                )
            )

            previous_year = year

        except (ValueError, KeyError, TypeError):
            dates.append(pd.NaT)

    data["날짜"] = pd.to_datetime(dates)

    data = data.dropna(subset=["날짜"]).copy()

    data["연도"] = data["날짜"].dt.year
    data["월"] = data["날짜"].dt.month

    return data.sort_values(
        ["연도", "월"]
    ).reset_index(drop=True)


# 데이터 불러오기
CSV_PATH = Path(__file__).resolve().parent / "temperature.csv"

st.title("🌡️ 월별 기온분석")

st.write(
    "원하는 월을 선택하면 전체 연도의 "
    "최고기온과 최저기온 변화를 비교할 수 있어요."
)

if not CSV_PATH.exists():
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.info("app.py와 temperature.csv를 같은 폴더에 넣어주세요.")
    st.stop()

try:
    df = load_temperature_data(str(CSV_PATH))

except Exception as error:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.code(str(error))
    st.stop()

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()


# 월 선택
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

available_months = sorted(
    df["월"].unique().tolist()
)

selected_month = st.selectbox(
    "📅 분석할 월을 선택하세요",
    options=available_months,
    format_func=lambda x: month_names[x]
)


# 선택한 월 데이터
monthly_data = df[
    df["월"] == selected_month
].copy()

monthly_data = monthly_data.dropna(
    subset=["최고기온(℃)", "최저기온(℃)"]
)

monthly_data = monthly_data.sort_values("연도")

st.subheader(
    f"📊 {month_names[selected_month]} 전체 연도 기온 변화"
)

if monthly_data.empty:
    st.warning("분석할 데이터가 없습니다.")
    st.stop()


# 그래프 생성
fig, ax = plt.subplots(figsize=(16, 6.5))

# 최고기온: 핫핑크
ax.plot(
    monthly_data["연도"],
    monthly_data["최고기온(℃)"],
    color="#FF1493",
    linewidth=2,
    marker="o",
    markersize=3.5,
    label="최고기온"
)

# 최저기온: 남색
ax.plot(
    monthly_data["연도"],
    monthly_data["최저기온(℃)"],
    color="#191970",
    linewidth=2,
    marker="o",
    markersize=3.5,
    label="최저기온"
)

# 그래프 제목 및 축
ax.set_title(
    "월별 기온분석",
    fontsize=20,
    pad=18
)

ax.set_xlabel("연도", fontsize=13)
ax.set_ylabel("온도(℃)", fontsize=13)

# 가로축 연도 표시 간격
ax.xaxis.set_major_locator(
    MaxNLocator(nbins=15, integer=True)
)

# 격자 및 범례
ax.grid(
    True,
    linestyle="--",
    alpha=0.35
)

ax.legend(
    loc="best",
    fontsize=12
)

ax.tick_params(
    axis="x",
    labelrotation=45
)

fig.tight_layout()

st.pyplot(fig, clear_figure=True)
plt.close(fig)


# 데이터 표
with st.expander("📋 연도별 기온 데이터 확인하기"):

    display_data = monthly_data[
        ["연도", "최고기온(℃)", "최저기온(℃)"]
    ].copy()

    display_data["연도"] = display_data["연도"].astype(int)

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

st.caption(
    f"분석 연도: {int(monthly_data['연도'].min())}년 ~ "
    f"{int(monthly_data['연도'].max())}년 | "
    f"유효 데이터: {len(monthly_data)}개"
)
