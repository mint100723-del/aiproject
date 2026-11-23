
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =====================================
# 1. 데이터 불러오기
# =====================================

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "copper-dishes_no_missing.csv"

try:
    df = pd.read_csv(FILE_PATH, encoding="utf-8-sig")
except UnicodeDecodeError:
    df = pd.read_csv(FILE_PATH, encoding="cp949")

# 필요한 데이터 확인
required = [
    "dish", "country", "region", "minutes",
    "difficulty", "ingredient_count", "ingredients"
]

for col in required:
    if col not in df.columns:
        raise ValueError(f"필요한 컬럼이 없습니다: {col}")

# 숫자 데이터 변환
for col in ["minutes", "ingredient_count"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 결측치 제거
df = df.dropna(subset=required).copy()

print("=" * 50)
print("🌍 세계 음식 데이터 분석")
print("=" * 50)

print("전체 음식 수:", len(df))
print("국가 수:", df["country"].nunique())
print("지역 수:", df["region"].nunique())

# =====================================
# 2. 가장 많이 사용되는 재료 TOP 15
# =====================================

ingredients = (
    df["ingredients"]
    .dropna()
    .astype(str)
    .str.lower()
    .str.split(";")
    .explode()
    .str.strip()
)

ingredients = ingredients[ingredients != ""]

ingredient_count = ingredients.value_counts().head(15)

print("\n🥕 가장 많이 사용되는 재료 TOP 15")
print(ingredient_count)

# 그래프
plt.figure(figsize=(10, 6))
ingredient_count.sort_values().plot(
    kind="barh",
    color="#F4A6C1"
)
plt.title("Top 15 Most Common Ingredients")
plt.xlabel("Frequency")
plt.ylabel("Ingredient")
plt.tight_layout()
plt.savefig("top_ingredients.png")
plt.show()

# =====================================
# 3. 가장 빨리 만들 수 있는 음식 TOP 10
# =====================================

quick_food = df.nsmallest(10, "minutes")

print("\n⏰ 가장 빠른 음식 TOP 10")
print(quick_food[["dish", "country", "minutes"]])

plt.figure(figsize=(10, 6))
plt.barh(
    quick_food["dish"].astype(str),
    quick_food["minutes"],
    color="#8FA8D8"
)
plt.title("Top 10 Quickest Dishes")
plt.xlabel("Cooking Time (Minutes)")
plt.ylabel("Dish")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("quick_food.png")
plt.show()

# =====================================
# 4. 가장 오래 걸리는 음식 TOP 10
# =====================================

slow_food = df.nlargest(10, "minutes")

print("\n🍲 가장 오래 걸리는 음식 TOP 10")
print(slow_food[["dish", "country", "minutes"]])

plt.figure(figsize=(10, 6))
plt.barh(
    slow_food["dish"].astype(str),
    slow_food["minutes"],
    color="#9575CD"
)
plt.title("Top 10 Longest Cooking Dishes")
plt.xlabel("Cooking Time (Minutes)")
plt.ylabel("Dish")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("slow_food.png")
plt.show()

# =====================================
# 5. 난이도별 조리 시간 비교
# =====================================

difficulty_time = (
    df.groupby("difficulty")["minutes"]
    .mean()
    .sort_values()
)

print("\n👩‍🍳 난이도별 평균 조리 시간")
print(difficulty_time)

plt.figure(figsize=(8, 5))
difficulty_time.plot(
    kind="bar",
    color=["#F4A6C1", "#8FA8D8", "#9575CD"]
)
plt.title("Average Cooking Time by Difficulty")
plt.xlabel("Difficulty")
plt.ylabel("Average Minutes")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("difficulty_time.png")
plt.show()

# =====================================
# 6. 지역별 평균 조리 시간
# =====================================

region_time = (
    df.groupby("region")["minutes"]
    .mean()
    .sort_values(ascending=False)
)

print("\n🌎 지역별 평균 조리 시간")
print(region_time.round(1))

plt.figure(figsize=(12, 6))
region_time.plot(
    kind="bar",
    color="#8FA8D8"
)
plt.title("Average Cooking Time by Region")
plt.xlabel("Region")
plt.ylabel("Minutes")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("region_time.png")
plt.show()

# =====================================
# 7. 재료 개수와 조리 시간의 관계
# =====================================

correlation = df[
    ["ingredient_count", "minutes"]
].corr().iloc[0, 1]

print("\n🥕 재료 개수와 조리 시간의 상관계수")
print(round(correlation, 3))

plt.figure(figsize=(8, 5))
plt.scatter(
    df["ingredient_count"],
    df["minutes"],
    color="#40BFA5",
    alpha=0.6
)
plt.title("Ingredients vs Cooking Time")
plt.xlabel("Number of Ingredients")
plt.ylabel("Cooking Time (Minutes)")
plt.tight_layout()
plt.savefig("ingredient_correlation.png")
plt.show()

# =====================================
# 8. 전체 통계 요약
# =====================================

print("\n📊 전체 조리 시간 통계")
print(df["minutes"].describe())

print("\n📊 전체 재료 개수 통계")
print(df["ingredient_count"].describe())

# =====================================
# 9. 분석 결과 저장
# =====================================

output_dir = BASE_DIR / "outputs"
output_dir.mkdir(exist_ok=True)

df.to_csv(
    output_dir / "cleaned_food_data.csv",
    index=False,
    encoding="utf-8-sig"
)

region_time.to_csv(
    output_dir / "region_analysis.csv",
    encoding="utf-8-sig"
)

ingredient_count.to_csv(
    output_dir / "ingredient_analysis.csv",
    encoding="utf-8-sig"
)

print("\n🎉 모든 분석이 완료되었습니다!")

