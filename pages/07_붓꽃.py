
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.colors import ListedColormap
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="붓꽃 AI 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 AI 품종 예측 프로그램")
st.write("꽃잎 길이와 너비를 입력하면 AI가 품종을 예측해 줘!")

st.divider()

# ==========================================
# 2. 데이터 불러오기
# ==========================================
@st.cache_data
def load_data():

    required = ["꽃잎 길이", "꽃잎 너비", "품종"]
    df = None

    for encoding in ["cp949", "utf-8-sig", "utf-8"]:

        try:
            temp = pd.read_csv(
                "Iris11.csv",
                encoding=encoding
            )

            # 컬럼명 앞뒤 공백 제거
            temp.columns = temp.columns.astype(str).str.strip()

            if all(col in temp.columns for col in required):
                df = temp
                break

        except (UnicodeDecodeError, pd.errors.ParserError):
            continue

    if df is None:
        raise ValueError(
            "Iris11.csv 파일을 읽을 수 없어. "
            "파일 이름과 컬럼명을 확인해 줘."
        )

    df = df[required].copy()

    df["꽃잎 길이"] = pd.to_numeric(
        df["꽃잎 길이"], errors="coerce"
    )

    df["꽃잎 너비"] = pd.to_numeric(
        df["꽃잎 너비"], errors="coerce"
    )

    df["품종"] = df["품종"].astype("string").str.strip()

    df = df.dropna()

    if len(df) < 5:
        raise ValueError("학습 데이터가 5개 미만이야.")

    if df["품종"].nunique() < 2:
        raise ValueError("품종은 최소 2종류 이상 필요해.")

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()

# ==========================================
# 3. 색상 설정
# ==========================================

# 기존 붓꽃 품종 색상
species_colors = {
    "Iris-setosa": "#F4A6C1",
    "Iris-versicolor": "#8FA8D8",
    "Iris-virginica": "#9575CD"
}

# 품종 한글 이름
korean_names = {
    "Iris-setosa": "세토사",
    "Iris-versicolor": "버시컬러",
    "Iris-virginica": "버지니카"
}

species_list = sorted(df["품종"].unique())

extra_colors = [
    "#F4A6C1",
    "#8FA8D8",
    "#9575CD"
]

colors = {}

for i, species in enumerate(species_list):
    colors[species] = species_colors.get(
        species,
        extra_colors[i % len(extra_colors)]
    )

# 사용자 입력 별 색상: 크리스마스 골드
INPUT_COLOR = "#F4C542"

# 최근접 이웃 원 색상: 민트
NEIGHBOR_COLOR = "#40E0D0"

# ==========================================
# 4. 입력 범위 계산
# ==========================================
length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())

width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())

# ==========================================
# 5. 입력 범위 안내
# ==========================================
st.subheader("📏 꽃잎 측정값 입력 범위")

col1, col2, col3 = st.columns(3)

col1.metric(
    "🌷 꽃잎 길이",
    f"{length_min:.1f} ~ {length_max:.1f} cm"
)

col2.metric(
    "🌷 꽃잎 너비",
    f"{width_min:.1f} ~ {width_max:.1f} cm"
)

col3.metric(
    "📊 학습 데이터",
    f"{len(df)}개"
)

st.info(
    "위 범위는 CSV 파일의 실제 최솟값과 최댓값이야. "
    "범위 안에서 입력해 줘!"
)

st.divider()

# ==========================================
# 6. KNN 모델 학습
# ==========================================

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# 표준화 + 최근접 이웃 5개
model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5))
])

model.fit(X, y)

# ==========================================
# 7. 사용자 입력
# ==========================================
st.subheader("✏️ 꽃잎 크기 입력하기")

default_length = round(
    (length_min + length_max) / 2, 1
)

default_width = round(
    (width_min + width_max) / 2, 1
)

with st.form("iris_form"):

    col1, col2 = st.columns(2)

    with col1:
        petal_length = st.number_input(
            "🌸 꽃잎 길이 (cm)",
            min_value=length_min,
            max_value=length_max,
            value=default_length,
            step=0.1,
            format="%.1f"
        )

    with col2:
        petal_width = st.number_input(
            "🌸 꽃잎 너비 (cm)",
            min_value=width_min,
            max_value=width_max,
            value=default_width,
            step=0.1,
            format="%.1f"
        )

    submitted = st.form_submit_button(
        "🔍 AI 품종 예측하기",
        use_container_width=True
    )

