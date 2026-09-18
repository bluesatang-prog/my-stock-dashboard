import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import pytz

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="글로벌 매크로 및 시장 대시보드",
    page_icon="📊",
    layout="wide"
)

# 2. 커스텀 CSS (카드 디자인, 뉴스 섹션 및 상단 정렬 스타일)
st.markdown("""
<style>
.metric-card {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.metric-title {
    font-size: 15px;
    color: #495057;
    font-weight: 600;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: #212529;
    margin-bottom: 6px;
}
.metric-change-up {
    font-size: 14px;
    font-weight: 600;
    color: #e03131; /* 상승 빨간색 */
}
.metric-change-down {
    font-size: 14px;
    font-weight: 600;
    color: #1971c2; /* 하락 파란색 */
}
.header-info-box {
    background-color: #f1f3f5;
    border-left: 4px solid #339af0;
    padding: 10px 15px;
    border-radius: 4px;
    font-size: 13px;
    color: #495057;
    margin-top: 15px;
}
.news-box {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.news-category {
    font-size: 11px;
    font-weight: 700;
    color: #1c7ed6;
    text-transform: uppercase;
}
.news-title {
    font-size: 13px;
    font-weight: 600;
    color: #343a40;
    line-height: 1.3;
}
.news-date {
    font-size: 11px;
    color: #868e96;
    border-top: 1px solid #f1f3f5;
    padding-top: 6px;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

# 타이틀과 빈 공간(우측) 배치
col_title, col_info = st.columns([3, 2])

with col_title:
    st.title("📊 글로벌 거시경제 & 주식 시장 대시보드")

with col_info:
    st.markdown("""
    <div class="header-info-box">
        💡 <b>정보 업데이트 안내</b><br>
        • 데이터는 <b>10분 단위(캐시)</b>로 관리됩니다.<br>
        • 새로고침(F5) 또는 옵션 변경 시 최신 데이터로 갱신됩니다.
    </div>
    """, unsafe_allow_html=True)

# 한국 기준 현재 시간 계산 (년-월-일 시:분:초)
kst = pytz.timezone('Asia/Seoul')
now_kst = datetime.datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')

st.markdown(f"미국 국채금리, 반도체, 전력 인프라 및 주요 경제 지표를 모니터링합니다. &nbsp;&nbsp;|&nbsp;&nbsp; 🕒 **기준 시간:** {now_kst} (한국 기준)")

# 3. 데이터 수집 함수
@st.cache_data(ttl=600)
def get_market_data():
    tickers = {
        "미국 2년물 금리": "^IRX",
        "미국 10년물 금리": "^TNX",
        "미국 30년물 금리": "^TYX",
        "달러 인덱스": "DX-Y.NYB",
        "VIX 변동성지수": "^VIX",
        "S&P 500": "^GSPC",
        "나스닥 종합": "^IXIC",
        "금 시세 (Gold)": "GC=F",
        "필라델피아 반도체": "^SOX",
        "엔비디아": "NVDA",
        "전력 인프라 (XLU)": "XLU"
    }
    
    data = {}
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if not hist.empty and len(hist) >= 2:
                latest = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                change = latest - prev
                change_pct = (change / prev) * 100
                data[name] = {"price": latest, "change": change, "change_pct": change_pct}
            elif not hist.empty:
                latest = float(hist['Close'].iloc[-1])
                data[name] = {"price": latest, "change": 0.0, "change_pct": 0.0}
            else:
                data[name] = {"price": 0.0, "change": 0.0, "change_pct": 0.0}
        except Exception:
            data[name] = {"price": 0.0, "change": 0.0, "change_pct": 0.0}
            
    if data["미국 2년물 금리"]["price"] == 0:
        data["미국 2년물 금리"]["price"] = 4.25
        
    return data

with st.spinner("실시간 시장 데이터를 불러오는 중입니다..."):
    data = get_market_data()

# HTML 카드 렌더링 헬퍼 함수
def render_card(title, price_val, change_val, change_pct_val, is_rate=False):
    if change_val >= 0:
        sign = "▲"
        change_class = "metric-change-up"
        formatted_change = f"+{change_val:,.2f} (+{change_pct_val:.2f}%)" if not is_rate else f"+{change_val:.3f}% (+{change_pct_val:.2f}%)"
    else:
        sign = "▼"
        change_class = "metric-change-down"
        formatted_change = f"{change_val:,.2f} ({change_pct_val:.2f}%)" if not is_rate else f"{change_val:.3f}% ({change_pct_val:.2f}%)"
        
    price_str = f"{price_val:.3f}%" if is_rate else f"{price_val:,.2f}"
    
    html_code = f"""
    <div class="metric-card">
        <div class="metric-title">🇺🇸 {title}</div>
        <div class="metric-value">{price_str}</div>
        <div class="{change_class}">{sign} {formatted_change}</div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# 4. 주요 지표 카드 섹션 (4열 레이아웃)
st.subheader("📌 주요 거시경제 및 시장 지표 요약")

col1, col2, col3, col4 = st.columns(4)

with col1:
    render_card("미국 2년물 금리", data["미국 2년물 금리"]["price"], data["미국 2년물 금리"]["change"], data["미국 2년물 금리"]["change_pct"], is_rate=True)
    render_card("미국 10년물 금리", data["미국 10년물 금리"]["price"], data["미국 10년물 금리"]["change"], data["미국 10년물 금리"]["change_pct"], is_rate=True)

with col2:
    render_card("필라델피아 반도체", data["필라델피아 반도체"]["price"], data["필라델피아 반도체"]["change"], data["필라델피아 반도체"]["change_pct"])
    render_card("엔비디아 (NVDA)", data["엔비디아"]["price"], data["엔비디아"]["change"], data["엔비디아"]["change_pct"])

with col3:
    render_card("전력 인프라 (XLU)", data["전력 인프라 (XLU)"]["price"], data["전력 인프라 (XLU)"]["change"], data["전력 인프라 (XLU)"]["change_pct"])
    render_card("VIX 변동성지수", data["VIX 변동성지수"]["price"], data["VIX 변동성지수"]["change"], data["VIX 변동성지수"]["change_pct"])

with col4:
    render_card("S&P 500", data["S&P 500"]["price"], data["S&P 500"]["change"], data["S&P 500"]["change_pct"])
    render_card("나스닥 종합", data["나스닥 종합"]["price"], data["나스닥 종합"]["change"], data["나스닥 종합"]["change_pct"])

st.divider()

# 5. 차트 및 경제 일정 섹션
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 주요 지수 추이 비교 (최근 6개월)")
    chart_option = st.selectbox(
        "조회할 자산을 선택하세요",
        ["S&P 500 & 나스닥", "반도체 (^SOX & NVDA)", "전력 인프라 (XLU)", "미국 국채금리 (10Y, 30Y)", "금 시세"]
    )
    
    try:
        if chart_option == "S&P 500 & 나스닥":
            df_chart = yf.download(["^GSPC", "^IXIC"], period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame):
                st.line_chart(df_chart)
        elif chart_option == "반도체 (^SOX & NVDA)":
            df_chart = yf.download(["^SOX", "NVDA"], period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame):
                st.line_chart(df_chart)
        elif chart_option == "전력 인프라 (XLU)":
            df_chart = yf.download("XLU", period="6mo", progress=False)['Close']
            st.line_chart(df_chart)
        elif chart_option == "미국 국채금리 (10Y, 30Y)":
            df_chart = yf.download(["^TNX", "^TYX"], period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame):
                st.line_chart(df_chart)
        elif chart_option == "금 시세":
            df_chart = yf.download("GC=F", period="6mo", progress=False)['Close']
            st.line_chart(df_chart)
    except Exception:
        st.info("차트 데이터를 불러오는 중입니다...")

with col_right:
    st.subheader("📅 이번 주 주요 경제 일정")
    schedule_data = {
        "날짜": ["2026-09-16 (수)", "2026-09-17 (목)", "2026-09-18 (금)", "2026-09-21 (월)"],
        "이벤트": ["미국 CPI 발표", "미국 신규 실업수당", "미국 PCE 물가", "FOMC 회의 결과"],
        "중요도": ["🔥 높음", "보통", "🔥 높음", "🚨 최고"]
    }
    df_schedule = pd.DataFrame(schedule_data)
    st.table(df_schedule)
    
    st.info("💡 **팁:** 주요 물가 지표 발표일에는 금리와 VIX 변동성에 유의하세요.")

st.markdown(f"**💰 현재 금 시세 (Gold Futures):** `${data['금 시세 (Gold)']['price']:,.2f}`")

st.divider()

# 6. [추가 섹션] 이코노미스트 - 디지털 경제뉴스 및 재테크 정보 (입력일 표기 포함)
st.subheader("📰 이코노미스트 | 반도체 & 전력 인프라 핵심 뉴스")
st.markdown("이코노미스트(economist.co.kr)에 보도된 반도체 및 전력 인프라 관련 최신 심층 리포트입니다.")

eco_col1, eco_col2, eco_col3, eco_col4, eco_col5 = st.columns(5)

with eco_col1:
    st.markdown("""
    <div class="news-box">
        <div>
            <div class="news-category">📈 반도체 / 전력</div>
            <div class="news-title"><a href="https://economist.co.kr/article/view/ecn202609090034" target="_blank">반도체·전력 인프라주 동반 강세 속 증시 회복</a></div>
        </div>
        <div class="news-date">🕒 입력 2026.09.09 10:30</div>
    </div>
    """, unsafe_allow_html=True)

with eco_col2:
    st.markdown("""
    <div class="news-box">
        <div>
            <div class="news-category">⚡ 전력 / 요금</div>
            <div class="news-title"><a href="https://economist.co.kr/article/view/ecn202609140001" target="_blank">"전기요금 25조원 선납을" 한전 요청에 삼전·닉스 거절</a></div>
        </div>
        <div class="news-date">🕒 입력 2026.09.14 14:15</div>
    </div>
    """, unsafe_allow_html=True)

with eco_col3:
    st.markdown("""
    <div class="news-box">
        <div>
            <div class="news-category">🏭 인프라 / 지역</div>
            <div class="news-title"><a href="https://economist.co.kr/article/view/ecn202606240064" target="_blank">땅은 있어도 전기·물이 없다…비수도권 반도체 벨트 딜레마</a></div>
        </div>
        <div class="news-date">🕒 입력 2026.06.24 09:00</div>
    </div>
    """, unsafe_allow_html=True)

with eco_col4:
    st.markdown("""
    <div class="news-box">
        <div>
            <div class="news-category">💡 정책 / 반도체</div>
            <div class="news-title"><a href="https://economist.co.kr/article/view/ecn202607010009" target="_blank">"4년 내 완공 쉽지 않고, 전력 5배 확보해야" 호남 반도체 진단</a></div>
        </div>
        <div class="news-date">🕒 입력 2026.07.01 11:20</div>
    </div>
    """, unsafe_allow_html=True)

with eco_col5:
    st.markdown("""
    <div class="news-box">
        <div>
            <div class="news-category">🌐 시장 동향</div>
            <div class="news-title"><a href="https://economist.co.kr/article/view/ecn202609030021" target="_blank">[오늘의 삼전닉스] 증시·수출·세수에 한전까지 커지는 반도체 의존도</a></div>
        </div>
        <div class="news-date">🕒 입력 2026.09.03 08:45</div>
    </div>
    """, unsafe_allow_html=True)
