import streamlit as st
import folium
from streamlit_folium import st_folium


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="서울 1박 2일 여행 코스",
    page_icon="🇰🇷",
    layout="wide"
)


# --------------------------------------------------
# 제목
# --------------------------------------------------

st.title("🇰🇷 서울 주요 관광지 1박 2일 여행 코스")

st.write(
    "서울의 대표 관광지 10곳을 1박 2일 동안 "
    "오전 9시부터 오후 7시까지 둘러보는 여행 코스입니다. 🗺️"
)

st.info(
    "💡 관광지 사이의 이동시간을 고려해 비슷한 지역끼리 묶었습니다. "
    "대중교통과 도보 이동을 중심으로 계획했습니다."
)


# --------------------------------------------------
# 관광지 데이터
# --------------------------------------------------

places = [
    {
        "day": "1일차",
        "time": "09:00 - 10:30",
        "rank": 1,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "description": "조선시대 대표 궁궐로 한국의 전통 건축과 역사를 볼 수 있는 서울 대표 관광지입니다.",
        "move": "여행 시작"
    },
    {
        "day": "1일차",
        "time": "10:40 - 12:00",
        "rank": 2,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "description": "전통 한옥이 모여 있는 서울의 대표적인 전통문화 거리입니다.",
        "move": "경복궁에서 도보 이동"
    },
    {
        "day": "1일차",
        "time": "12:10 - 13:10",
        "rank": 3,
        "name": "인사동",
        "english": "Insadong",
        "lat": 37.5740,
        "lon": 126.9857,
        "description": "전통 공예품과 기념품, 전통적인 분위기의 상점과 카페를 즐길 수 있습니다.",
        "move": "북촌에서 도보 이동"
    },
    {
        "day": "1일차",
        "time": "14:00 - 15:00",
        "rank": 4,
        "name": "청계천",
        "english": "Cheonggyecheon Stream",
        "lat": 37.5690,
        "lon": 126.9784,
        "description": "서울 도심을 흐르는 하천으로 산책하면서 서울의 도시 풍경을 즐길 수 있습니다.",
        "move": "인사동에서 도보 이동"
    },
    {
        "day": "1일차",
        "time": "15:20 - 17:00",
        "rank": 5,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "description": "빈대떡, 김밥 등 다양한 한국 음식과 전통시장 분위기를 경험할 수 있습니다.",
        "move": "청계천에서 도보 이동"
    },
    {
        "day": "2일차",
        "time": "09:00 - 10:30",
        "rank": 6,
        "name": "동대문디자인플라자",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5671,
        "lon": 127.0095,
        "description": "독특한 건축 디자인과 전시, 패션 등을 즐길 수 있는 서울의 랜드마크입니다.",
        "move": "호텔에서 지하철 이동"
    },
    {
        "day": "2일차",
        "time": "11:00 - 12:00",
        "rank": 7,
        "name": "명동",
        "english": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9826,
        "description": "쇼핑과 맛집, 길거리 음식 등을 즐길 수 있는 서울의 대표적인 관광 거리입니다.",
        "move": "DDP에서 지하철 이동"
    },
    {
        "day": "2일차",
        "time": "13:00 - 14:30",
        "rank": 8,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "description": "서울의 도시 풍경을 한눈에 볼 수 있는 대표적인 전망 명소입니다.",
        "move": "명동에서 버스 또는 택시 이동"
    },
    {
        "day": "2일차",
        "time": "15:30 - 17:00",
        "rank": 9,
        "name": "홍대",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "description": "공연, 쇼핑, 카페와 다양한 젊은 문화를 즐길 수 있는 활기찬 거리입니다.",
        "move": "N서울타워에서 대중교통 이동"
    },
    {
        "day": "2일차",
        "time": "18:00 - 19:00",
        "rank": 10,
        "name": "한강공원",
        "english": "Hangang Park",
        "lat": 37.5283,
        "lon": 126.9326,
        "description": "한강을 바라보며 서울의 저녁 풍경을 즐길 수 있는 대표적인 휴식 공간입니다.",
        "move": "홍대에서 대중교통 이동"
    }
]


# --------------------------------------------------
# 지도
# --------------------------------------------------

st.subheader("🗺️ 1박 2일 서울 여행 지도")

seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12
)


# 1일차 / 2일차 색상
day1_color = "red"
day2_color = "blue"


