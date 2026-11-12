
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re
import math
from pathlib import Path

# =====================================================
# 1. 페이지 기본 설정
# =====================================================
st.set_page_config(
    page_title="서울 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 평균기온 예측")
st.write("과거 기온 데이터를 바탕으로 미래의 평균기온을 예측해 봐요!")

st.divider()

# =====================================================
# 2. 데이터 파일 불러오기
# =====================================================
@st.cache_data
def load_temperature_data():

    current_folder = Path(__file__).resolve().parent

    possible_paths = [
        current_folder / "temperature.csv",
        current_folder.parent / "temperature.csv",
        current_folder.parent.parent / "temperature.csv"
    ]

    file_path = None

    for path in possible_paths:
        if path.exists():
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다. "
            "GitHub 저장소의 최상위 폴더에 temperature.csv를 넣어 주세요."
        )

    # 다양한 인코딩 시도
    df = None

    for encoding in ["cp949", "utf-8-sig", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError("CSV 파일의 인코딩을 읽을 수 없습니다.")

    # 열 이름 공백 및 BOM 제거
    df.columns = (
        df.columns.astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    required_columns = ["일시", "평균기온(℃)"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"CSV 파일에 '{column}' 열이 없습니다. "
                f"현재 열 이름: {list(df.columns)}"
            )

    # =================================================
    # 날짜 데이터 정리
    # =================================================
    def parse_month_dates(date_series):

        years = []
        months = []

        previous_short_year = None
        century = 1900

        month_map = {
            "Jan": 1, "Feb": 2, "Mar": 3,
            "Apr": 4, "May": 5, "Jun": 6,
            "Jul": 7, "Aug": 8, "Sep": 9,
            "Oct": 10, "Nov": 11, "Dec": 12
        }

        for value in date_series:

            value = str(value).strip()

            # Oct-07 형식 처리
            match = re.match(
                r"^([A-Za-z]{3})[-/ ](\d{2})$",
                value
            )

            if match:
                month_text = match.group(1).title()
                short_year = int(match.group(2))

                if month_text not in month_map:
                    years.append(np.nan)
                    months.append(np.nan)
                    continue

                # 99년 다음 00년으로 넘어가는 경우 처리
                if (
                    previous_short_year is not None
                    and short_year < previous_short_year
                ):
                    century += 100

                year = century + short_year
                month = month_map[month_text]

                previous_short_year = short_year

                years.append(year)
                months.append(month)
                continue

            # YYYY-MM 또는 YYYY-MM-DD 형식 처리
            parsed = pd.to_datetime(
                value,
                errors="coerce"
            )

            if pd.isna(parsed):
                years.append(np.nan)
                months.append(np.nan)
            else:
                years.append(parsed.year)
                months.append(parsed.month)

        return years, months

    years, months = parse_month_dates(df["일시"])

    df["연도"] = years
    df["월번호"] = months

    # 기온 숫자 변환
    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"],
        errors="coerce"
    )

    # 결측치 제거
    df = df.dropna(
        subset=["연도", "월번호", "평균기온(℃)"]
    ).copy()

    df["연도"] = df["연도"].astype(int)
    df["월번호"] = df["월번호"].astype(int)

    df = df.sort_values(
        ["연도", "월번호"]
    ).reset_index(drop=True)

    if df.empty:
        raise ValueError("분석할 수 있는 기온 데이터가 없습니다.")

    return df


# =====================================================
# 3. 데이터 불러오기 오류 처리
# =====================================================
try:
    raw_data = load_temperature_data()

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했어요.")
    st.error(str(e))
    st.stop()


# =====================================================
# 4. 월 이름 설정
# =====================================================
month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}


# =====================================================
# 5. 사용자 선택
# =====================================================
st.subheader("📅 예측할 시기 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측하고 싶은 월을 선택하세요.",
        list(range(1, 13)),
        format_func=lambda x: month_names[x]
    )

latest_year = int(raw_data["연도"].max())

with col2:
    prediction_year = st.number_input(
        "예측하고 싶은 연도",
        min_value=latest_year + 1,
        max_value=2100,
        value=latest_year + 1,
        step=1
    )

prediction_year = int(prediction_year)

st.divider()


