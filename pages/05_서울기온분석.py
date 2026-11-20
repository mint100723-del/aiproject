import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="서울 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 기온 분석")
st.markdown(
    "서울의 월별 평균기온과 연도별 최고·최저기온을 분석해 보세요!"
)

# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================
current_dir = Path(__file__).resolve().parent

possible_paths = [
    current_dir / "temperature.csv",
    current_dir.parent / "temperature.csv"
]

csv_path = None

for path in possible_paths:
    if path.exists():
        csv_path = path
        break

if csv_path is None:
    st.error(
        "temperature.csv 파일을 찾을 수 없습니다. "
        "프로젝트 최상위 폴더에 CSV 파일을 넣어주세요."
    )
    st.stop()


# ==========================================
# 3. 데이터 불러오기 및 전처리
# ==========================================
@st.cache_data
def load_data(file_path):

    # 한글 인코딩 자동 확인
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
        raise ValueError("CSV 파일의 인코딩을 확인해주세요.")

    data.columns = (
        data.columns.astype(str).str.strip()
    )

    # 필요한 열 확인
    required_columns = [
        "일시",
        "평균기온(℃)",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(
                f"CSV 파일에 '{col}' 열이 없습니다."
            )

    # 기온 데이터 숫자 변환
    temperature_columns = [
        "평균기온(℃)",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in temperature_columns:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    # ======================================
    # 날짜 변환
    # Oct-07 형식의 연도를 순서에 맞게 처리
    # 1907년부터 2026년까지 지원
    # ======================================

    month_map = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }

    dates = []
    century = 1900
    previous_year = None

    for value in data["일시"]:

        try:
            month_text, year_text = (
                str(value).strip().split("-")
            )

            month_text = month_text.title()
            year_number = int(year_text)

            # 연도가 99에서 00으로 바뀌면
            # 다음 세기로 이동
            if previous_year is not None:
                if year_number < previous_year:
                    century += 100

            full_year = century + year_number

            month_number = month_map[month_text]

            dates.append(
                pd.Timestamp(
                    year=full_year,
                    month=month_number,
                    day=1
                )
            )

            previous_year = year_number

        except (ValueError, KeyError, TypeError):
            dates.append(pd.NaT)

    data["날짜"] = pd.to_datetime(dates)

    # 날짜가 없는 데이터 제외
    data = data.dropna(
        subset=["날짜"]
    ).copy()

    data["연도"] = data["날짜"].dt.year.astype(int)
    data["월"] = data["날짜"].dt.month.astype(int)

    return data.sort_values(
        ["연도", "월"]
    ).reset_index(drop=True)


# ==========================================
# 4. 데이터 실행
# ==========================================
try:
    df = load_data(str(csv_path))

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.code(str(e))
    st.stop()

if df.empty:
    st.warning("분석할 데이터가 없습니다.")
    st.stop()


# 월 이름
month_names = [
    "1월", "2월", "3월", "4월",
    "5월", "6월", "7월", "8월",
    "9월", "10월", "11월", "12월"
]


# ==========================================
# 5. 그래프 공통 디자인
# ==========================================
def set_graph_style(fig, title):

    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor="center",
            font=dict(size=23)
        ),

        xaxis=dict(
            title="월",
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=month_names,
            showgrid=True
        ),

        yaxis=dict(
            title="온도 (℃)",
            showgrid=True,
            zeroline=True
        ),

        template="plotly_white",

        font=dict(
            family="sans-serif",
            size=13
        ),

        hovermode="x unified",

        height=520,

        legend=dict(
            title="기온 구분",
            orientation="h",
            y=1.12,
            x=1,
            xanchor="right"
        ),

        margin=dict(
            l=50,
            r=30,
            t=100,
            b=60
        )
    )

    return fig


# ==========================================
# 6. 그래프 1
# 서울의 월별 평균기온
# ==========================================
st.divider()

st.header("📊 1. 서울의 월별 평균기온")

st.write(
    "전체 연도의 데이터를 월별로 평균 내어 "
    "서울의 계절별 기온 변화를 보여줍니다."
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
            color="#219EBC",
            width=3
        ),

        marker=dict(
            size=9
        ),

        connectgaps=False,

        hovertemplate=
        "%{x}월<br>평균기온: %{y:.1f}℃<extra></extra>"
    )
)

set_graph_style(
    fig1,
    "서울의 월별 평균기온"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# ==========================================
# 7. 그래프 2
# 연도 선택
# ==========================================
st.divider()

st.header("📈 2. 연도별 최고기온과 최저기온")

st.write(
    "연도를 선택하면 해당 연도의 최고기온과 "
    "최저기온을 하나의 그래프에서 확인할 수 있습니다."
)

available_years = sorted(
    df["연도"].unique().tolist()
)

selected_years = st.multiselect(
    "📅 분석할 연도를 선택하세요 (최대 2개)",

    options=available_years,

    default=[available_years[-1]],

    max_selections=2,

    format_func=lambda x: f"{x}년"
)


# ==========================================
# 8. 연도별 기온 그래프
# ==========================================
if len(selected_years) == 0:

    st.info("분석할 연도를 1개 또는 2개 선택해주세요.")

else:

    selected_years = sorted(selected_years)

    fig2 = go.Figure()

    for index, year in enumerate(selected_years):

        year_data = df[
            df["연도"] == year
        ].copy()

        # 같은 연도와 월에 여러 자료가 있다면 평균 계산
        year_data = (
            year_data.groupby("월")[
                ["최고기온(℃)", "최저기온(℃)"]
            ].mean()
        )

        # 1~12월 순서 유지
        year_data = year_data.reindex(
            range(1, 13)
        )

        # 연도 구분
        if index == 0:
            line_style = "solid"
        else:
            line_style = "dash"

        # ----------------------------------
        # 최고기온: 핫핑크
        # ----------------------------------
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

                connectgaps=False,

                hovertemplate=
                f"{year}년 최고기온<br>"
                "%{x}월: %{y:.1f}℃<extra></extra>"
            )
        )

        # ----------------------------------
        # 최저기온: 남색
        # ----------------------------------
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

                connectgaps=False,

                hovertemplate=
                f"{year}년 최저기온<br>"
                "%{x}월: %{y:.1f}℃<extra></extra>"
            )
        )

    # ======================================
    # 그래프 제목 자동 변경
    # ======================================
    if len(selected_years) == 1:

        graph_title = (
            f"{selected_years[0]}년 "
            "월별 최고기온과 최저기온"
        )

    else:

        graph_title = (
            f"{selected_years[0]}년과 "
            f"{selected_years[1]}년 기온 비교"
        )

    set_graph_style(
        fig2,
        graph_title
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ==========================================
# 9. 선택한 연도 데이터 표
# ==========================================
st.divider()

st.header("📋 3. 기온 데이터 확인")

if len(selected_years) > 0:

    with st.expander("선택한 연도의 상세 데이터 보기"):

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

        table["월"] = (
            table["월"].astype(str) + "월"
        )

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# 10. 데이터 정보
# ==========================================
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "시작 연도",
        f"{df['연도'].min()}년"
    )

with col2:
    st.metric(
        "마지막 연도",
        f"{df['연도'].max()}년"
    )

with col3:
    st.metric(
        "전체 데이터",
        f"{len(df):,}개"
    )

st.caption(
    "서울 기온 데이터 분석 | "
    "CSV 자료를 활용한 월별 및 연도별 기온 분석"
)
