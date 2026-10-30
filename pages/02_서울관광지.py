```python
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🇰🇷",
    layout="wide"
)

st.title("🇰🇷 서울 관광지 TOP 10 🗺️")
st.write("외국인 관광객에게 인기 있는 서울의 대표 관광지를 지도에서 확인해 보세요! ✨")

# 서울 주요 관광지 10곳
data = {
    "관광지": [
        "경복궁",
        "명동",
        "N서울타워",
        "북촌한옥마을",
        "인사동",
        "청계천",
        "광장시장",
        "동대문디자인플라자",
        "홍대",
        "한강공원"
    ],
    "영문명": [
        "Gyeongbokgung Palace",
        "Myeongdong",
        "N Seoul Tower",
        "Bukchon Hanok Village",
        "Insadong",
        "Cheonggyecheon Stream",
        "Gwangjang Market",
        "Dongdaemun Design Plaza",
        "Hongdae",
        "Hangang Park"
    ],
    "위도": [
        37.5796,
        37.5636,
        37.5512,
        37.5826,
        37.5740,
        37.5690,
        37.5700,
        37.5671,
        37.5563,
        37.5283
    ],
    "경도": [
        126.9770,
        126.9826,
        126.9882,
        126.9830,
        126.9857,
        126.9784,
        126.9997,
        127.0095,
        126.9236,
        126.9326
    ]
}

df = pd.DataFrame(data)

# 지도
st.header("📍 서울 관광지 지도")

st.map(
    df,
    latitude="위도",
    longitude="경도"
)

# 관광지 목록
st.header("🏆 서울 관광지 TOP 10")

for i, row in df.iterrows():
    st.subheader(f"{i + 1}위. {row['관광지']} 🇰🇷")
    st.write(f"**{row['영문명']}**")
    st.write(
        f"📍 위치: {row['위도']:.4f}, {row['경도']:.4f}"
    )

# 관광지 선택
st.header("🔎 관광지 선택")

place = st.selectbox(
    "관광지를 선택하세요!",
    df["관광지"]
)

selected = df[df["관광지"] == place].iloc[0]

st.success(
    f"📍 {selected['관광지']} / {selected['영문명']}"
)

st.write(
    f"위도: {selected['위도']}, "
    f"경도: {selected['경도']}"
)

st.markdown("---")
st.caption("🇰🇷 Seoul Travel Map")
```