# =====================================================
# 6. 선택한 월의 과거 데이터 추출
# =====================================================
monthly_data = raw_data[
    raw_data["월번호"] == selected_month
].copy()

monthly_data = (
    monthly_data
    .groupby("연도", as_index=False)["평균기온(℃)"]
    .mean()
)

monthly_data = monthly_data.sort_values(
    "연도"
).reset_index(drop=True)

if len(monthly_data) < 3:
    st.error("선택한 월의 데이터가 3개 연도 이상 있어야 예측할 수 있습니다.")
    st.stop()

x = monthly_data["연도"].to_numpy(dtype=float)
y = monthly_data["평균기온(℃)"].to_numpy(dtype=float)

target_x = float(prediction_year)


# =====================================================
# 7. 선형회귀
# =====================================================
def linear_regression(x, y):

    x_mean = np.mean(x)
    y_mean = np.mean(y)

    denominator = np.sum((x - x_mean) ** 2)

    if denominator == 0:
        slope = 0
    else:
        slope = np.sum(
            (x - x_mean) * (y - y_mean)
        ) / denominator

    intercept = y_mean - slope * x_mean

    def predict(new_x):
        new_x = np.asarray(new_x, dtype=float)
        return slope * new_x + intercept

    return predict


linear_predict = linear_regression(x, y)


# =====================================================
# 8. 다항회귀
# =====================================================
def polynomial_regression(x, y):

    x_mean = np.mean(x)
    x_std = np.std(x)

    if x_std == 0:
        x_std = 1

    z = (x - x_mean) / x_std

    matrix = np.column_stack([
        z ** 2,
        z,
        np.ones(len(z))
    ])

    coefficients, _, _, _ = np.linalg.lstsq(
        matrix,
        y,
        rcond=None
    )

    def predict(new_x):

        new_x = np.asarray(new_x, dtype=float)
        new_z = (new_x - x_mean) / x_std

        new_matrix = np.column_stack([
            new_z ** 2,
            new_z,
            np.ones(len(new_z))
        ])

        return new_matrix @ coefficients

    return predict


polynomial_predict = polynomial_regression(x, y)


# =====================================================
# 9. 의사결정나무 회귀
# =====================================================
def build_decision_tree(x, y, depth=0, max_depth=3, min_leaf=2):

    # 현재 노드의 평균값
    current_mean = float(np.mean(y))

    # 종료 조건
    if (
        depth >= max_depth
        or len(y) < min_leaf * 2
        or len(np.unique(x)) < 2
    ):
        return {
            "value": current_mean
        }

    best_error = float("inf")
    best_split = None

    sorted_x = np.sort(np.unique(x))

    # 후보 분할 지점
    split_points = (
        sorted_x[:-1] + sorted_x[1:]
    ) / 2

    for split in split_points:

        left_mask = x <= split
        right_mask = x > split

        if (
            np.sum(left_mask) < min_leaf
            or np.sum(right_mask) < min_leaf
        ):
            continue

        left_y = y[left_mask]
        right_y = y[right_mask]

        error = (
            np.sum((left_y - np.mean(left_y)) ** 2)
            + np.sum((right_y - np.mean(right_y)) ** 2)
        )

        if error < best_error:
            best_error = error
            best_split = split

    if best_split is None:
        return {
            "value": current_mean
        }

    left_mask = x <= best_split
    right_mask = x > best_split

    return {
        "split": float(best_split),
        "left": build_decision_tree(
            x[left_mask],
            y[left_mask],
            depth + 1,
            max_depth,
            min_leaf
        ),
        "right": build_decision_tree(
            x[right_mask],
            y[right_mask],
            depth + 1,
            max_depth,
            min_leaf
        )
    }


def predict_tree(tree, value):

    if "value" in tree:
        return tree["value"]

    if value <= tree["split"]:
        return predict_tree(tree["left"], value)

    return predict_tree(tree["right"], value)


def decision_tree_regression(x, y):

    min_leaf = max(
        2,
        math.ceil(len(x) * 0.03)
    )

    tree = build_decision_tree(
        x,
        y,
        max_depth=3,
        min_leaf=min_leaf
    )

    def predict(new_x):

        new_x = np.asarray(new_x, dtype=float)

        return np.array([
            predict_tree(tree, value)
            for value in new_x
        ])

    return predict


