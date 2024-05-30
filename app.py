import streamlit as st

from htmlTemplates import footer_css, footer_html
import pandas as pd
# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False
# DB Management
import sqlite3
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
    conn.commit()

def login_user(username,password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
    data = c.fetchall()
    return data


def view_login_users(username):
    c.execute('SELECT * FROM userstable WHERE username =?', (username,))
    data = c.fetchall()
    return data



def main():
    st.title("QuizGen :books:")

    st.write("좌측에서 문제 생성에 참고할 파일 유형을 선택하여 주십시오.")

    menu = ["Login","SignUp"]
    choice = st.selectbox("Menu",menu)

    if choice == "Login":
        st.subheader("로그인")

        username = st.text_input("User Name")
        password = st.text_input("Password",type='password')
        if st.checkbox("Login"):
            # if password == '12345':
            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username,check_hashes(password,hashed_pswd))
            if result:

                st.success("{}으로 로그인 되었습니다.".format(username))

                task = st.selectbox("마이페이지",["프로필","미구현1","미구현2"])
                if task == "미구현1":
                    st.subheader("아직 구현 되지 않은 기능입니다.")

                elif task == "미구현2":
                    st.subheader("아직 구현 되지 않은 기능입니다.")
                elif task == "프로필":
                    st.subheader("{} 프로필".format(username))
                    user_result = view_login_users(username)
                    clean_db = pd.DataFrame(user_result,columns=["Username","Password"])
                    st.dataframe(clean_db)
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "SignUp":
        st.subheader("회원가입")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')

        if st.button("Signup"):
            create_usertable()
            add_userdata(new_user,make_hashes(new_password))
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")

    st.caption("Sponsored by")

    st.image('hsu.png', width=200)

    # Inject CSS with markdown
    st.markdown(footer_css, unsafe_allow_html=True)

    # Inject footer HTML with markdown
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == '__main__':
    main()




