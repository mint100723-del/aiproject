
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import re

# ==================================================
# 1. 페이지 설정
# ==================================================
st.set_page_config(
    page_title="서울 월별 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 평균기온 예측")
st.write(
    "원하는 월과 예측 연도를 선택하고 "
    "세 가지 회귀 알고리즘의 예측 결과를 비교해 봐!"
)

st.divider()


# ==================================================
# 2. CSV 데이터 불러오기
# ==================================================
@st.cache_data
def load_temperature_data():
    current_folder = Path(__file__).resolve().parent

    possible_paths = [
        current_folder / "temperature.csv",
        current_folder.parent / "temperature.csv",
        current_folder.parent / "temperature (1).csv"
    ]

    csv_path = None

    for path in possible_paths:
        if path.exists():
            csv_path = path
            break

    if csv_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다. "
            "프로젝트 최상위 폴더에 파일을 넣어 주세요."
        )

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
            f"CSV 파일을 읽을 수 없습니다: {last_error}"
        )

    required_columns = ["일시", "평균기온(℃)"]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                f"CSV 파일에 '{column}' 열이 없습니다.\n"
                f"현재 열 이름: {list(data.columns)}"
            )

    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    years = []
    months = []

    century = 1900
    previous_short_year = None

    for value in data["일시"].astype(str):
        value = value.strip()

        match = re.fullmatch(
            r"([A-Za-z]{3})-(\d{2})",
            value
        )

        if match:
            month_text = match.group(1).title()
            short_year = int(match.group(2))
            month_number = month_map.get(month_text)

            if month_number is None:
                years.append(np.nan)
                months.append(np.nan)
                continue

            # 99년 다음 00년으로 넘어갈 때 세기 변경
            if (
                previous_short_year is not None
                and short_year < previous_short_year
            ):
                century += 100

            years.append(century + short_year)
            months.append(month_number)

            previous_short_year = short_year

        else:
            # YYYY-MM 또는 YYYY-MM-DD 형식도 처리
            parsed_date = pd.to_datetime(
                value,
                errors="coerce"
            )

            if pd.isna(parsed_date):
                years.append(np.nan)
                months.append(np.nan)
            else:
                years.append(parsed_date.year)
                months.append(parsed_date.month)

    data["연도"] = years
    data["월"] = months

    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["연도", "월", "평균기온(℃)"]
    ).copy()

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    data = data[data["월"].between(1, 12)]

    data = data.sort_values(
        ["연도", "월"]
    ).reset_index(drop=True)

    if data.empty:
        raise ValueError("분석할 수 있는 기온 데이터가 없습니다.")

    return data


try:
    df = load_temperature_data()

except Exception as error:
    st.error(
        f"데이터를 불러오는 중 오류가 발생했습니다.\n\n{error}"
    )
    st.stop()


# ==================================================
# 3. 사용자 입력
# ==================================================
st.subheader("🔎 예측 조건 선택")

month_names = {
    1: "1월", 2: "2월", 3: "3월", 4: "4월",
    5: "5월", 6: "6월", 7: "7월", 8: "8월",
    9: "9월", 10: "10월", 11: "11월", 12: "12월"
}

latest_year = int(df["연도"].max())

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월",
        options=list(range(1, 13)),
        format_func=lambda x: month_names[x]
    )

with col2:
    prediction_year = st.number_input(
        "예측할 연도",
        min_value=latest_year + 1,
        max_value=2100,
        value=latest_year + 1,
        step=1
    )

st.info(
    f"📅 선택 조건: {month_names[selected_month]} "
    f"/ {int(prediction_year)}년"
)


# ==================================================
# 4. 선택한 월의 데이터 추출
# ==================================================
month_data = df[
    df["월"] == selected_month
].copy()

# 같은 연도에 데이터가 여러 개 있으면 평균으로 정리
month_data = (
    month_data.groupby("연도", as_index=False)
    ["평균기온(℃)"].mean()
)

month_data = month_data.sort_values("연도")

if len(month_data) < 3:
    st.error(
        "선택한 월의 데이터가 너무 적습니다. "
        "최소 3개 연도의 데이터가 필요합니다."
    )
    st.stop()