tree_predict = decision_tree_regression(x, y)


# =====================================================
# 10. 예측값 계산
# =====================================================
predictions = {
    "선형회귀": float(linear_predict([target_x])[0]),
    "다항회귀": float(polynomial_predict([target_x])[0]),
    "의사결정나무 회귀": float(tree_predict([target_x])[0])
}


# =====================================================
# 11. 결정계수 R² 계산
# =====================================================
def calculate_r2(actual, predicted):

    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    total_error = np.sum(
        (actual - np.mean(actual)) ** 2
    )

    residual_error = np.sum(
        (actual - predicted) ** 2
    )

    if total_error == 0:
        return 0.0

    return 1 - residual_error / total_error


fitted_values = {
    "선형회귀": linear_predict(x),
    "다항회귀": polynomial_predict(x),
    "의사결정나무 회귀": tree_predict(x)
}

r2_values = {
    name: calculate_r2(y, fitted)
    for name, fitted in fitted_values.items()
}


# =====================================================
# 12. 알고리즘 선택
# =====================================================
st.subheader("🧠 예측 알고리즘 선택")

selected_model = st.selectbox(
    "어떤 알고리즘으로 예측할까요?",
    [
        "선형회귀",
        "다항회귀",
        "의사결정나무 회귀"
    ]
)

selected_prediction = predictions[selected_model]
selected_r2 = r2_values[selected_model]


# =====================================================
# 13. 선택 알고리즘 예측 결과
# =====================================================
st.subheader("🔮 예측 결과")

result_col1, result_col2 = st.columns(2)

with result_col1:
    st.metric(
        label=f"{prediction_year}년 {month_names[selected_month]} 예상 평균기온",
        value=f"{selected_prediction:.2f}℃"
    )

with result_col2:
    st.metric(
        label="과거 데이터 결정계수 R²",
        value=f"{selected_r2:.3f}"
    )

st.caption(
    "※ R²는 과거 데이터에 모델을 적용했을 때의 설명력을 나타내며, "
    "미래 예측의 정확도를 보장하지는 않아요."
)


# =====================================================
# 14. 세 가지 알고리즘 예측값 비교
# =====================================================
st.subheader("📊 알고리즘별 예측 결과 비교")

comparison_data = pd.DataFrame({
    "알고리즘": list(predictions.keys()),
    "예측 평균기온(℃)": [
        predictions[name]
        for name in predictions
    ],
    "과거 데이터 R²": [
        r2_values[name]
        for name in predictions
    ]
})

st.dataframe(
    comparison_data,
    use_container_width=True,
    hide_index=True
)


# =====================================================
# 15. 그래프
# =====================================================
st.divider()
st.subheader("📈 과거 기온과 미래 예측 그래프")

model_colors = {
    "선형회귀": "#800080",
    "다항회귀": "#000080",
    "의사결정나무 회귀": "#FF1493"
}

# 실제 관측 데이터 점 색상: 민트색
actual_point_color = "#40E0D0"

grid_x = np.linspace(
    float(np.min(x)),
    target_x,
    400
)

fig = go.Figure()

# 실제 관측 데이터
fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        mode="markers",
        name="실제 관측 기온",
        marker=dict(
            color=actual_point_color,
            size=9,
            opacity=1,
            line=dict(
                color="#168F86",
                width=1
            )
        )
    )
)

# 세 가지 알고리즘 선
for model_name, predict_function in [
    ("선형회귀", linear_predict),
    ("다항회귀", polynomial_predict),
    ("의사결정나무 회귀", tree_predict)
]:

    line_width = 4 if model_name == selected_model else 2
    line_opacity = 1 if model_name == selected_model else 0.65

    fig.add_trace(
        go.Scatter(
            x=grid_x,
            y=predict_function(grid_x),
            mode="lines",
            name=model_name,
            line=dict(
                color=model_colors[model_name],
                width=line_width,
                shape=(
                    "hv"
                    if model_name == "의사결정나무 회귀"
                    else "linear"
                )
            ),
            opacity=line_opacity
        )
    )