# ==========================================
# 8. 예측 실행
# ==========================================
if submitted:

    input_data = pd.DataFrame({
        "꽃잎 길이": [petal_length],
        "꽃잎 너비": [petal_width]
    })

    # 품종 예측
    prediction = model.predict(input_data)[0]

    # 최근접 이웃 5개 찾기
    scaler = model.named_steps["scaler"]

    distances, indices = model.named_steps["knn"].kneighbors(
        scaler.transform(input_data),
        n_neighbors=5
    )

    nearest = df.iloc[indices[0]].copy()
    nearest["거리"] = distances[0]

    votes = nearest["품종"].value_counts()

    result_name = korean_names.get(
        prediction, prediction
    )

    st.divider()

    # ======================================
    # 9. 예측 결과
    # ======================================
    st.subheader("🏆 AI 예측 결과")

    st.success("품종 예측이 완료되었어!")

    st.markdown(
        f"""
        <div style="
            background-color:#FFF8E1;
            border:2px solid #F4C542;
            border-radius:18px;
            padding:25px;
            text-align:center;
        ">
            <h2 style="color:#9A7200;">
                🌸 예측된 붓꽃 품종
            </h2>
            <h1 style="color:#805F00;">
                {result_name}
            </h1>
            <p style="color:#9A7200;">
                {prediction}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    c1, c2 = st.columns(2)

    c1.metric(
        "입력한 꽃잎 길이",
        f"{petal_length:.1f} cm"
    )

    c2.metric(
        "입력한 꽃잎 너비",
        f"{petal_width:.1f} cm"
    )

    st.divider()

    # ======================================
    # 10. 그래프 시각화
    # ======================================
    st.subheader("📊 붓꽃 품종 분류 그래프")

    st.write(
        "가로축은 꽃잎 길이, 세로축은 꽃잎 너비야. "
        "크리스마스 골드 별이 네가 입력한 값이야!"
    )

    x_range = length_max - length_min
    y_range = width_max - width_min

    x_pad = max(x_range * 0.08, 0.1)
    y_pad = max(y_range * 0.08, 0.1)

    x_values = np.linspace(
        length_min - x_pad,
        length_max + x_pad,
        250
    )

    y_values = np.linspace(
        width_min - y_pad,
        width_max + y_pad,
        200
    )

    xx, yy = np.meshgrid(x_values, y_values)

    grid_data = pd.DataFrame({
        "꽃잎 길이": xx.ravel(),
        "꽃잎 너비": yy.ravel()
    })

    # 그래프 배경의 품종 분류
    grid_prediction = model.predict(grid_data)

    class_to_num = {
        species: i
        for i, species in enumerate(species_list)
    }

    Z = np.array([
        class_to_num[value]
        for value in grid_prediction
    ]).reshape(xx.shape)

    fig, ax = plt.subplots(figsize=(12, 7))

    background_cmap = ListedColormap([
        colors[species] for species in species_list
    ])

    ax.contourf(
        xx,
        yy,
        Z,
        levels=np.arange(len(species_list) + 1) - 0.5,
        cmap=background_cmap,
        alpha=0.20
    )

    # 기존 데이터: 품종별 별
    for species in species_list:

        subset = df[df["품종"] == species]

        ax.scatter(
            subset["꽃잎 길이"],
            subset["꽃잎 너비"],
            color=colors[species],
            marker="*",
            s=110,
            alpha=0.9,
            edgecolors="white",
            linewidths=0.5,
            label=korean_names.get(species, species),
            zorder=3
        )

    # 최근접 이웃 5개: 민트색 원
    ax.scatter(
        nearest["꽃잎 길이"],
        nearest["꽃잎 너비"],
        marker="o",
        s=260,
        facecolors="none",
        edgecolors=NEIGHBOR_COLOR,
        linewidths=3,
        label="Nearest 5 Neighbors",
        zorder=6
    )

    # ======================================
    # 사용자 입력값: 크리스마스 골드 별
    # ======================================
    ax.scatter(
        petal_length,
        petal_width,
        marker="*",
        s=550,
        color=INPUT_COLOR,
        edgecolors="#A87900",
        linewidths=1.8,
        label="Your Input",
        zorder=10
    )

    ax.annotate(
        "YOUR INPUT ★",
        xy=(petal_length, petal_width),
        xytext=(13, 15),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
        color="#805F00",
        bbox=dict(
            boxstyle="round,pad=0.4",
            fc="#FFF8E1",
            ec=INPUT_COLOR,
            alpha=0.95
        )
    )

    ax.set_xlabel(
        "Petal Length (cm)",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_ylabel(
        "Petal Width (cm)",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_title(
        "Iris Species Classification - KNN",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlim(
        length_min - x_pad,
        length_max + x_pad
    )

    ax.set_ylim(
        width_min - y_pad,
        width_max + y_pad
    )

    ax.grid(alpha=0.2)

    ax.legend(
        loc="best",
        fontsize=9,
        framealpha=0.95
    )

    fig.tight_layout()

    st.pyplot(fig, use_container_width=True)

    plt.close(fig)

    # ======================================
    # 11. 분류 이유
    # ======================================
    st.divider()

    st.subheader("🔎 왜 이 품종으로 분류되었을까?")

    st.write(
        "AI가 입력한 값과 가장 가까운 데이터 5개를 "
        "비교해서 투표를 진행했어."
    )

    vote_cols = st.columns(len(species_list))

    for i, species in enumerate(species_list):

        count = int(votes.get(species, 0))

        with vote_cols[i]:

            st.metric(
                korean_names.get(species, species),
                f"{count}표"
            )

    winner_count = int(votes.get(prediction, 0))

    st.success(
        f"가장 가까운 데이터 5개 중 "
        f"{winner_count}개가 {result_name}이므로 "
        f"이 품종으로 예측했어!"
    )

    # ======================================
    # 12. 최근접 데이터 표
    # ======================================
    st.subheader("📋 가장 가까운 데이터 5개")

    result_table = nearest[
        ["꽃잎 길이", "꽃잎 너비", "품종", "거리"]
    ].copy()

    result_table["품종"] = result_table["품종"].map(
        lambda x: korean_names.get(x, x)
    )

    result_table["거리"] = result_table["거리"].round(3)

    result_table = result_table.rename(
        columns={
            "꽃잎 길이": "꽃잎 길이(cm)",
            "꽃잎 너비": "꽃잎 너비(cm)",
            "거리": "표준화 거리"
        }
    )

    st.dataframe(
        result_table,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "※ 표준화 거리가 작을수록 입력값과 가까운 데이터야."
    )

    # ======================================
    # 13. 색상 안내
    # ======================================
    st.divider()

    st.subheader("🎨 그래프 색상 안내")

    st.markdown(
        f"""
        <div style="
            background-color:#FAFAFA;
            padding:18px;
            border-radius:12px;
            line-height:2.2;
        ">
            <span style="color:#F4C542;font-size:25px;">★</span>
            <b>골드 옐로우</b> : 사용자 입력값<br>

            <span style="color:#F4A6C1;font-size:25px;">★</span>
            <b>연핑크</b> : Setosa<br>

            <span style="color:#8FA8D8;font-size:25px;">★</span>
            <b>연남색</b> : Versicolor<br>

            <span style="color:#9575CD;font-size:25px;">★</span>
            <b>연보라</b> : Virginica<br>

            <span style="color:#40E0D0;font-size:25px;">◯</span>
            <b>민트색 원</b> : 최근접 이웃 5개
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# 14. 알고리즘 안내
# ==========================================
st.divider()

st.subheader("🌱 KNN 알고리즘이란?")

st.write("""
KNN은 가까운 이웃의 데이터를 이용해서
새로운 데이터의 품종을 예측하는 머신러닝 알고리즘이야.

1. 기존 붓꽃 데이터를 학습해.
2. 꽃잎 길이와 너비를 표준화해.
3. 입력값과 기존 데이터의 거리를 계산해.
4. 가장 가까운 5개 데이터를 찾아.
5. 가장 많이 등장한 품종으로 예측해!

이 프로그램은 꽃잎 길이와 너비 두 가지 변수를 사용해.
""")

st.caption("🌸 Iris AI Classification Project")
