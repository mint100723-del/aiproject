
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
import os

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="아이리스 꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 아이리스 꽃 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하면 어떤 품종인지 예측해 줄게!")

# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    file_path = "Iris11.csv"

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            "Iris11.csv 파일을 app.py와 같은 폴더에 넣어 주세요."
        )

    encodings = ["cp949", "utf-8-sig", "utf-8"]
    df = None

    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError("CSV 파일 인코딩을 읽을 수 없습니다.")

    df.columns = df.columns.astype(str).str.strip()

    required_columns = ["꽃잎 길이", "꽃잎 너비", "품종"]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV 파일에 다음 열이 필요합니다: "
            + ", ".join(missing_columns)
        )

    df = df[required_columns].copy()

    df["꽃잎 길이"] = pd.to_numeric(
        df["꽃잎 길이"], errors="coerce"
    )
    df["꽃잎 너비"] = pd.to_numeric(
        df["꽃잎 너비"], errors="coerce"
    )

    df = df.dropna()

    if len(df) < 5:
        raise ValueError("분석할 데이터가 5개 이상 필요합니다.")

    if df["품종"].nunique() < 2:
        raise ValueError("품종 데이터가 2종류 이상 필요합니다.")

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 문제가 발생했어요: {e}")
    st.stop()

# -----------------------------
# 데이터와 모델 설정
# -----------------------------
X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"].astype(str)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5))
])

model.fit(X, y)

# 품종별 그래프 색상
species_colors = {
    "Setosa": "#F4A6C1",
    "Versicolor": "#8FA8D8",
    "Virginica": "#9575CD"
}

# 데이터에 다른 품종 이름이 있어도 그래프가 작동하도록 처리
for species in y.unique():
    if species not in species_colors:
        species_colors[species] = "#B0BEC5"

# -----------------------------
# 사용자 입력
# -----------------------------
st.subheader("✏️ 꽃잎 정보 입력하기")

col1, col2 = st.columns(2)

petal_length_min = float(X["꽃잎 길이"].min())
petal_length_max = float(X["꽃잎 길이"].max())
petal_width_min = float(X["꽃잎 너비"].min())
petal_width_max = float(X["꽃잎 너비"].max())

with col1:
    petal_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=0.0,
        max_value=max(10.0, petal_length_max + 2.0),
        value=float(round(
            (petal_length_min + petal_length_max) / 2, 1
        )),
        step=0.1
    )

with col2:
    petal_width = st.number_input(
        "🌷 꽃잎 너비 (cm)",
        min_value=0.0,
        max_value=max(5.0, petal_width_max + 2.0),
        value=float(round(
            (petal_width_min + petal_width_max) / 2, 1
        )),
        step=0.1
    )

input_data = pd.DataFrame({
    "꽃잎 길이": [petal_length],
    "꽃잎 너비": [petal_width]
})

# -----------------------------
# 품종 예측
# -----------------------------
prediction = model.predict(input_data)[0]
probabilities = model.predict_proba(input_data)[0]
class_names = model.named_steps["knn"].classes_

result_color = species_colors.get(prediction, "#B0BEC5")

st.divider()
st.subheader("🔍 예측 결과")

