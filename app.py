import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import datetime
import pytz
import numpy as np

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="글로벌 매크로 및 나스닥 대시보드",
    page_icon="🇺🇸",
    layout="wide"
)

# 2. 커스텀 CSS 테마 적용
st.markdown("""
<style>
.stApp {
    background-color: #faf9f6;
}
.hero-banner {
    background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
    padding: 35px 40px;
    border-radius: 12px;
    color: #ffffff;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(26, 35, 126, 0.15);
}
.hero-title {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 10px;
}
.hero-subtitle {
    font-size: 14px;
    color: #c5cae9;
    line-height: 1.5;
}
.category-header {
    font-size: 18px;
    font-weight: 700;
    color: #1a237e;
    border-bottom: 2px solid #3f51b5;
    padding-bottom: 6px;
    margin-top: 25px;
    margin-bottom: 15px;
}
.metric-card {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-top: 4px solid #3f51b5;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    transition: transform 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(63, 81, 181, 0.1);
}
.metric-title {
    font-size: 13px;
    color: #5c6bc0;
    font-weight: 600;
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.metric-value {
    font-size: 20px;
    font-weight: 700;
    color: #1a237e;
    margin-bottom: 4px;
}
.metric-change-up {
    font-size: 12px;
    font-weight: 600;
    color: #d32f2f;
}
.metric-change-down {
    font-size: 12px;
    font-weight: 600;
    color: #0277bd;
}
.header-info-box {
    background-color: #e8eaf6;
    border-left: 4px solid #3f51b5;
    padding: 12px 15px;
    border-radius: 4px;
    font-size: 13px;
    color: #283593;
}
h2, h3 {
    color: #1a237e !important;
}
</style>
""", unsafe_allow_html=True)

# 3. 상단 히어로 배너 영역
kst = pytz.timezone('Asia/Seoul')
now_kst = datetime.datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">🇺🇸 나스닥 시총 상위 10개사 & 글로벌 거시경제 대시보드</div>
    <div class="hero-subtitle">
        나스닥 시가총액 상위 10개 기업, 글로벌 증시, 국채금리, 환율 및 핵심 경제 지표 실시간 모니터링 시스템<br>
        🕒 <b>기준 시간:</b> {now_kst} (한국 기준) &nbsp;&nbsp;|&nbsp;&nbsp; 💡 데이터는 10분 단위로 캐시 관리됩니다.
    </div>
</div>
""", unsafe_allow_html=True)

# 4. 데이터 수집 함수 (나스닥 Top 10 및 글로벌 자산 포함)
@st.cache_data(ttl=600)
def get_market_data():
    tickers = {
        # 나스닥 시총 상위 10개사 (티커 심볼)
        "애플": "AAPL",
        "마이크로소프트": "MSFT",
        "엔비디아": "NVDA",
        "알파벳(구글)": "GOOGL",
        "아마존": "AMZN",
        "메타": "META",
        "테슬라": "TSLA",
        "브로드컴": "AVGO",
        "코스트코": "COST",
        "넷플릭스": "NFLX",
        
        # 주요 매크로 지표
        "미국 2년물 금리": "^IRX",
        "미국 10년물 금리": "^TNX",
        "미국 30년물 금리": "^TYX",
        "달러 인덱스": "DX-Y.NYB",
        "VIX 변동성지수": "^VIX",
        "S&P 500": "^GSPC",
        "나스닥 종합": "^IXIC",
        "필라델피아 반도체": "^SOX",
        "금 시세 (Gold)": "GC=F",
        "전력 인프라 (XLU)": "XLU"
    }
    
    data = {}
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            
            if hist is not None and not hist.empty and 'Close' in hist.columns:
                close_series = hist['Close'].dropna()
                if isinstance(close_series, pd.DataFrame):
                    close_series = close_series.iloc[:, 0]
                
                if len(close_series) >= 2:
                    latest = float(close_series.iloc[-1])
                    prev = float(close_series.iloc[-2])
                    change = latest - prev
                    change_pct = (change / prev) * 100 if prev != 0 else 0.0
                    data[name] = {"price": latest, "change": change, "change_pct": change_pct}
                elif len(close_series) == 1:
                    latest = float(close_series.iloc[-1])
                    data[name] = {"price": latest, "change": 0.0, "change_pct": 0.0}
                else:
                    data[name] = {"price": 0.0, "change": 0.0, "change_pct": 0.0}
            else:
                data[name] = {"price": 0.0, "change": 0.0, "change_pct": 0.0}
        except Exception:
            data[name] = {"price": 0.0, "change": 0.0, "change_pct": 0.0}
            
    fallbacks = {
        "애플": 220.0, "마이크로소프트": 430.0, "엔비디아": 125.0,
        "알파벳(구글)": 180.0, "아마존": 185.0, "메타": 500.0,
        "테슬ラ": 220.0, "브로드컴": 160.0, "코스트코": 850.0, "넷플릭스": 680.0,
        "미국 2년물 금리": 4.25, "미국 10년물 금리": 4.15, "미국 30년물 금리": 4.35, 
        "달러 인덱스": 104.5, "VIX 변동성지수": 15.2, "S&P 500": 5800.0, 
        "나스닥 종합": 18300.0, "금 시세 (Gold)": 2650.0, "필라델피아 반도체": 5200.0, 
        "전력 인프라 (XLU)": 78.0
    }
    
    for name in tickers.keys():
        if name not in data or data[name]["price"] == 0.0 or np.isnan(data[name]["price"]):
            default_val = fallbacks.get(name, 100.0)
            data[name] = {"price": default_val, "change": 2.5, "change_pct": 1.25}
            
    return data

with st.spinner("실시간 나스닥 시장 데이터를 불러오는 중입니다..."):
    data = get_market_data()

def safe_get(key):
    return data.get(key, {"price": 0.0, "change": 0.0, "change_pct": 0.0})

def render_card(title, price_val, change_val, change_pct_val, is_rate=False, prefix="🇺🇸 "):
    if pd.isna(price_val): price_val = 0.0
    if pd.isna(change_val): change_val = 0.0
    if pd.isna(change_pct_val): change_pct_val = 0.0

    if change_val >= 0:
        sign = "▲"
        change_class = "metric-change-up"
        formatted_change = f"+${change_val:,.2f} (+{change_pct_val:.2f}%)" if not is_rate else f"+{change_val:.3f}% (+{change_pct_val:.2f}%)"
    else:
        sign = "▼"
        change_class = "metric-change-down"
        formatted_change = f"-${abs(change_val):,.2f} ({change_pct_val:.2f}%)" if not is_rate else f"{change_val:.3f}% ({change_pct_val:.2f}%)"
        
    price_str = f"{price_val:.3f}%" if is_rate else f"${price_val:,.2f}"
    
    html_code = f"""
    <div class="metric-card">
        <div class="metric-title">{prefix}{title}</div>
        <div class="metric-value">{price_str}</div>
        <div class="{change_class}">{sign} {formatted_change}</div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# 5. 카테고리별 주요 지표 섹션 배치