for place in places:

    if place["day"] == "1일차":
        marker_color = day1_color
    else:
        marker_color = day2_color

    popup_text = (
        "<b>"
        + str(place["rank"])
        + ". "
        + place["name"]
        + "</b><br><br>"
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
            place["day"]
            + " | "
            + place["time"]
            + " | "
            + place["name"]
        ),
        popup=folium.Popup(
            popup_text,
            max_width=320
        ),
        icon=folium.Icon(
            color=marker_color,
            icon="info-sign"
        )
    ).add_to(seoul_map)


# 관광지 이동선을 지도에 표시
route_points = []

for place in places:
    route_points.append(
        [place["lat"], place["lon"]]
    )


# 전체 이동선
folium.PolyLine(
    route_points,
    weight=4,
    opacity=0.7
).add_to(seoul_map)


st_folium(
    seoul_map,
    width=1200,
    height=600
)


# --------------------------------------------------
# 1박 2일 일정표
# --------------------------------------------------

st.subheader("📅 1박 2일 여행 일정표")

st.markdown("### 🌅 DAY 1 — 전통문화 + 시장 코스")

day1_schedule = [
    ["09:00 - 10:30", "경복궁", "한국 전통문화와 조선 왕실 역사 감상", "도보"],
    ["10:40 - 12:00", "북촌한옥마을", "한옥 골목 산책 및 사진 촬영", "도보"],
    ["12:00 - 13:00", "🍚 점심", "토속촌 삼계탕", "북촌 → 식당"],
    ["13:10 - 14:00", "인사동", "전통거리 구경 및 기념품 쇼핑", "도보"],
    ["14:10 - 15:00", "청계천", "도심 산책", "도보"],
    ["15:20 - 17:00", "광장시장", "시장 구경 및 간식", "도보"],
    ["17:00 - 18:00", "🍽️ 저녁", "광장시장 먹거리", "도보"],
    ["18:00 - 19:00", "🏨 호텔", "명동 호텔로 이동 및 휴식", "지하철"]
]

st.table(
    {
        "시간": [row[0] for row in day1_schedule],
        "일정": [row[1] for row in day1_schedule],
        "내용": [row[2] for row in day1_schedule],
        "이동": [row[3] for row in day1_schedule]
    }
)


st.markdown("### 🌇 DAY 2 — 랜드마크 + 쇼핑 + 한강 코스")

day2_schedule = [
    ["09:00 - 10:30", "동대문디자인플라자", "DDP 건축물과 주변 구경", "지하철"],
    ["10:30 - 11:00", "🚇 이동", "DDP → 명동", "지하철"],
    ["11:00 - 12:00", "명동", "쇼핑 및 거리 구경", "도보"],
    ["12:00 - 13:00", "🍜 점심", "명동교자", "도보"],
    ["13:00 - 14:30", "N서울타워", "서울 전망 감상", "버스/택시"],
    ["14:30 - 15:30", "🚇 이동", "남산 → 홍대", "대중교통"],
    ["15:30 - 17:00", "홍대", "쇼핑, 카페, 거리문화 구경", "도보"],
    ["17:00 - 18:00", "🍽️ 저녁", "육지 홍대", "도보"],
    ["18:00 - 19:00", "한강공원", "한강 저녁 풍경 감상", "대중교통"]
]

st.table(
    {
        "시간": [row[0] for row in day2_schedule],
        "일정": [row[1] for row in day2_schedule],
        "내용": [row[2] for row in day2_schedule],
        "이동": [row[3] for row in day2_schedule]
    }
)


# --------------------------------------------------
# 식당 추천
# --------------------------------------------------

st.subheader("🍽️ 동선에 맞춘 식당 추천")

st.write(
    "식당은 관광지와 가까운 곳을 우선으로 골라 이동시간을 줄였습니다."
)


st.markdown("### 🌅 DAY 1 아침")

st.info(
    "🏨 아침은 명동 호텔에서 간단하게 먹고 "
    "경복궁으로 이동하는 것을 추천합니다."
)


st.markdown("### 🍗 DAY 1 점심 — 토속촌 삼계탕")

st.write(
    "경복궁 근처에서 전통적인 한국 음식인 삼계탕을 먹기 좋은 선택입니다."
)

st.markdown(
    "[📍 토속촌 삼계탕 지도에서 보기](https://www.google.com/maps/search/?api=1&query=토속촌+삼계탕+서울)"
)


