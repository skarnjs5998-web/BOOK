import streamlit as st
import mysql.connector
import pandas as pd
from mysql.connector import Error


# 1. DB 연결 캐싱 (성능 최적화)
# @st.cache_resource 데코레이터를 사용하여 앱 실행 중 단 한 번만 DB에 연결합니다.
@st.cache_resource
def init_connection():
    """st.secrets에 저장된 정보를 사용하여 MySQL에 연결하고 연결 객체를 반환합니다."""
    try:
        # secrets.toml에서 접속 정보 로드
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        return conn
    except Error as e:
        st.error(f"MySQL 연결 오류: {e}")
        return None


# 2. 쿼리 실행 함수
def run_query(conn, query):
    """주어진 쿼리를 실행하고 결과를 DataFrame으로 반환합니다."""
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(query)

        # 컬럼 이름과 데이터 가져오기
        columns = [i[0] for i in cursor.description]
        data = cursor.fetchall()

        cursor.close()

        return pd.DataFrame(data, columns=columns)
    except Error as e:
        st.error(f"쿼리 실행 오류: {e}")
        return None


# =========================================================================
# Streamlit 웹 앱 메인 로직
# =========================================================================

st.title("📚 madang DB 조회 웹 애플리케이션")
st.markdown("---")

# 1. DB 연결 시도
conn = init_connection()

if conn:
    st.success(f"데이터베이스 '{st.secrets['mysql']['database']}'에 연결되었습니다.")

    # 2. Book 테이블 조회 및 표시
    st.header("📖 Book (도서 목록)")
    book_query = "SELECT bookid, bookname, publisher, price FROM Book;"
    book_df = run_query(conn, book_query)

    if book_df is not None:
        st.dataframe(book_df, use_container_width=True)

    st.markdown("---")

    # 3. Customer 테이블 조회 및 표시
    st.header("👤 Customer (고객 목록)")
    cust_query = "SELECT custid, name, address, phone FROM Customer;"
    cust_df = run_query(conn, cust_query)

    if cust_df is not None:
        st.dataframe(cust_df, use_container_width=True)

    st.markdown("---")

    # 추가: 주문 건수 조회
    st.subheader("📊 통계: 전체 주문 건수")
    order_count_query = "SELECT COUNT(*) FROM Orders;"
    order_count_df = run_query(conn, order_count_query)

    if order_count_df is not None:
        count = order_count_df.iloc[0, 0]
        st.metric(label="총 주문 건수", value=f"{count} 건")

else:
    st.error("데이터베이스 연결에 실패했습니다. `.streamlit/secrets.toml` 파일의 설정과 MySQL 서버 상태를 확인해주세요.")