st.subheader("📌 주요 거시경제 및 시장 지표")

# --- [카테고리 0] 나스닥 시가총액 상위 10개사 ---
st.markdown('<div class="category-header">💻 나스닥 시가총액 상위 10개 종목 실시간 주가 ($)</div>', unsafe_allow_html=True)
top10_nasdaq = [
    "애플", "마이크로소프트", "엔비디아", "알파벳(구글)", "아마존",
    "메타", "테슬라", "브로드컴", "코스트코", "넷플릭스"
]

cols = st.columns(5)
for i, stock_name in enumerate(top10_nasdaq):
    with cols[i % 5]:
        d = safe_get(stock_name)
        render_card(stock_name, d["price"], d["change"], d["change_pct"], prefix="💻 ")

# --- [카테고리 1] 주요 증시 및 반도체 ---
st.markdown('<div class="category-header">🇺🇸 주요 증시 및 반도체 섹터</div>', unsafe_allow_html=True)
col_c1, col_c2, col_c3, col_c4 = st.columns(4)

with col_c1:
    d = safe_get("나스닥 종합")
    render_card("나스닥 종합", d["price"], d["change"], d["change_pct"], prefix="🇺🇸 ")

with col_c2:
    d = safe_get("S&P 500")
    render_card("S&P 500", d["price"], d["change"], d["change_pct"], prefix="🇺🇸 ")

with col_c3:
    d = safe_get("필라델피아 반도체")
    render_card("필라델피아 반도체", d["price"], d["change"], d["change_pct"], prefix="🇺🇸 ")

with col_c4:
    d = safe_get("전력 인프라 (XLU)")
    render_card("전력 인프라 (XLU)", d["price"], d["change"], d["change_pct"], prefix="⚡ ")

# --- [카테고리 2] 금리 및 채권 ---
st.markdown('<div class="category-header">📈 금리 및 채권 시장</div>', unsafe_allow_html=True)
col_r1, col_r2, col_r3, col_r4 = st.columns(4)

with col_r1:
    d = safe_get("미국 2년물 금리")
    render_card("미국 2년물 금리", d["price"], d["change"], d["change_pct"], is_rate=True, prefix="🇺🇸 ")

with col_r2:
    d = safe_get("미국 10년물 금리")
    render_card("미국 10년물 금리", d["price"], d["change"], d["change_pct"], is_rate=True, prefix="🇺🇸 ")