x = month_data["연도"].to_numpy(dtype=float)
y = month_data["평균기온(℃)"].to_numpy(dtype=float)

if len(np.unique(x)) < 3:
    st.error("서로 다른 연도가 최소 3개 필요합니다.")
    st.stop()


# ==================================================
# 5. 알고리즘 1: 선형회귀
# ==================================================
def linear_regression(x, y):
    x_mean = np.mean(x)
    y_mean = np.mean(y)

    denominator = np.sum((x - x_mean) ** 2)

    if denominator == 0:
        raise ValueError("선형회귀 계산에 필요한 데이터가 부족합니다.")

    slope = np.sum(
        (x - x_mean) * (y - y_mean)
    ) / denominator

    intercept = y_mean - slope * x_mean

    def predict(new_x):
        new_x = np.asarray(new_x, dtype=float)
        return slope * new_x + intercept

    return predict, slope, intercept


# ==================================================
# 6. 알고리즘 2: 2차 다항회귀
# ==================================================
def polynomial_regression(x, y):
    center = np.mean(x)
    scale = np.std(x)

    if scale == 0:
        raise ValueError("다항회귀 계산에 필요한 데이터가 부족합니다.")

    z = (x - center) / scale

    features = np.column_stack([
        z ** 2,
        z,
        np.ones(len(z))
    ])

    coefficients, _, _, _ = np.linalg.lstsq(
        features,
        y,
        rcond=None
    )

    def predict(new_x):
        new_x = np.asarray(new_x, dtype=float)
        new_z = (new_x - center) / scale

        new_features = np.column_stack([
            new_z ** 2,
            new_z,
            np.ones(len(new_z))
        ])

        return new_features @ coefficients

    return predict, coefficients, center, scale


# ==================================================
# 7. 알고리즘 3: 의사결정나무 회귀
# ==================================================
def decision_tree_regression(x, y, max_depth=3):
    min_samples_leaf = max(
        2,
        int(np.ceil(len(x) * 0.03))
    )

    def build_tree(x_values, y_values, depth):
        node = {
            "value": float(np.mean(y_values)),
            "threshold": None,
            "left": None,
            "right": None
        }

        if depth >= max_depth:
            return node

        if len(x_values) < min_samples_leaf * 2:
            return node

        order = np.argsort(x_values)
        sorted_x = x_values[order]
        sorted_y = y_values[order]

        parent_sse = np.sum(
            (sorted_y - np.mean(sorted_y)) ** 2
        )

        best_sse = parent_sse
        best_threshold = None

        for i in range(
            min_samples_leaf,
            len(sorted_x) - min_samples_leaf + 1
        ):
            if sorted_x[i - 1] == sorted_x[i]:
                continue

            left_y = sorted_y[:i]
            right_y = sorted_y[i:]

            left_sse = np.sum(
                (left_y - np.mean(left_y)) ** 2
            )

            right_sse = np.sum(
                (right_y - np.mean(right_y)) ** 2
            )

            total_sse = left_sse + right_sse

            if total_sse < best_sse:
                best_sse = total_sse
                best_threshold = (
                    sorted_x[i - 1] + sorted_x[i]
                ) / 2

        if best_threshold is None:
            return node

        left_mask = x_values <= best_threshold
        right_mask = x_values > best_threshold

        node["threshold"] = float(best_threshold)

        node["left"] = build_tree(
            x_values[left_mask],
            y_values[left_mask],
            depth + 1
        )

        node["right"] = build_tree(
            x_values[right_mask],
            y_values[right_mask],
            depth + 1
        )

        return node

    tree = build_tree(x, y, 0)

    def predict_one(value, node):
        if node["threshold"] is None:
            return node["value"]

        if value <= node["threshold"]:
            return predict_one(value, node["left"])

        return predict_one(value, node["right"])

    def predict(new_x):
        new_x = np.asarray(new_x, dtype=float)

        return np.array([
            predict_one(value, tree)
            for value in new_x
        ])

    return predict, tree


