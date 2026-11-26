
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="세계 음식 데이터 분석",
    page_icon="🍰",
    layout="wide"
)

st.title("🌍 세계 음식 데이터 분석")
st.caption("나라별 음식의 재료, 조리 시간, 난이도를 분석합니다.")

# =====================================
# 2. 데이터 불러오기
# =====================================

# 현재 파이썬 파일의 상위 폴더로 이동
BASE_DIR = Path(__file__).resolve().parent.parent

# 상위 폴더에 있는 CSV 파일 경로
FILE_PATH = BASE_DIR / "copper-dishes_no_missing.csv"


@st.cache_data
def load_data(file_path):
    """CSV 파일을 읽고 숫자 데이터를 정리합니다."""

    try:
        data = pd.read_csv(
            file_path,
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        data = pd.read_csv(
            file_path,
            encoding="cp949"
        )

    return data


# CSV 파일 존재 여부 확인
if not FILE_PATH.exists():
    st.error("CSV 파일을 찾을 수 없습니다.")

    st.write("현재 확인한 파일 경로:")
    st.code(str(FILE_PATH))

    st.info(
        "GitHub 저장소의 상위 폴더에 "
        "copper-dishes_no_missing.csv 파일이 있는지 확인해 주세요."
    )

    st.stop()


# CSV 파일 읽기
try:
    df = load_data(str(FILE_PATH))

except Exception as e:
    st.error("CSV 파일을 읽는 중 오류가 발생했습니다.")
    st.code(str(e))
    st.stop()


# =====================================
# 3. 필요한 데이터 확인
# =====================================

required = [
    "dish",
    "country",
    "region",
    "minutes",
    "difficulty",
    "ingredient_count",
    "ingredients"
]

missing_columns = [
    col for col in required
    if col not in df.columns
]

if missing_columns:
    st.error("CSV 파일에 필요한 컬럼이 없습니다.")

    st.write("누락된 컬럼:")
    st.write(missing_columns)

    st.write("현재 CSV 파일의 컬럼:")
    st.write(df.columns.tolist())

    st.stop()


# =====================================
# 4. 데이터 정리
# =====================================

# 숫자 데이터 변환
for col in ["minutes", "ingredient_count"]:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# 결측치 제거
df = df.dropna(
    subset=required
).copy()

# 음식 이름과 나라 이름을 문자열로 변환
for col in ["dish", "country", "region", "difficulty"]:
    df[col] = df[col].astype(str).str.strip()

# 빈 문자열 제거
df = df[
    (df["dish"] != "") &
    (df["country"] != "") &
    (df["ingredients"].astype(str).str.strip() != "")
].copy()

# 음수 조리 시간 및 재료 개수 제거
df = df[
    (df["minutes"] >= 0) &
    (df["ingredient_count"] >= 0)
].copy()

if df.empty:
    st.warning("분석할 수 있는 데이터가 없습니다.")
    st.stop()


# =====================================
# 5. 전체 데이터 요약
# =====================================

st.header("📊 전체 데이터 요약")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "전체 음식 수",
        f"{len(df):,}개"
    )

with col2:
    st.metric(
        "국가 수",
        f"{df['country'].nunique():,}개"
    )

with col3:
    st.metric(
        "지역 수",
        f"{df['region'].nunique():,}개"
    )

with col4:
    st.metric(
        "평균 조리 시간",
        f"{df['minutes'].mean():.1f}분"
    )

st.divider()


# =====================================
# 6. 가장 많이 사용되는 재료 TOP 15
# =====================================

st.header("🥕 가장 많이 사용되는 재료 TOP 15")

ingredients = (
    df["ingredients"]
    .dropna()
    .astype(str)
    .str.lower()
    .str.split(";")
    .explode()
    .str.strip()
)

ingredients = ingredients[
    ingredients != ""
]

ingredient_count = ingredients.value_counts().head(15)

if not ingredient_count.empty:

    fig, ax = plt.subplots(figsize=(10, 6))

    ingredient_count.sort_values().plot(
        kind="barh",
        color="#F4A6C1",
        ax=ax
    )

    ax.set_title("Top 15 Most Common Ingredients")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Ingredient")

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(
        ingredient_count.rename("사용 횟수"),
        use_container_width=True
    )

else:
    st.info("재료 데이터가 없습니다.")


st.divider()


# =====================================
# 7. 가장 빨리 만들 수 있는 음식 TOP 10
# =====================================

st.header("⏰ 가장 빨리 만들 수 있는 음식 TOP 10")

quick_food = df.nsmallest(
    10,
    "minutes"
).copy()

if not quick_food.empty:

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh(
        quick_food["dish"].astype(str),
        quick_food["minutes"],
        color="#8FA8D8"
    )

    ax.set_title("Top 10 Quickest Dishes")
    ax.set_xlabel("Cooking Time (Minutes)")
    ax.set_ylabel("Dish")

    ax.invert_yaxis()

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(
        quick_food[
            ["dish", "country", "minutes"]
        ].rename(
            columns={
                "dish": "음식",
                "country": "나라",
                "minutes": "조리 시간(분)"
            }
        ),
        use_container_width=True
    )