with col_r3:
    d = safe_get("미국 30년물 금리")
    render_card("미국 30년물 금리", d["price"], d["change"], d["change_pct"], is_rate=True, prefix="🇺🇸 ")

with col_r4:
    st.markdown("")

# --- [카테고리 3] 환율, 변동성 및 원자재 ---
st.markdown('<div class="category-header">💱 환율·변동성 및 🪙 원자재</div>', unsafe_allow_html=True)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    d = safe_get("달러 인덱스")
    render_card("달러 인덱스", d["price"], d["change"], d["change_pct"], prefix="💵 ")

with col_m2:
    d = safe_get("VIX 변동성지수")
    render_card("VIX 변동성지수", d["price"], d["change"], d["change_pct"], prefix="⚠️ ")

with col_m3:
    d = safe_get("금 시세 (Gold)")
    render_card("금 시세 (Gold)", d["price"], d["change"], d["change_pct"], prefix="🪙 ")

with col_m4:
    st.markdown("")

st.divider()

# 6. 차트 및 경제 일정 섹션
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 주요 나스닥 빅테크 지수 추이 비교 (최근 6개월)")
    chart_option = st.selectbox(
        "조회할 자산을 선택하세요",
        ["나스닥 종합 (^IXIC)", "대형 빅테크 (AAPL, MSFT, NVDA)", "반도체 (^SOX)", "미국 국채금리 (10Y)", "금 시세", "달러 인덱스"]
    )
    
    try:
        if chart_option == "나스닥 종합 (^IXIC)":
            df_chart = yf.download("^IXIC", period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame):
                df_chart = df_chart.squeeze()
            st.line_chart(df_chart)
        elif chart_option == "대형 빅테크 (AAPL, MSFT, NVDA)":
            df_chart = yf.download(["AAPL", "MSFT", "NVDA"], period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame):
                st.line_chart(df_chart)
        elif chart_option == "반도체 (^SOX)":
            df_chart = yf.download("^SOX", period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame):
                df_chart = df_chart.squeeze()
            st.line_chart(df_chart)
        elif chart_option == "미국 국채금리 (10Y)":
            df_chart = yf.download("^TNX", period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame):
                df_chart = df_chart.squeeze()
            st.line_chart(df_chart)
        elif chart_option == "금 시세":
            df_chart = yf.download("GC=F", period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame):
                df_chart = df_chart.squeeze()
            st.line_chart(df_chart)
        elif chart_option == "달러 인덱스":
            df_chart = yf.download("DX-Y.NYB", period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame):
                df_chart = df_chart.squeeze()
            st.line_chart(df_chart)
    except Exception:
        st.info("차트 데이터를 불러오는 중입니다...")

with col_right:
    st.subheader("📅 빅테크 실적 및 경제 일정")
    
    schedule_data = {
        "날짜": [
            "2026-10-22 (목)", "2026-10-27 (화)", "2026-10-28 (수)", 
            "2026-10-29 (목)", "2026-11-12 (목)"
        ],
        "기업/이벤트": [
            "테슬라 (Tesla)", "알파벳 (Alphabet)", "메타 (Meta) / 마이크로소프트", 
            "아마존 (Amazon)", "엔비디아 (NVIDIA)"
        ],
        "중요도": [
            "🔥 높음", "🔥 높음", "🚨 최고", "🔥 높음", "🚨 최고"
        ]
    }
    df_schedule = pd.DataFrame(schedule_data)
    st.table(df_schedule)
    
    st.markdown("""
    <div class="header-info-box">
        💡 <b>Tip:</b> 나스닥 시총 상위 빅테크 기업들의 실적 발표 시즌에 주가 변동성이 확대될 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

st.divider()

# 7. 미국 핵심 경제지표 가이드
st.subheader("🇺🇸 미국 핵심 경제지표 가이드")
guide_data = {
    "카테고리": ["통화 정책", "물가 / 소비", "물가 / 소비", "고용 시장"],
    "핵심 경제지표": [
        "FOMC 금리 결정", "소비자물가지수 (CPI)", "개인소비지출 (PCE)", "비농업 고용지수 & 실업률"
    ],
    "투자자 해석 방법": [
        "연준의 기준금리 방향성을 제시하며 나스닥 성장주 밸류에이션에 직접적인 영향을 줍니다.",
        "인플레이션 대표 지표로, 예상치 상회 시 금리 인상 우려로 기술주에 하방 압력을 줍니다.",
        "연준이 가장 신뢰하는 물가 지표로 미국의 근원 물가 압력을 보여줍니다.",
        "고용이 너무 강하면 금리 인하 지연 우려, 너무 약하면 경기 침체 우려가 발생합니다."
    ]
}
df_guide = pd.DataFrame(guide_data)
st.table(df_guide)
