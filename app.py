import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import pytz

# 1. 페이지 레이아웃 설정 (브라우저 탭 아이콘을 대한민국 국기 🇰🇷로 설정)
st.set_page_config(
    page_title="글로벌 매크로 및 시장 대시보드",
    page_icon="🇰🇷",
    layout="wide"
)

# 2. Carestream 감성의 딥 브라운 & 오렌지 커스텀 CSS 테마 적용
st.markdown("""
<style>
/* 전체 배경 및 폰트 톤 핏 */
.stApp {
    background-color: #faf9f6;
}

/* 상단 메인 히어로 배너 스타일 (딥 브라운 그라데이션) */
.hero-banner {
    background: linear-gradient(135deg, #2b1d14 0%, #422d20 100%);
    padding: 35px 40px;
    border-radius: 12px;
    color: #ffffff;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(43, 29, 20, 0.15);
}
.hero-title {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 10px;
}
.hero-subtitle {
    font-size: 14px;
    color: #d7ccc8;
    line-height: 1.5;
}

/* 메트릭 카드 스타일 (오렌지 포인트 테두리 및 톤) */
.metric-card {
    background-color: #ffffff;
    border: 1px solid #e6ded6;
    border-top: 4px solid #e65100; /* 오렌지 포인트 상단 바 */
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    transition: transform 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(230, 81, 0, 0.1);
}
.metric-title {
    font-size: 14px;
    color: #5d4037;
    font-weight: 600;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #2b1d14;
    margin-bottom: 6px;
}
.metric-change-up {
    font-size: 13px;
    font-weight: 600;
    color: #d32f2f; /* 상승 빨간색 */
}
.metric-change-down {
    font-size: 13px;
    font-weight: 600;
    color: #0277bd; /* 하락 파란색 */
}

/* 정보 안내 박스 */
.header-info-box {
    background-color: #fbe9e7;
    border-left: 4px solid #e65100;
    padding: 12px 15px;
    border-radius: 4px;
    font-size: 13px;
    color: #4e342e;
}

/* 뉴스 아카이브 카드 스타일 */
.news-box {
    background-color: #ffffff;
    border: 1px solid #e6ded6;
    border-left: 3px solid #ff8f00;
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 10px;
    height: 145px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.news-category {
    font-size: 11px;
    font-weight: 700;
    color: #e65100;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.news-title {
    font-size: 13px;
    font-weight: 600;
    color: #2b1d14;
    line-height: 1.3;
}
.news-title a {
    color: #2b1d14;
    text-decoration: none;
}
.news-title a:hover {
    color: #e65100;
    text-decoration: underline;
}
.news-date {
    font-size: 11px;
    color: #8d6e63;
    border-top: 1px solid #efebe9;
    padding-top: 6px;
    margin-top: 6px;
}

/* 서브헤더 커스텀 컬러링 */
h2, h3 {
    color: #2b1d14 !important;
}
</style>
""", unsafe_allow_html=True)

# 3. 상단 히어로 배너 영역 (Carestream 딥브라운 톤 적용)
kst = pytz.timezone('Asia/Seoul')
now_kst = datetime.datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">🇰🇷 글로벌 거시경제 & 주식 시장 대시보드</div>
    <div class="hero-subtitle">
        미국 국채금리, 반도체, 전력 인프라 및 핵심 경제 지표 실시간 모니터링 시스템<br>
        🕒 <b>기준 시간:</b> {now_kst} (한국 기준) &nbsp;&nbsp;|&nbsp;&nbsp; 💡 데이터는 10분 단위로 캐시 관리됩니다.
    </div>
</div>
""", unsafe_allow_html=True)

# 4. 데이터 수집 함수
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
def render_card(title, price_val, change_val, change_pct_val, is_rate=False, prefix="🇺🇸 "):
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
        <div class="metric-title">{prefix}{title}</div>
        <div class="metric-value">{price_str}</div>
        <div class="{change_class}">{sign} {formatted_change}</div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# 5. 주요 지표 카드 섹션 (4열 레이아웃 - 금 시세 카드 포함)
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
    # 기존 단독 텍스트였던 금 시세를 카드 형태로 4열 상단 요약에 편입
    render_card("금 시세 (Gold)", data["금 시세 (Gold)"]["price"], data["금 시세 (Gold)"]["change"], data["금 시세 (Gold)"]["change_pct"], prefix="🪙 ")

st.divider()

# 6. 차트 및 경제 일정 섹션
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
    
    st.markdown("""
    <div class="header-info-box">
        💡 <b>Tip:</b> 주요 물가 지표 발표일에는 금리와 VIX 변동성에 유의하세요.
    </div>
    """, unsafe_allow_html=True)

st.divider()

# 7. [아카이브 관리 섹션] 핵심 뉴스 리포트 데이터 리스트 관리
archived_news = [
    {
        "category": "📈 반도체 / 전력",
        "title": "반도체·전력 인프라주 동반 강세 속 증시 회복",
        "url": "https://economist.co.kr/article/view/ecn202609090034",
        "date": "2026.09.09 10:30"
    },
    {
        "category": "⚡ 전력 / 요금",
        "title": "\"전기요금 25조원 선납을\" 한전 요청에 삼전·닉스 거절",
        "url": "https://economist.co.kr/article/view/ecn202609140001",
        "date": "2026.09.14 14:15"
    },
    {
        "category": "🏭 인프라 / 지역",
        "title": "땅은 있어도 전기·물이 없다…비수도권 반도체 벨트 딜레마",
        "url": "https://economist.co.kr/article/view/ecn202606240064",
        "date": "2026.06.24 09:00"
    },
    {
        "category": "💡 정책 / 반도체",
        "title": "\"4년 내 완공 쉽지 않고, 전력 5배 확보해야\" 호남 반도체 진단",
        "url": "https://economist.co.kr/article/view/ecn202607010009",
        "date": "2026.07.01 11:20"
    },
    {
        "category": "🌐 시장 동향",
        "title": "[오늘의 삼전닉스] 증시·수출·세수에 한전까지 커지는 반도체 의존도",
        "url": "https://economist.co.kr/article/view/ecn202609030021",
        "date": "2026.09.03 08:45"
    }
]

st.subheader("📰 이코노미스트 | 반도체 & 전력 인프라 핵심 리포트 아카이브")
st.markdown("이코노미스트(economist.co.kr)에 보도된 반도체 및 전력 인프라 관련 핵심 심층 리포트 모음입니다.")

# 한 줄에 5개씩 배치하고, 기사가 많아지면 자동으로 아랫줄로 내려가도록 동적 렌더링
num_cols = 5
for i in range(0, len(archived_news), num_cols):
    row_news = archived_news[i:i + num_cols]
    cols = st.columns(num_cols)
    
    for j, news in enumerate(row_news):
        with cols[j]:
            st.markdown(f"""
            <div class="news-box">
                <div>
                    <div class="news-category">{news['category']}</div>
                    <div class="news-title"><a href="{news['url']}" target="_blank">{news['title']}</a></div>
                </div>
                <div class="news-date">🕒 입력 {news['date']}</div>
            </div>
            """, unsafe_allow_html=True)
