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
    {
        "rank": 1,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "description": "조선시대 대표 궁궐로 한국의 전통문화를 느낄 수 있는 서울의 대표 관광지입니다."
    },
    {
        "rank": 2,
        "name": "명동",
        "english": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9826,
        "description": "쇼핑과 맛집, 길거리 음식 등을 즐길 수 있는 서울의 대표적인 번화가입니다."
    },
    {
        "rank": 3,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "description": "서울의 아름다운 풍경과 야경을 감상할 수 있는 대표적인 전망 명소입니다."
    },
    {
        "rank": 4,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "description": "전통 한옥이 모여 있어 한국의 전통적인 분위기를 느낄 수 있는 곳입니다."
    },
    {
        "rank": 5,
        "name": "인사동",
        "english": "Insadong",
        "lat": 37.5740,
        "lon": 126.9857,
        "description": "전통 공예품과 기념품, 한국 음식 등을 만나볼 수 있는 문화 거리입니다."
    },
    {
        "rank": 6,
        "name": "청계천",
        "english": "Cheonggyecheon Stream",
        "lat": 37.5690,
        "lon": 126.9784,
        "description": "서울 도심을 흐르는 아름다운 하천으로 산책하기 좋은 관광 명소입니다."
    },
    {
        "rank": 7,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "description": "빈대떡과 김밥 등 다양한 한국 음식을 맛볼 수 있는 전통시장입니다."
    },
    {
        "rank": 8,
        "name": "동대문디자인플라자",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5671,
        "lon": 127.0095,
        "description": "독특한 건축물과 전시, 디자인, 패션 등을 즐길 수 있는 명소입니다."
    },
    {
        "rank": 9,
        "name": "홍대",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "description": "음악과 공연, 쇼핑, 맛집 등 젊은 문화를 즐길 수 있는 활기찬 거리입니다."
    },
    {
        "rank": 10,
        "name": "한강공원",
        "english": "Hangang Park",
        "lat": 37.5283,
        "lon": 126.9326,
        "description": "한강을 바라보며 산책하고 여유로운 시간을 보내기 좋은 서울의 대표적인 공간입니다."
    }
]


st.subheader("🗺️ 서울 관광지 지도")

seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12
)


for place in places:

    popup_text = (
        "<b>"
        + place["name"]
        + "</b><br>"
        + place["english"]
        + "<br><br>"
        + place["description"]
    )

    folium.Marker(
        location=[
            place["lat"],
            place["lon"]
        ],
        tooltip=(
            str(place["rank"])
            + "위 | "
            + place["name"]
        ),
        popup=folium.Popup(
            popup_text,
            max_width=300
        ),
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


st.subheader("📍 서울 관광지 TOP 10")

for place in places:

    st.markdown(
        "**"
        + str(place["rank"])
        + "위. "
        + place["name"]
        + "** — "
        + place["english"]
    )


st.divider()


st.subheader("🔎 관광지 자세히 알아보기")

selected_place = st.selectbox(
    "궁금한 관광지를 선택해 주세요!",
    [place["name"] for place in places]
)


for place in places:

    if place["name"] == selected_place:

        st.success(
            "📍 "
            + place["name"]
            + "에 대해 알아볼까요?"
        )

        st.write(
            "🇺🇸 영어 이름: "
            + place["english"]
        )

        st.write(
            "💬 "
            + place["description"]
        )

        st.write(
            "📌 위치: "
            + str(place["lat"])
            + ", "
            + str(place["lon"])
        )


st.divider()

st.caption("🇰🇷 서울에서 즐거운 여행을 시작해 보세요! ✨")
