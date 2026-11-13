
import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from matplotlib.colors import ListedColormap
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="아이리스 꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 아이리스 꽃 품종 예측 프로그램")
st.write(
    "꽃잎의 길이와 너비를 입력하고 "
    "3가지 인공지능 분류 알고리즘으로 꽃의 품종을 예측해 보자!"
)

# =====================================
# 2. 데이터 불러오기
# =====================================
@st.cache_data
def load_data():
    file_path = "Iris11.csv"

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            "Iris11.csv 파일이 app.py와 같은 폴더에 있는지 확인해 주세요."
        )

    df = None

    for encoding in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError("CSV 파일의 인코딩을 읽을 수 없습니다.")

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
    )

    # 한글/영문 열 이름 모두 인식
    aliases = {
        "꽃잎 길이": [
            "꽃잎 길이", "petal_length",
            "PetalLengthCm", "Petal Length"
        ],
        "꽃잎 너비": [
            "꽃잎 너비", "petal_width",
            "PetalWidthCm", "Petal Width"
        ],
        "품종": [
            "품종", "species", "variety", "Species"
        ]
    }

    rename_dict = {}

    for standard_name, possible_names in aliases.items():
        for name in possible_names:
            if name in df.columns:
                rename_dict[name] = standard_name
                break

    df = df.rename(columns=rename_dict)

    required = ["꽃잎 길이", "꽃잎 너비", "품종"]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(
            "CSV 파일에서 필요한 열을 찾지 못했습니다: "
            + ", ".join(missing)
            + "\n필요한 열: 꽃잎 길이, 꽃잎 너비, 품종"
        )

    df = df[required].copy()

    df["꽃잎 길이"] = pd.to_numeric(
        df["꽃잎 길이"], errors="coerce"
    )
    df["꽃잎 너비"] = pd.to_numeric(
        df["꽃잎 너비"], errors="coerce"
    )

    df["품종"] = df["품종"].astype(str).str.strip()

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    df = df[df["품종"] != ""]

    if len(df) < 5:
        raise ValueError("분석할 데이터가 5개 이상 필요합니다.")

    if df["품종"].nunique() < 2:
        raise ValueError("품종 종류가 2개 이상 있어야 합니다.")

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했어요: {e}")
    st.stop()


# =====================================
# 3. 데이터와 색상 설정
# =====================================
X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

species_colors = {
    "setosa": "#F4A6C1",
    "versicolor": "#8FA8D8",
    "virginica": "#9575CD"
}

def get_species_color(species):
    name = str(species).lower()

    for key, color in species_colors.items():
        if key in name:
            return color

    return "#B0BEC5"


# =====================================
# 4. 알고리즘 선택
# =====================================
st.divider()
st.subheader("🤖 분류 알고리즘 선택")

algorithm_name = st.selectbox(
    "사용할 분류 알고리즘을 선택해 줘!",
    [
        "KNN (K-최근접 이웃)",
        "의사결정나무 (Decision Tree)",
        "랜덤 포레스트 (Random Forest)"
    ]
)

# =====================================
# 5. 알고리즘 설명
# =====================================
st.subheader("📚 알고리즘 알아보기")

with st.expander("① KNN (K-최근접 이웃) 설명"):
    st.write("""
    **KNN은 주변에 있는 데이터와 비교하는 알고리즘이야.**

    - 입력한 꽃과 가장 가까운 데이터 5개를 찾는다.
    - 가까운 데이터들의 품종을 확인한다.
    - 가장 많이 등장한 품종으로 최종 분류한다.

    예를 들어 주변의 5개 꽃 중 4개가 Setosa라면
    Setosa로 예측하는 방식이야.

    **특징:** 원리가 직관적이고 이해하기 쉬워.
    """)