# ==================================================
# 8. 세 알고리즘 학습
# ==================================================
try:
    linear_predict, linear_slope, linear_intercept = (
        linear_regression(x, y)
    )

    poly_predict, poly_coef, poly_center, poly_scale = (
        polynomial_regression(x, y)
    )

    tree_predict, tree_model = decision_tree_regression(
        x,
        y,
        max_depth=3
    )

except Exception as error:
    st.error(f"회귀 알고리즘 계산 중 오류가 발생했습니다: {error}")
    st.stop()


# ==================================================
# 9. 알고리즘별 예측값 계산
# ==================================================
target_year = float(prediction_year)

predictions = {
    "선형회귀": float(linear_predict([target_year])[0]),
    "다항회귀": float(poly_predict([target_year])[0]),
    "의사결정나무 회귀": float(tree_predict([target_year])[0])
}

fitted_values = {
    "선형회귀": linear_predict(x),
    "다항회귀": poly_predict(x),
    "의사결정나무 회귀": tree_predict(x)
}


# ==================================================
# 10. 결정계수 R² 계산
# ==================================================
def calculate_r2(actual, predicted):
    ss_total = np.sum(
        (actual - np.mean(actual)) ** 2
    )

    ss_residual = np.sum(
        (actual - predicted) ** 2
    )

    if ss_total == 0:
        return 0.0

    return float(1 - ss_residual / ss_total)


r2_scores = {
    name: calculate_r2(y, values)
    for name, values in fitted_values.items()
}


# ==================================================
# 11. 알고리즘 색상 설정
# ==================================================
algorithm_names = [
    "선형회귀",
    "다항회귀",
    "의사결정나무 회귀"
]

# 요청한 색상: 자주색, 남색, 핑크색
model_colors = {
    "선형회귀": "#800080",
    "다항회귀": "#000080",
    "의사결정나무 회귀": "#FF1493"
}


# ==================================================
# 12. 알고리즘 선택
# ==================================================
st.divider()
st.subheader("🧠 회귀 알고리즘 선택")

selected_algorithm = st.selectbox(
    "사용할 예측 알고리즘을 선택해 줘!",
    options=algorithm_names,
    index=0
)

algorithm_descriptions = {
    "선형회귀": (
        "과거 기온 변화의 전체적인 방향을 직선으로 나타내는 방법이야."
    ),
    "다항회귀": (
        "기온 변화가 직선이 아니라 곡선 형태로 나타나는 경우를 "
        "표현할 수 있어. 이번 프로그램에서는 2차 곡선을 사용해."
    ),
    "의사결정나무 회귀": (
        "연도를 여러 구간으로 나누고 각 구간의 평균기온을 "
        "예측값으로 사용하는 방법이야."
    )
}

st.info(
    f"💡 **{selected_algorithm}**\n\n"
    f"{algorithm_descriptions[selected_algorithm]}"
)


# ==================================================
# 13. 예측 결과 표시
# ==================================================
st.divider()
st.subheader("🎯 알고리즘별 예측 결과")

selected_prediction = predictions[selected_algorithm]
selected_r2 = r2_scores[selected_algorithm]

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "선택한 알고리즘",
        selected_algorithm
    )

with c2:
    st.metric(
        "예측 평균기온",
        f"{selected_prediction:.2f} ℃"
    )

with c3:
    st.metric(
        "과거 데이터 결정계수 R²",
        f"{selected_r2:.3f}"
    )


# ==================================================
# 14. 세 알고리즘 비교표
# ==================================================
st.markdown("### 📋 세 가지 알고리즘 비교")

comparison_data = []

for name in algorithm_names:
    comparison_data.append({
        "알고리즘": name,
        "예측 평균기온(℃)": round(predictions[name], 2),
        "과거 데이터 R²": round(r2_scores[name], 3)
    })

comparison_df = pd.DataFrame(comparison_data)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)

difference = (
    max(predictions.values()) - min(predictions.values())
)

st.write(
    f"📊 세 알고리즘의 예측 기온 차이는 "
    f"**{difference:.2f}℃**야."
)


