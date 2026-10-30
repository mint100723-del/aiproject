```python
import streamlit as st
import folium
from streamlit_folium import st_folium

# ---------------------------------------
# 페이지 설정
# ---------------------------------------
st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🇰🇷",
    layout="wide"
)

# ---------------------------------------
# 제목
# ---------------------------------------
st.title("🇰🇷 서울 관광지 TOP 10 🗺️")
st.subheader("외국인 관광객에게 인기 있는 서울의 대표 관광지를 만나보세요! ✨")

st.write(
    "서울 여행을 계획하고 있다면 어디부터 가야 할까요? "
    "아래 지도에서 주요 관광지를 확인해 보세요! 📸"
)

# ---------------------------------------
# 서울 관광지 데이터
# ---------------------------------------
tourist_data = [
    {
        "rank": 1,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "description": "조선시대의 대표적인 궁궐이에요. 한복 체험과 함께 방문하면 더욱 특별해요! 👘"
    },
    {
        "rank": 2,
        "name": "명동",
        "english": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9826,
        "description": "쇼핑과 K-뷰티, 길거리 음식까지 즐길 수 있는 서울 대표 관광지예요! 🛍️"
    },
    {
        "rank": 3,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "description": "서울의 멋진 야경을 감상하기 좋은 대표적인 전망 명소예요! 🌃"
    },
    {
        "rank": 4,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "description": "전통 한옥과 서울의 옛 분위기를 느낄 수 있는 곳이에요. 🏠"
    },
    {
        "rank": 5,
        "name": "인사동",
        "english": "Insadong",
        "lat": 37.5740,
        "lon": 126.9857,
        "description": "전통 공예품과 한국적인 기념품을 만나볼 수 있어요! 🎨"
    },
    {
        "rank": 6,
        "name": "청계천",
        "english": "Cheonggyecheon Stream",
        "lat": 37.5690,
        "lon": 126.9784,
        "description": "도심 속에서 산책하며 서울의 분위기를 즐기기 좋은 곳이에요. 🌿"
    },
    {
        "rank": 7,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "description": "빈대떡과 다양한 한국 길거리 음식을 맛볼 수 있는 전통 시장이에요! 🥢"
    },
    {
        "rank": 8,
        "name": "동대문디자인플라자",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5671,
        "lon": 127.0095,
        "description": "독특한 건축물과 전시, 패션을 즐길 수 있는 서울의 랜드마크예요! 🌟"
    },
    {
        "rank": 9,
        "name": "홍대",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "description": "K-POP, 스트리트 문화, 쇼핑과 맛집을 즐길 수 있는 젊음의 거리예요! 🎵"
    },
    {
        "rank": 10,
        "name": "한강공원",
        "english": "Hangang Park",
        "lat": 37.5283,
        "lon": 126.9326,
        "description": "한강을 바라보며 산책하거나 피크닉을 즐기기 좋은 서울의 명소예요! 🧺"
    }
]

# ---------------------------------------
# 지도 만들기
# ---------------------------------------
st.header("📍 서울 관광지 TOP 10 지도")

seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# ---------------------------------------
# 관광지 마커 추가
# ---------------------------------------
for place in tourist_data:

    popup_html = f"""
    <div style="width:250px;">
        <h3>{place['rank']}위. {place['name']}</h3>
        <p><b>{place['english']}</b></p>
        <p>{place['description']}</p>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        popup=folium.Popup(
            popup_html,
            max_width=300
        ),
        tooltip=f"{place['rank']}위 | {place['name']}",
        icon=folium.Icon(
            color="red",
            icon="star"
        )
    ).add_to(seoul_map)

# ---------------------------------------
# Streamlit에 지도 표시
# ---------------------------------------
st_folium(
    seoul_map,
    width=None,
    height=600,
    returned_objects=[]
)

st.info(
    "💡 지도에서 ⭐ 표시를 클릭하면 관광지의 이름과 설명을 볼 수 있어요!"
)

# ---------------------------------------
# 관광지 목록
# ---------------------------------------
st.header("🏆 서울 관광지 TOP 10")

for place in tourist_data:

    with st.expander(
        f"{place['rank']}위. {place['name']} 🇰🇷"
    ):

        st.write(f"**영문명:** {place['english']}")

        st.write(place["description"])

        st.write(
            f"📍 위도: {place['lat']} / "
            f"경도: {place['lon']}"
        )

# ---------------------------------------
# 관광지 선택
# ---------------------------------------
st.header("🔎 관광지 자세히 보기")

place_names = [
    place["name"]
    for place in tourist_data
]

selected_name = st.selectbox(
    "궁금한 관광지를 선택해 보세요!",
    place_names
)

selected_place = next(
    place for place in tourist_data
    if place["name"] == selected_name
)

st.success(
    f"📍 {selected_place['name']} "
    f"({selected_place['english']})"
)

st.write(selected_place["description"])

# ---------------------------------------
# 푸터
# ---------------------------------------
st.markdown("---")

st.caption(
    "🇰🇷 Seoul Travel Map | 서울의 대표 관광지를 쉽고 재미있게 알아보는 지도"
)
```