with st.expander("② 의사결정나무 (Decision Tree) 설명"):
    st.write("""
    **의사결정나무는 여러 가지 질문을 통해 답을 찾아가는 알고리즘이야.**

    - 꽃잎 길이가 특정 값보다 긴지 확인한다.
    - 꽃잎 너비가 특정 값보다 큰지 확인한다.
    - 이런 조건을 따라가며 품종을 분류한다.

    마치 스무고개처럼 질문을 하나씩 거치면서
    최종 품종을 결정하는 방식이야.

    **특징:** 어떤 기준으로 분류했는지 이해하기 쉬워.
    """)

with st.expander("③ 랜덤 포레스트 (Random Forest) 설명"):
    st.write("""
    **랜덤 포레스트는 여러 개의 의사결정나무를 함께 사용하는 알고리즘이야.**

    - 여러 개의 의사결정나무를 만든다.
    - 각 나무가 독립적으로 품종을 예측한다.
    - 여러 나무의 예측 결과를 모아 최종 품종을 결정한다.

    한 그루의 나무가 아니라 여러 나무의 의견을
    종합하는 방식이라고 생각하면 돼.

    **특징:** 여러 나무의 결과를 종합해 예측을 안정적으로 만들 수 있어.
    """)


# =====================================
# 6. 모델 생성
# =====================================
models = {
    "KNN (K-최근접 이웃)": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", KNeighborsClassifier(n_neighbors=5))
    ]),

    "의사결정나무 (Decision Tree)": DecisionTreeClassifier(
        random_state=42,
        max_depth=5
    ),

    "랜덤 포레스트 (Random Forest)": RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        max_depth=5
    )
}

model = models[algorithm_name]

try:
    model.fit(X, y)
except Exception as e:
    st.error(f"모델 학습 중 오류가 발생했습니다: {e}")
    st.stop()


# =====================================
# 7. 사용자 입력
# =====================================
st.divider()
st.subheader("✏️ 꽃잎 정보 입력하기")

length_min = max(0.0, float(X["꽃잎 길이"].min()) - 1.0)
length_max = float(X["꽃잎 길이"].max()) + 2.0

width_min = max(0.0, float(X["꽃잎 너비"].min()) - 1.0)
width_max = float(X["꽃잎 너비"].max()) + 2.0

default_length = float(
    round(X["꽃잎 길이"].median(), 1)
)
default_width = float(
    round(X["꽃잎 너비"].median(), 1)
)

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=default_length,
        step=0.1
    )

with col2:
    petal_width = st.number_input(
        "🌷 꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=default_width,
        step=0.1
    )

input_data = pd.DataFrame({
    "꽃잎 길이": [petal_length],
    "꽃잎 너비": [petal_width]
})


# =====================================
# 8. 예측 결과
# =====================================
try:
    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    class_names = model.classes_
except Exception as e:
    st.error(f"품종 예측 중 오류가 발생했습니다: {e}")
    st.stop()

result_color = get_species_color(prediction)

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
        <div style="font-size:20px;">🌼 선택한 알고리즘</div>
        <div style="font-size:18px; margin:8px;">
            {algorithm_name}
        </div>
        <div style="font-size:20px;">예측된 꽃 품종</div>
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


# =====================================
# 9. 예측 확률
# =====================================
st.subheader("📈 품종별 예측 확률")

probability_df = pd.DataFrame({
    "품종": class_names,
    "예측 확률": probabilities
})

fig_prob, ax_prob = plt.subplots(figsize=(8, 4))

bar_colors = [
    get_species_color(name) for name in class_names
]

ax_prob.bar(
    probability_df["품종"],
    probability_df["예측 확률"] * 100,
    color=bar_colors,
    edgecolor="white"
)

ax_prob.set_ylabel("예측 확률 (%)")
ax_prob.set_ylim(0, 105)
ax_prob.set_title("Species Prediction Probability")
ax_prob.grid(axis="y", alpha=0.2)

for i, value in enumerate(probabilities):
    ax_prob.text(
        i,
        value * 100 + 2,
        f"{value * 100:.1f}%",
        ha="center"
    )

plt.tight_layout()
st.pyplot(fig_prob)
plt.close(fig_prob)


