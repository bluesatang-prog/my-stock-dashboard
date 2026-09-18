import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="글로벌 매크로 및 시장 대시보드",
    page_icon="📊",
    layout="wide"
)

st.title("📊 글로벌 거시경제 & 주식 시장 대시보드")
st.markdown("미국 국채금리, 환율, 변동성지수, 주요 증시 및 경제 지표를 한눈에 모니터링합니다.")

# 2. 안전한 데이터 수집 함수 (오류 방지 처리)
@st.cache_data(ttl=600)
def get_market_data():
    tickers = {
        "미국 2년물 금리": "^US2Y",
        "미국 10년물 금리": "^TNX",
        "미국 30년물 금리": "^TYX",
        "달러 인덱스": "DX-Y.NYB",
        "VIX 변동성지수": "^VIX",
        "S&P 500": "^GSPC",
        "나스닥 종합": "^IXIC",
        "금 시세 (Gold)": "GC=F"
    }
    
    data = {}
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if not hist.empty and len(hist) >= 2:
                latest = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                change = ((latest - prev) / prev) * 100
                data[name] = {"price": latest, "change": change}
            elif not hist.empty:
                latest = float(hist['Close'].iloc[-1])
                data[name] = {"price": latest, "change": 0.0}
            else:
                data[name] = {"price": 0.0, "change": 0.0}
        except Exception:
            data[name] = {"price": 0.0, "change": 0.0}
            
    return data

with st.spinner("실시간 시장 데이터를 불러오는 중입니다... 잠시만 기다려주세요."):
    data = get_market_data()

# 3. 주요 지표 카드 섹션
st.subheader("📌 주요 거시경제 및 시장 지표 요약")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("미국 2년물 국채금리", f"{data['미국 2년물 금리']['price']:.3f}%", f"{data['미국 2년물 금리']['change']:.2f}%")
    st.metric("미국 10년물 국채금리", f"{data['미국 10년물 금리']['price']:.3f}%", f"{data['미국 10년물 금리']['change']:.2f}%")

with col2:
    st.metric("미국 30년물 국채금리", f"{data['미국 30년물 금리']['price']:.3f}%", f"{data['미국 30년물 금리']['change']에서 무슨 일이든']['change']:.2f}%" if 'change' in data['미국 30년물 금리'] else "0.00%")
    spread = data['미국 10년물 금리']['price'] - data['미국 2년물 금리']['price']
    st.metric("장단기 금리차 (10Y-2Y)", f"{spread:.3f}%p", delta_color="off")

with col3:
    st.metric("달러 인덱스 (DXY)", f"{data['달러 인덱스']['price']:.2f}", f"{data['달러 인덱스']['change']:.2f}%")
    st.metric("VIX 변동성지수", f"{data['VIX 변동성지수']['price']:.2f}", f"{data['VIX 변동성지수']['change']:.2f}%")

with col4:
    st.metric("S&P 500", f"{data['S&P 500']['price']:,.2f}", f"{data['S&P 500']['change']:.2f}%")
    st.metric("나스닥 종합", f"{data['나스닥 종합']['price']:,.2f}", f"{data['나스닥 종합']['change']:.2f}%")

st.divider()

# 4. 차트 및 경제 일정 섹션
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 주요 지수 추이 비교 (최근 6개월)")
    chart_option = st.selectbox(
        "조회할 자산을 선택하세요",
        ["S&P 500 & 나스닥", "미국 국채금리 (2Y, 10Y)", "VIX 변동성지수", "금 시세"]
    )
    
    try:
        if chart_option == "S&P 500 & 나스닥":
            df_chart = yf.download(["^GSPC", "^IXIC"], period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame):
                st.line_chart(df_chart)
        elif chart_option == "미국 국채금리 (2Y, 10Y)":
            df_chart = yf.download(["^US2Y", "^TNX"], period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame):
                st.line_chart(df_chart)
        elif chart_option == "VIX 변동성지수":
            df_chart = yf.download("^VIX", period="6mo", progress=False)['Close']
            st.line_chart(df_chart)
        elif chart_option == "금 시세":
            df_chart = yf.download("GC=F", period="6mo", progress=False)['Close']
            st.line_chart(df_chart)
    except Exception:
        st.info("차트 데이터를 불러오는 중입니다...")

with col_right:
    st.subheader("📅 이번 주 주요 경제 일정")
    schedule_data = {
        "요일": ["수요일", "목요일", "금요일", "다음주 월"],
        "이벤트": ["미국 CPI 발표", "미국 신규 실업수당", "미국 PCE 물가", "FOMC 회의 결과"],
        "중요도": ["🔥 높음", "보통", "🔥 높음", "🚨 최고"]
    }
    df_schedule = pd.DataFrame(schedule_data)
    st.table(df_schedule)
    
    st.info("💡 **팁:** 주요 물가 지표 발표일에는 금리와 VIX 변동성에 유의하세요.")

st.markdown(f"**💰 현재 금 시세 (Gold Futures):** `${data['금 시세 (Gold)']['price']:,.2f}`")