st.divider()


# =====================================
# 8. 가장 오래 걸리는 음식 TOP 10
# =====================================

st.header("🍲 가장 오래 걸리는 음식 TOP 10")

slow_food = df.nlargest(
    10,
    "minutes"
).copy()

if not slow_food.empty:

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh(
        slow_food["dish"].astype(str),
        slow_food["minutes"],
        color="#9575CD"
    )

    ax.set_title("Top 10 Longest Cooking Dishes")
    ax.set_xlabel("Cooking Time (Minutes)")
    ax.set_ylabel("Dish")

    ax.invert_yaxis()

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(
        slow_food[
            ["dish", "country", "minutes"]
        ].rename(
            columns={
                "dish": "음식",
                "country": "나라",
                "minutes": "조리 시간(분)"
            }
        ),
        use_container_width=True
    )


st.divider()


# =====================================
# 9. 난이도별 조리 시간 비교
# =====================================

st.header("👩‍🍳 난이도별 평균 조리 시간")

difficulty_time = (
    df.groupby("difficulty")["minutes"]
    .mean()
    .sort_values()
)

if not difficulty_time.empty:

    fig, ax = plt.subplots(figsize=(8, 5))

    difficulty_time.plot(
        kind="bar",
        color="#F4A6C1",
        ax=ax
    )

    ax.set_title("Average Cooking Time by Difficulty")
    ax.set_xlabel("Difficulty")
    ax.set_ylabel("Average Minutes")

    ax.tick_params(
        axis="x",
        rotation=0
    )

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(
        difficulty_time.round(1).rename(
            "평균 조리 시간(분)"
        ),
        use_container_width=True
    )


st.divider()


# =====================================
# 10. 지역별 평균 조리 시간
# =====================================

st.header("🌎 지역별 평균 조리 시간")

region_time = (
    df.groupby("region")["minutes"]
    .mean()
    .sort_values(ascending=False)
)

if not region_time.empty:

    fig, ax = plt.subplots(figsize=(12, 6))

    region_time.plot(
        kind="bar",
        color="#8FA8D8",
        ax=ax
    )

    ax.set_title("Average Cooking Time by Region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Minutes")

    ax.tick_params(
        axis="x",
        rotation=45
    )

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(
        region_time.round(1).rename(
            "평균 조리 시간(분)"
        ),
        use_container_width=True
    )


st.divider()


# =====================================
# 11. 재료 개수와 조리 시간의 관계
# =====================================

st.header("🥕 재료 개수와 조리 시간의 관계")

correlation = df[
    ["ingredient_count", "minutes"]
].corr().iloc[0, 1]

st.metric(
    "재료 개수와 조리 시간의 상관계수",
    f"{correlation:.3f}"
)

fig, ax = plt.subplots(figsize=(8, 5))

ax.scatter(
    df["ingredient_count"],
    df["minutes"],
    color="#40BFA5",
    alpha=0.6
)

ax.set_title("Ingredients vs Cooking Time")
ax.set_xlabel("Number of Ingredients")
ax.set_ylabel("Cooking Time (Minutes)")

fig.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.caption(
    "상관계수는 두 변수 사이의 관계를 나타냅니다. "
    "양수이면 함께 증가하는 경향, 음수이면 반대 방향의 경향이 있습니다."
)


st.divider()


# =====================================
# 12. 전체 통계 요약
# =====================================

st.header("📈 전체 통계 요약")

col1, col2 = st.columns(2)

with col1:
    st.subheader("조리 시간 통계")

    st.dataframe(
        df["minutes"].describe().round(1),
        use_container_width=True
    )

with col2:
    st.subheader("재료 개수 통계")

    st.dataframe(
        df["ingredient_count"].describe().round(1),
        use_container_width=True
    )


st.divider()


# =====================================
# 13. 분석 결과 다운로드
# =====================================

st.header("📥 분석 결과 다운로드")

# 정리된 전체 데이터
cleaned_csv = df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="정리된 전체 데이터 다운로드",
    data=cleaned_csv,
    file_name="cleaned_food_data.csv",
    mime="text/csv"
)


# 지역별 분석 결과
region_csv = region_time.to_csv(
    encoding="utf-8-sig"
)

st.download_button(
    label="지역별 조리 시간 분석 다운로드",
    data=region_csv,
    file_name="region_analysis.csv",
    mime="text/csv"
)


# 재료 분석 결과
ingredient_csv = ingredient_count.to_csv(
    encoding="utf-8-sig"
)

st.download_button(
    label="재료 분석 결과 다운로드",
    data=ingredient_csv,
    file_name="ingredient_analysis.csv",
    mime="text/csv"
)


st.success("🎉 모든 분석이 완료되었습니다!")