# =====================================
# 10. 최근접 이웃 5개 계산
# =====================================
# 최근접 이웃은 그래프에서 참고용으로 표시
neighbor_scaler = StandardScaler()
scaled_X = neighbor_scaler.fit_transform(X)
scaled_input = neighbor_scaler.transform(input_data)

distances = np.sqrt(
    np.sum((scaled_X - scaled_input[0]) ** 2, axis=1)
)

nearest_indices = np.argsort(distances)[:5]

nearest_data = df.iloc[nearest_indices].copy()
nearest_data["거리"] = distances[nearest_indices]
nearest_data = nearest_data.sort_values("거리")

vote_counts = nearest_data["품종"].value_counts()


# =====================================
# 11. 예측 이유
# =====================================
st.divider()
st.subheader("💡 예측 결과 이해하기")

if algorithm_name == "KNN (K-최근접 이웃)":
    st.write(
        "선택한 KNN 알고리즘은 가장 가까운 데이터 5개를 비교해서 "
        "품종을 예측했어."
    )

    for species, count in vote_counts.items():
        st.write(f"- **{species}**: {count}개")

elif algorithm_name == "의사결정나무 (Decision Tree)":
    st.write(
        "선택한 의사결정나무는 꽃잎 길이와 너비의 조건을 "
        "따라가면서 품종을 예측했어."
    )

    st.write(
        "각 조건에 따라 데이터가 나뉘고, "
        "마지막 단계에서 가장 적합한 품종을 결정해."
    )

elif algorithm_name == "랜덤 포레스트 (Random Forest)":
    st.write(
        "선택한 랜덤 포레스트는 여러 개의 의사결정나무가 "
        "각각 예측한 결과를 종합해서 품종을 결정했어."
    )

    st.write(
        "여러 나무의 예측 확률을 종합해 "
        "가장 높은 확률을 가진 품종을 선택한 거야."
    )

st.success(
    f"🌼 최종 예측 결과는 {prediction} 이야!"
)


# =====================================
# 12. 그래프
# =====================================
st.divider()
st.subheader("📊 꽃잎 길이와 너비에 따른 품종 분포")

fig, ax = plt.subplots(figsize=(12, 7))

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

class_list = list(model.classes_)

Z_numeric = np.array([
    class_list.index(value) for value in Z
]).reshape(xx.shape)

region_colors = [
    get_species_color(name) for name in class_list
]

light_colors = []

for color in region_colors:
    rgb = np.array(mcolors.to_rgb(color))
    light_rgb = rgb * 0.22 + np.array([1, 1, 1]) * 0.78
    light_colors.append(light_rgb)

cmap = ListedColormap(light_colors)

ax.contourf(
    xx,
    yy,
    Z_numeric,
    alpha=0.4,
    cmap=cmap,
    levels=np.arange(len(class_list) + 1) - 0.5
)

# 실제 품종별 데이터 별표
for species in y.unique():
    subset = df[df["품종"] == species]

    ax.scatter(
        subset["꽃잎 길이"],
        subset["꽃잎 너비"],
        color=get_species_color(species),
        marker="*",
        s=110,
        edgecolors="white",
        linewidths=0.5,
        alpha=0.9
    )

# 최근접 이웃 5개: 민트색 원
ax.scatter(
    nearest_data["꽃잎 길이"],
    nearest_data["꽃잎 너비"],
    s=260,
    facecolors="none",
    edgecolors="#40E0D0",
    linewidths=2.8,
    marker="o",
    zorder=8
)

# 사용자 입력: 골드 옐로우 별표
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
    algorithm_name + " - Iris Classification",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.grid(alpha=0.2)

# 별도의 색상 범례는 표시하지 않음
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)


# =====================================
# 13. 최근접 이웃 데이터 표
# =====================================
st.divider()
st.subheader("🔎 입력한 꽃과 가까운 데이터 5개")

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

st.caption(
    "※ 최근접 이웃 5개는 선택한 알고리즘과 관계없이 "
    "입력한 꽃과 가까운 실제 데이터를 참고용으로 보여 줍니다."
)

st.divider()
st.caption("🌸 아이리스 데이터 분류 학습 프로그램")