# ==================================================
# 15. 그래프 생성
# ==================================================
st.divider()
st.subheader("📈 과거 기온과 알고리즘별 예측 그래프")

grid_x = np.linspace(
    float(np.min(x)),
    target_year,
    400
)

model_functions = {
    "선형회귀": linear_predict,
    "다항회귀": poly_predict,
    "의사결정나무 회귀": tree_predict
}

fig = go.Figure()

# 실제 과거 기온 데이터: 회색 점
fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="#777777",
            size=8,
            opacity=0.75
        ),
        hovertemplate=(
            "%{x:.0f}년<br>"
            "실제 평균기온: %{y:.2f}℃"
            "<extra></extra>"
        )
    )
)

# 세 가지 알고리즘의 예측선
for name in algorithm_names:
    predicted_line = model_functions[name](grid_x)

    is_selected = name == selected_algorithm

    # 의사결정나무는 계단형 선으로 표시
    line_shape = (
        "hv"
        if name == "의사결정나무 회귀"
        else "linear"
    )

    fig.add_trace(
        go.Scatter(
            x=grid_x,
            y=predicted_line,
            mode="lines",
            name=name,
            line=dict(
                color=model_colors[name],
                width=4 if is_selected else 2.5,
                dash="solid" if is_selected else "dash",
                shape=line_shape
            ),
            opacity=1.0 if is_selected else 0.8,
            hovertemplate=(
                "%{x:.0f}년<br>"
                f"{name}: "
                "%{y:.2f}℃"
                "<extra></extra>"
            )
        )
    )

# 각 알고리즘의 최종 예측 지점
for name in algorithm_names:
    is_selected = name == selected_algorithm

    fig.add_trace(
        go.Scatter(
            x=[target_year],
            y=[predictions[name]],
            mode="markers+text",
            name=f"{name} 예측값",
            marker=dict(
                color=model_colors[name],
                size=16 if is_selected else 11,
                symbol="star" if is_selected else "circle"
            ),
            text=[
                f"{predictions[name]:.1f}℃"
                if is_selected else ""
            ],
            textposition="top center",
            showlegend=False,
            hovertemplate=(
                f"{name}<br>"
                "%{x:.0f}년<br>"
                "예측: %{y:.2f}℃"
                "<extra></extra>"
            )
        )
    )

fig.add_vline(
    x=target_year,
    line_width=1,
    line_dash="dot",
    line_color="#999999"
)

