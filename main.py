import streamlit as st 
st.title('나의 첫 한정선 만들기!')
a=st.text_input('이름을 입력행 중셍용')
b=st.selectbox('알럽유한정선요거트모찌',['블루베리요거트','샤머요거트','무화과'])
if st.button('인사말 생성'):
  st.write('반갑습니다')
