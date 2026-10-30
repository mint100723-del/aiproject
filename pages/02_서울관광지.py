```python
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🇰🇷",
    layout="wide"
)

st.title("🇰🇷 서울 관광지 TOP 10")
st.write("외국인 관광객에게 인기 있는 서울의 대표 관광지를 지도에서 확인해 보세요! 🗺️")

places = [
    ("경복궁", "Gyeongbokgung Palace", 37.5796, 126.9770, "조선시대 대표 궁궐 👘"),
    ("명동", "Myeongdong", 37.5636, 126.9826, "쇼핑과 K-뷰티, 맛집을 즐길 수 있는 곳 🛍️"),
    ("N서울타워", "N Seoul Tower", 37.5512, 126.9882, "서울의 아름다운 야경을 볼 수 있는 곳 🌃"),
    ("북촌한옥마을", "Bukchon Hanok Village", 37.5826, 126.9830, "전통 한옥을 볼 수 있는 곳 🏠"),
    ("인사동", "Insadong", 37.5740, 126.9857, "전통 문화와 기념품을 만날 수 있는 곳 🎨"),
    ("청계천", "Cheonggyecheon Stream", 37.5690, 126.9784, "도심 속 산책 명소 🌿"),
    ("광장시장", "Gwangjang Market", 37.5700, 126.9997, "한국의 다양한 먹거리를 즐길 수 있는 전통시장 🥢"),
    ("동대문디자인플라자", "Dongdaemun Design Plaza", 37.5671, 127.0095, "서울의 대표적인 건축 랜드마크 🌟"),
    ("홍대", "Hongdae", 37.5563, 126.9236, "K-POP과 젊은 문화를 즐길 수 있는 곳 🎵"),
    ("한강공원", "Hangang Park", 37.5283, 126.9326, "한강에서 산책과 피크닉을 즐길 수 있는 곳 🧺")
]

st.header("📍 서울 관광지 TOP 10 지도")

seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12
)

for number, place in enumerate(places, start=1):

    name = place[0]
    english = place[1]
    latitude = place[2]
    longitude = place[3]
    description = place[4]

    popup = (
        "<b>" + str(number) + "위. " + name + "</b><br>"
        + english + "<br><br>"
        + description
    )

    folium.Marker(
        location=[latitude, longitude],
        tooltip=str(number) + "위 " + name,
        popup=folium.Popup(popup, max_width=300),
        icon=folium.Icon(
            color="red",
            icon="info-sign"
        )
    ).add_to(seoul_map)

st_folium(
    seoul_map,
    width=1200,
    height=600
)

st.header("🏆 관광지 TOP 10")

for number, place in enumerate(places, start=1):

    name = place[0]
    english = place[1]
    description = place[4]

    st.subheader(str(number) + "위. " + name)
    st.write("영문명: " + english)
    st.write(description)
    st.divider()

st.header("🔎 관광지 선택")

names = []

for place in places:
    names.append(place[0])

selected = st.selectbox(
    "궁금한 관광지를 선택하세요!",
    names
)

for place in places:

    if place[0] == selected:

        st.success(
            place[0] + " | " + place[1]
        )

        st.write(place[4])
        break

st.caption("🇰🇷 Seoul Travel Map")
```