st.markdown(
    f"""
    <div style="
        background-color:#FFF8E7;
        padding:25px;
        border-radius:15px;
        text-align:center;
        border:2px solid #F4C542;
    ">
        <div style="font-size:20px;">🌼 예측된 꽃 품종</div>
        <div style="
            font-size:36px;
            font-weight:bold;
            color:{result_color};
            margin-top:8px;
        ">{prediction}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 최근접 이웃 5개 찾기
# -----------------------------
scaler = model.named_steps["scaler"]
knn = model.named_steps["knn"]

scaled_input = scaler.transform(input_data)
scaled_X = scaler.transform(X)

distances, indices = knn.kneighbors(scaled_input)

nearest_indices = indices[0]
nearest_distances = distances[0]

nearest_data = df.iloc[nearest_indices].copy()
nearest_data["거리"] = nearest_distances
nearest_data = nearest_data.reset_index(drop=True)

# 최근접 이웃 품종별 투표 수
vote_counts = nearest_data["품종"].value_counts()

# -----------------------------
# 예측 이유 설명
# -----------------------------
st.subheader("💡 왜 이 품종으로 예측했을까?")

st.write(
    "KNN 알고리즘은 입력한 꽃과 가장 비슷한 데이터 5개를 찾고, "
    "가장 많이 등장한 품종을 예측 결과로 선택해."
)

for species, count in vote_counts.items():
    st.write(f"- **{species}**: {count}표")

st.success(
    f"가장 가까운 데이터 5개 중 "
    f"{prediction} 품종이 가장 많이 나타나서 "
    f"{prediction}으로 예측했어!"
)

# -----------------------------
# 그래프
# -----------------------------
st.divider()
st.subheader("📊 꽃잎 길이와 너비에 따른 품종 분포")

fig, ax = plt.subplots(figsize=(12, 7))

# 그래프 배경의 예측 영역
x_min = min(float(X["꽃잎 길이"].min()), petal_length) - 0.5
x_max = max(float(X["꽃잎 길이"].max()), petal_length) + 0.5
y_min = min(float(X["꽃잎 너비"].min()), petal_width) - 0.5
y_max = max(float(X["꽃잎 너비"].max()), petal_width) + 0.5

xx, yy = np.meshgrid(
    np.linspace(x_min, x_max, 180),
    np.linspace(y_min, y_max, 180)
)

grid_data = pd.DataFrame({
    "꽃잎 길이": xx.ravel(),
    "꽃잎 너비": yy.ravel()
})

Z = model.predict(grid_data)

class_list = list(model.named_steps["knn"].classes_)
Z_numeric = np.array([
    class_list.index(value) for value in Z
]).reshape(xx.shape)

region_colors = [
    species_colors.get(name, "#B0BEC5")
    for name in class_list
]

light_colors = []
for color in region_colors:
    import matplotlib.colors as mcolors
    rgb = np.array(mcolors.to_rgb(color))
    light_rgb = rgb * 0.22 + np.array([1, 1, 1]) * 0.78
    light_colors.append(light_rgb)

cmap = ListedColormap(light_colors)

ax.contourf(
    xx,
    yy,
    Z_numeric,
    alpha=0.35,
    cmap=cmap,
    levels=np.arange(len(class_list) + 1) - 0.5
)

# 품종별 실제 데이터
for species in y.unique():
    subset = df[df["품종"].astype(str) == species]

    ax.scatter(
        subset["꽃잎 길이"],
        subset["꽃잎 너비"],
        color=species_colors[species],
        marker="*",
        s=110,
        alpha=0.85,
        edgecolors="white",
        linewidths=0.5
    )

# 최근접 이웃 5개: 민트색 원
ax.scatter(
    nearest_data["꽃잎 길이"],
    nearest_data["꽃잎 너비"],
    s=260,
    facecolors="none",
    edgecolors="#40E0D0",
    linewidths=2.8,
    marker="o"
)

# 사용자 입력: 노란색 별
ax.scatter(
    petal_length,
    petal_width,
    color="#F4C542",
    edgecolors="#A87900",
    linewidths=2,
    marker="*",
    s=550,
    zorder=10
)

ax.set_xlabel("Petal Length (cm)", fontsize=13)
ax.set_ylabel("Petal Width (cm)", fontsize=13)
ax.set_title(
    "Iris Species Classification",
    fontsize=17,
    fontweight="bold"
)

ax.grid(alpha=0.2)
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

# 범례 문구를 따로 표시하지 않음
ax.legend_.remove() if ax.get_legend() else None

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

# -----------------------------
# 최근접 이웃 데이터 표
# -----------------------------
st.divider()
st.subheader("🔎 가장 가까운 데이터 5개")

st.dataframe(
    nearest_data[
        ["꽃잎 길이", "꽃잎 너비", "품종", "거리"]
    ].style.format({
        "꽃잎 길이": "{:.2f}",
        "꽃잎 너비": "{:.2f}",
        "거리": "{:.3f}"
    }),
    use_container_width=True
)

# -----------------------------
# 품종별 예측 확률
# -----------------------------
st.subheader("📈 품종별 예측 확률")

probability_df = pd.DataFrame({
    "품종": class_names,
    "예측 확률": probabilities
})

st.bar_chart(
    probability_df.set_index("품종")
)

st.caption(
    "※ KNN 알고리즘은 입력한 값과 가까운 데이터 5개를 "
    "기준으로 품종을 예측합니다."
)
