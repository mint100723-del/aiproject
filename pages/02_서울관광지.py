```python
import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🇰🇷",
    layout="wide"
)

# 제목
st.title("🇰🇷 서울 관광지 TOP 10 🗺️")
st.subheader("외국인 관광객에게 인기 있는 서울의 대표 관광지를 만나보세요! ✨")

st.write(
    "서울 여행을 계획하고 있다면 어디부터 가야 할까요? "
    "지도에서 주요 관광지를 확인하고 마음에 드는 곳을 찾아보세요! 📸"
)

# 서울 관광지 데이터
tourist_data = [
    [1, "경복궁", "Gyeongbokgung Palace", 37.5796, 126.9770,
     "조선시대의 대표적인 궁궐이에요. 한복을 입고 방문하면 더욱 특별해요! 👘"],

    [2, "명동", "Myeongdong", 37.5636, 126.9826,
     "쇼핑과 K-뷰티, 길거리 음식까지 즐길 수 있는 서울 대표 관광지예요! 🛍️"],

    [3, "N서울타워", "N Seoul Tower", 37.5512, 126.9882,
     "서울의 멋진 야경을 감상하기 좋은 대표적인 전망 명소예요! 🌃"],

    [4, "북촌한옥마을", "Bukchon Hanok Village", 37.5826, 126.9830,
     "전통 한옥과 서울의 옛 분위기를 느낄 수 있는 곳이에요. 🏠"],

    [5, "인사동", "Insadong", 37.5740, 126.9857,
     "전통 공예품과 한국적인 기념품을 만나볼 수 있어요! 🎨"],

    [6, "청계천", "Cheonggyecheon Stream", 37.5690, 126.9784,
     "도심 속에서 산책하며 서울의 분위기를 즐기기 좋은 곳이에요. 🌿"],

    [7, "광장시장", "Gwangjang Market", 37.5700, 126.9997,
     "다양한 한국 길거리 음식을 맛볼 수 있는 전통 시장이에요! 🥢"],

    [8, "동대문디자인플라자", "DDP", 37.5671, 127.0095,
     "독특한 건축물과 전시, 패션을 즐길 수 있는 서울의 랜드마크예요! 🌟"],

    [9, "홍대", "Hongdae", 37.5563, 126.9236,
     "K-POP, 스트리트 문화, 쇼핑과 맛집을 즐길 수 있는 젊음의 거리예요! 🎵"],

    [10, "한강공원", "Hangang Park", 37.5283, 126.9326,
     "한강을 바라보며 산책하거나 피크닉을 즐기기 좋은 서울의 명소예요! 🧺"]
]

df = pd.DataFrame(
    tourist_data,
    columns=["순위", "관광지", "영문명", "위도", "경도", "설명"]
)

# 지도
st.header("📍 서울 관광지 TOP 10 지도")

st.map(
    df,
    latitude="위도",
    longitude="경도",
    size=100
)

st.caption("📌 지도 위의 위치를 확인하면서 서울 여행 코스를 계획해 보세요!")

# 관광지 목록
st.header("🏆 서울 관광지 TOP 10")

for _, row in df.iterrows():

    st.markdown(
        f"""
        ### {row['순위']}위. {row['관광지']} 🇰🇷

        **{row['영문명']}**

        💡 {row['설명']}

        📍 위도: {row['위도']:.4f}  
        📍 경도: {row['경도']:.4f}
        """
    )

    st.divider()

# 관광지 선택
st.header("🔎 관광지 자세히 보기")

selected_place = st.selectbox(
    "궁금한 관광지를 선택해 보세요!",
    df["관광지"].tolist()
)

selected = df[df["관광지"] == selected_place].iloc[0]

st.success(
    f"📍 {selected['관광지']} ({selected['영문명']})\n\n"
    f"{selected['설명']}"
)

st.info(
    "💡 Tip: 지도에서 관광지들의 위치를 비교하면 "
    "하루 여행 코스를 만들기 더 쉬워요!"
)

# 푸터
st.markdown("---")

st.caption(
    "🇰🇷 Seoul Travel Map | 서울의 대표 관광지를 쉽고 재미있게 알아보는 지도"
)
```
