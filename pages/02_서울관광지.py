```python
import streamlit as st
import folium
from streamlit_folium import st_folium


# 페이지 설정
st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🇰🇷",
    layout="wide"
)


# 제목
st.title("🇰🇷 서울 관광지 TOP 10")
st.write("외국인 관광객에게 인기 있는 서울의 대표 관광지를 지도에서 만나보세요! 🗺️✨")


# 관광지 데이터
places = [
    {
        "rank": 1,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "description": "조선시대의 대표적인 궁궐입니다. 한복 체험과 함께 방문하기 좋아요! 👘"
    },
    {
        "rank": 2,
        "name": "명동",
        "english": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9826,
        "description": "쇼핑, K-뷰티, 음식 등을 즐길 수 있는 서울의 대표적인 관광지입니다. 🛍️"
    },
    {
        "rank": 3,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "description": "서울의 아름다운 풍경과 야경을 볼 수 있는 대표적인 전망 명소입니다. 🌃"
    },
    {
        "rank": 4,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "description": "전통 한옥과 서울의 옛 모습을 느낄 수 있는 곳입니다. 🏠"
    },
    {
        "rank": 5,
        "name": "인사동",
        "english": "Insadong",
        "lat": 37.5740,
        "lon": 126.9857,
        "description": "전통 공예품과 한국적인 기념품을 만나볼 수 있습니다. 🎨"
    },
    {
        "rank": 6,
        "name": "청계천",
        "english": "Cheonggyecheon Stream",
        "lat": 37.5690,
        "lon": 126.9784,
        "description": "서울 도심에서 산책과 휴식을 즐기기 좋은 명소입니다. 🌿"
    },
    {
        "rank