# 선택된 알고리즘의 미래 예측 지점
fig.add_trace(
    go.Scatter(
        x=[prediction_year],
        y=[selected_prediction],
        mode="markers",
        name="선택한 알고리즘의 예측값",
        marker=dict(
            color=model_colors[selected_model],
            size=16,
            symbol="star",
            line=dict(
                color="white",
                width=1
            )
        )
    )
)

fig.update_layout(
    title=f"{month_names[selected_month]} 평균기온 변화와 {prediction_year}년 예측",
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    template="plotly_white",
    hovermode="x unified",
    height=600,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ),
    xaxis=dict(
        tickformat="d",
        showgrid=True
    ),
    yaxis=dict(
        showgrid=True
    )
)

fig.add_vline(
    x=prediction_year,
    line_dash="dash",
    line_color="#777777",
    annotation_text="예측 연도"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================================
# 16. 그래프 색상 설명
# =====================================================
st.markdown("### 🎨 그래프 색상 안내")

color_col1, color_col2, color_col3, color_col4 = st.columns(4)

with color_col1:
    st.markdown("🟢 **민트색 점**")
    st.caption("실제 관측된 기온")

with color_col2:
    st.markdown("🟣 **보라색 선**")
    st.caption("선형회귀")

with color_col3:
    st.markdown("🔵 **남색 선**")
    st.caption("다항회귀")

with color_col4:
    st.markdown("💗 **핑크색 선**")
    st.caption("의사결정나무 회귀")


# =====================================================
# 17. 알고리즘 설명
# =====================================================
st.divider()
st.subheader("📚 예측 알고리즘 알아보기")

with st.expander("1️⃣ 선형회귀란?"):

    st.write("""
    선형회귀는 과거 기온 데이터의 전체적인 증가 또는 감소 흐름을
    직선으로 나타내는 방법이에요.

    - 과거 데이터의 평균적인 변화 추세를 분석해요.
    - 계산이 간단하고 결과를 이해하기 쉬워요.
    - 장기적인 변화 방향을 살펴보는 데 활용할 수 있어요.
    """)

with st.expander("2️⃣ 다항회귀란?"):

    st.write("""
    다항회귀는 직선뿐만 아니라 곡선 형태로 데이터의 흐름을 표현해요.

    - 기온의 굴곡진 변화 패턴을 반영할 수 있어요.
    - 여기서는 2차 다항식을 사용했어요.
    - 과거 데이터에 지나치게 맞춰질 가능성도 있어요.
    """)

with st.expander("3️⃣ 의사결정나무 회귀란?"):

    st.write("""
    의사결정나무 회귀는 데이터를 여러 구간으로 나누고
    각 구간의 평균값을 이용해 예측하는 방법이에요.

    - 데이터의 구간별 특징을 반영해요.
    - 직선이나 곡선이 아닌 계단 형태의 결과가 나올 수 있어요.
    - 미래 연도가 과거 데이터의 범위를 벗어나면
      마지막 구간의 평균값이 유지될 수 있어요.
    """)


# =====================================================
# 18. 데이터 확인
# =====================================================
st.divider()

with st.expander("🗂️ 원본 기온 데이터 확인하기"):

    display_data = raw_data.copy()

    # ★ 중요: '월' 열을 먼저 확실하게 생성
    # 기존 오류처럼 없는 열을 불러오지 않도록 수정했어요.
    display_data["월번호"] = pd.to_numeric(
        display_data["월번호"],
        errors="coerce"
    )

    display_data["월"] = (
        display_data["월번호"]
        .map(month_names)
        .fillna("월 정보 없음")
    )

    display_data["연도"] = display_data["연도"].astype(int)

    # 화면에 보여줄 열을 새로 구성
    display_data = display_data[
        ["연도", "월", "평균기온(℃)"]
    ].copy()

    display_data = display_data.sort_values(
        ["연도", "월"]
    ).reset_index(drop=True)

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"총 {len(display_data):,}개의 월별 기온 데이터가 있어요."
    )


# =====================================================
# 19. 마무리 안내
# =====================================================
st.divider()

st.info("""
💡 **알아두기!**

기온은 장기적인 기후 변화뿐 아니라 자연적인 변동에도 영향을 받아요.
따라서 이 앱의 결과는 과거 데이터에 기반한 통계적 예측이며,
실제 미래 기온과 차이가 날 수 있어요.
""")