fig.update_layout(
    title=dict(
        text=(
            f"{month_names[selected_month]} 서울 평균기온 "
            f"알고리즘 비교"
        ),
        x=0.5
    ),
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    height=650,
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
        t=110,
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


# ==================================================
# 16. 그래프 범례 설명
# ==================================================
st.markdown("### 🧭 그래프 보는 방법")

st.markdown(
    """
    - ⚫ **회색 점:** CSV에 기록된 실제 과거 평균기온
    - 🟣 **자주색 선:** 선형회귀 예측 추세
    - 🔵 **남색 선:** 다항회귀 예측 추세
    - 💗 **핑크색 선:** 의사결정나무 회귀 예측 추세
    - ⭐ **별 모양:** 선택한 알고리즘의 최종 예측 기온

    선택한 알고리즘은 그래프에서 더 굵은 선으로 표시돼.
    """
)


# ==================================================
# 17. 알고리즘 설명
# ==================================================
st.divider()
st.subheader("📚 세 가지 회귀 알고리즘 알아보기")

with st.expander("1️⃣ 선형회귀 (Linear Regression)", expanded=True):
    st.markdown(
        """
        과거 데이터의 전체적인 변화 방향을 하나의 직선으로 표현해.

        1. 과거 연도와 평균기온을 점으로 표시해.
        2. 실제 점들과 직선 사이의 오차 제곱합이 작아지는 직선을 찾아.
        3. 입력한 연도를 직선에 대입해 예측 기온을 계산해.

        **특징:** 전체적인 상승 또는 하락 추세를 파악하기 좋아.
        """
    )

    st.latex(r"\hat{y}=ax+b")

    st.write(
        f"이번 선택 조건의 기울기: {linear_slope:.5f}"
    )


with st.expander("2️⃣ 다항회귀 (Polynomial Regression)"):
    st.markdown(
        """
        다항회귀는 직선이 아닌 곡선 형태로 데이터의 관계를 표현해.

        이번 프로그램에서는 2차 다항회귀를 사용했어.

        1. 연도 데이터를 표준화해.
        2. 연도의 제곱 항을 추가해.
        3. 과거 기온의 곡선 형태를 계산해.
        4. 입력한 연도의 기온을 예측해.

        **특징:** 기온 변화가 직선 형태가 아닐 때 곡선으로 추세를 표현할 수 있어.
        """
    )

    st.latex(r"\hat{y}=az^2+bz+c")

    st.write(
        "z는 계산하기 쉽도록 표준화한 연도야."
    )


with st.expander("3️⃣ 의사결정나무 회귀 (Decision Tree Regression)"):
    st.markdown(
        """
        의사결정나무 회귀는 데이터를 여러 구간으로 나누고
        각 구간의 평균값을 예측하는 알고리즘이야.

        1. 연도 데이터를 여러 구간으로 나눌 기준을 찾아.
        2. 각 구간의 기온이 서로 비슷하도록 분할해.
        3. 새로운 연도가 속한 구간의 평균기온을 예측값으로 사용해.

        **특징:** 직선이나 곡선이 아닌 계단 형태의 예측선을 만들 수 있어.

        미래 연도가 과거의 마지막 구간에 속하면 그 구간의 평균값을
        예측한다는 점도 기억해 줘.
        """
    )


# ==================================================
# 18. 계산 결과 확인
# ==================================================
with st.expander("🧮 알고리즘 계산 결과 자세히 보기"):
    st.write("**선형회귀 계산식**")

    st.code(
        f"y = {linear_slope:.6f} × 연도 "
        f"+ ({linear_intercept:.6f})",
        language="text"
    )

    st.write("**다항회귀 계산 계수**")

    st.code(
        f"2차 계수: {poly_coef[0]:.6f}\n"
        f"1차 계수: {poly_coef[1]:.6f}\n"
        f"상수항: {poly_coef[2]:.6f}",
        language="text"
    )

    st.write("**의사결정나무 회귀 설정**")

    st.write(
        "- 최대 깊이: 3\n"
        f"- 최소 잎 노드 데이터 수: "
        f"{max(2, int(np.ceil(len(x) * 0.03)))}개"
    )


# ==================================================
# 19. 알고리즘 비교 시 주의점
# ==================================================
st.divider()
st.subheader("💡 알고리즘을 비교할 때 알아둘 점")

st.markdown(
    """
    **결정계수 R²**는 각 알고리즘이 과거 데이터의 변화를
    얼마나 설명하는지 보여주는 지표야.

    - 1에 가까우면 과거 데이터의 설명력이 높은 편이야.
    - 0에 가까우면 직선이나 곡선이 과거 데이터의 변화를 잘 설명하지 못해.
    - 음수가 나올 수도 있어.

    하지만 R²가 가장 높은 알고리즘이 미래 기온도 반드시
    가장 정확하게 예측한다는 뜻은 아니야.

    특히 다항회귀는 먼 미래로 갈수록 곡선이 크게 휘어질 수 있고,
    의사결정나무는 과거 마지막 구간의 평균값을 유지하는 경향이 있어.

    세 알고리즘의 예측값이 왜 다른지 그래프와 함께 비교해 보는 것이 중요해!
    """
)


# ==================================================
# 20. 실제 데이터 확인
# ==================================================
with st.expander("📋 선택한 월의 과거 데이터 확인하기"):
    display_data = month_data.copy()

    display_data["월"] = display_data["월"].map(
        month_names
    )

    display_data = display_data.rename(
        columns={
            "연도": "연도",
            "월": "월",
            "평균기온(℃)": "평균기온 (℃)"
        }
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "자료: temperature.csv | "
    "알고리즘: 선형회귀, 2차 다항회귀, 의사결정나무 회귀"
)