st.markdown("### 🥞 DAY 1 저녁 — 광장시장")

st.write(
    "광장시장에서 빈대떡, 김밥 등 여러 가지 음식을 조금씩 먹는 "
    "시장 먹거리 코스를 추천합니다."
)

st.markdown(
    "[📍 광장시장 지도에서 보기](https://www.google.com/maps/search/?api=1&query=광장시장+서울)"
)


st.markdown("### 🍜 DAY 2 점심 — 명동교자")

st.write(
    "명동 관광 직후 바로 식사할 수 있는 대표적인 칼국수·만두 맛집입니다."
)

st.markdown(
    "[🔗 명동교자 공식 관광정보 보기](https://english.visitseoul.net/eat/Myeongdong-Kyoja-EN/ENP008570)"
)

st.markdown(
    "[📍 명동교자 지도에서 보기](https://www.google.com/maps/search/?api=1&query=명동교자+서울)"
)


st.markdown("### 🥩 DAY 2 저녁 — 육지 홍대")

st.write(
    "홍대 관광을 마친 뒤 한국식 숯불구이를 즐기고 "
    "한강으로 이동하는 동선입니다."
)

st.markdown(
    "[📍 육지 홍대 지도에서 보기](https://www.google.com/maps/search/?api=1&query=육지+홍대+서울)"
)


# --------------------------------------------------
# 호텔 추천
# --------------------------------------------------

st.subheader("🏨 1박 호텔 추천")

st.write(
    "이번 일정은 종로 → 동대문 → 명동 → 남산 → 홍대 → 한강으로 "
    "움직이기 때문에 명동에 숙박하는 것을 추천합니다."
)

st.markdown("### ⭐ 추천 1 — 솔라리아 니시테츠 호텔 서울 명동")

st.write(
    "명동 중심에 있어 1일차 저녁 후 쉬기 좋고, "
    "2일차 DDP와 명동으로 이동하기도 편리합니다."
)

st.markdown(
    "[🔗 솔라리아 니시테츠 호텔 서울 명동 공식 홈페이지](https://solaria-seoul.nnr-h.com/)"
)

st.markdown(
    "[📍 호텔 지도에서 보기](https://www.google.com/maps/search/?api=1&query=솔라리아+니시테츠+호텔+서울+명동)"
)


st.markdown("### ⭐ 추천 2 — 트래블로지 명동 남산")

st.write(
    "명동과 충무로 사이에 있어 명동·남산 관광을 함께 하기 좋은 위치입니다."
)

st.markdown(
    "[🔗 트래블로지 명동 남산 관광정보 보기](https://english.visitseoul.net/hotel/view/27122598)"
)

st.markdown(
    "[📍 호텔 지도에서 보기](https://www.google.com/maps/search/?api=1&query=Travelodge+Myeongdong+Namsan+Seoul)"
)


# --------------------------------------------------
# 관광지별 간단 설명
# --------------------------------------------------

st.subheader("📍 관광지 한눈에 보기")

selected_place = st.selectbox(
    "궁금한 관광지를 선택하세요!",
    [place["name"] for place in places]
)


for place in places:

    if place["name"] == selected_place:

        st.success(
            place["day"]
            + " | "
            + place["time"]
        )

        st.write(
            "📌 "
            + place["description"]
        )

        st.write(
            "🚶 이동: "
            + place["move"]
        )

        map_url = (
            "https://www.google.com/maps/search/?api=1&query="
            + place["lat"].__str__()
            + ","
            + place["lon"].__str__()
        )

        st.markdown(
            "[📍 지도에서 위치 확인하기]("
            + map_url
            + ")"
        )


# --------------------------------------------------
# 여행 팁
# --------------------------------------------------

st.subheader("💡 여행 팁")

st.write(
    "👟 관광지가 많기 때문에 편한 신발을 추천합니다."
)

st.write(
    "🚇 서울 지하철을 이용하면 관광지 사이 이동이 편리합니다."
)

st.write(
    "📱 식당은 방문 전 영업시간과 휴무일을 확인하는 것이 좋습니다."
)

st.write(
    "🌦️ 비가 오거나 날씨가 좋지 않은 경우 야외 관광지 체류시간을 줄이고 "
    "실내 쇼핑이나 카페 시간을 늘리는 것을 추천합니다."
)

st.divider()

st.caption(
    "🇰🇷 즐거운 서울 1박 2일 여행 되세요! ✨"
)
