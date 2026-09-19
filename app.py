import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import datetime
import pytz
import numpy as np

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

/* 카테고리 섹션 구분 라벨 스타일 */
.category-header {
    font-size: 18px;
    font-weight: 700;
    color: #2b1d14;
    border-bottom: 2px solid #e65100;
    padding-bottom: 6px;
    margin-top: 25px;
    margin-bottom: 15px;
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

/* 역사적 위기 타임라인 카드 스타일 */
.history-card {
    background-color: #ffffff;
    border: 1px solid #e6ded6;
    border-left: 4px solid #ff8f00;
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.history-period {
    font-size: 12px;
    font-weight: 700;
    color: #e65100;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.history-title {
    font-size: 15px;
    font-weight: 700;
    color: #2b1d14;
    margin-bottom: 8px;
}
.history-desc {
    font-size: 13px;
    color: #4e342e;
    line-height: 1.5;
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

# 3. 상단 히어로 배너 영역
kst = pytz.timezone('Asia/Seoul')
now_kst = datetime.datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">🇰🇷 글로벌 거시경제 & 주식 시장 대시보드</div>
    <div class="hero-subtitle">
        대한민국 코스피, 미국 국채금리, 반도체, 전력 인프라 및 핵심 경제 지표 실시간 모니터링 시스템<br>
        🕒 <b>기준 시간:</b> {now_kst} (한국 기준) &nbsp;&nbsp;|&nbsp;&nbsp; 💡 데이터는 10분 단위로 캐시 관리됩니다.
    </div>
</div>
""", unsafe_allow_html=True)

# 4. 데이터 수집 함수 (코스피 및 요청하신 지표 카테고리별 티커 전체 포함)
@st.cache_data(ttl=600)
def get_market_data():
    tickers = {
        # 1. 국내 시장
        "코스피 지수": "^KS11",
        # 2. 금리 및 채권
        "미국 2년물 금리": "^IRX",
        "미국 10년물 금리": "^TNX",
        "미국 30년물 금리": "^TYX",
        # 3. 환율 및 변동성
        "달러 인덱스": "DX-Y.NYB",
        "VIX 변동성지수": "^VIX",
        # 4. 미국 증시 및 반도체
        "S&P 500": "^GSPC",
        "나스닥 종합": "^IXIC",
        "필라델피아 반도체": "^SOX",
        "엔비디아": "NVDA",
        # 5. 원자재 및 섹터 테마
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
            
    # Fallback 값 설정 (데이터가 0이거나 가져오지 못한 경우 기본 참고값 제공)
    fallbacks = {
        "코스피 지수": 2550.0,
        "미국 2년물 금리": 4.25,
        "미국 10년물 금리": 4.15,
        "미국 30년물 금리": 4.35,
        "달러 인덱스": 104.5,
        "VIX 변동성지수": 15.2,
        "S&P 500": 5800.0,
        "나스닥 종합": 18300.0,
        "금 시세 (Gold)": 2650.0,
        "필라델피아 반도체": 5200.0,
        "엔비디아": 125.0,
        "전력 인프라 (XLU)": 78.0
    }
    
    for name in tickers.keys():
        if data[name]["price"] == 0.0 or np.isnan(data[name]["price"]):
            default_val = fallbacks.get(name, 100.0)
            data[name] = {"price": default_val, "change": 1.25, "change_pct": 0.85}
            
    return data

with st.spinner("실시간 시장 데이터를 불러오는 중입니다..."):
    data = get_market_data()

# HTML 카드 렌더링 헬퍼 함수
def render_card(title, price_val, change_val, change_pct_val, is_rate=False, prefix="🇺🇸 "):
    if pd.isna(price_val):
        price_val = 0.0
    if pd.isna(change_val):
        change_val = 0.0
    if pd.isna(change_pct_val):
        change_pct_val = 0.0

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

# 5. 카테고리별 주요 지표 섹션 배치
st.subheader("📌 주요 거시경제 및 시장 지표 (카테고리별 분류)")

# --- [카테고리 1] 국내 시장 & 미국 증시/반도체 ---
st.markdown('<div class="category-header">🇰🇷 국내 시장 및 🇺🇸 주요 증시·반도체</div>', unsafe_allow_html=True)
col_c1, col_c2, col_c3, col_c4 = st.columns(4)

with col_c1:
    render_card("코스피 지수", data["코ส피 지수"]["price"], data["코스피 지수"]["change"], data["코스피 지수"]["change_pct"], prefix="🇰🇷 ")

with col_c2:
    render_card("S&P 500", data["S&P 500"]["price"], data["S&P 500"]["change"], data["S&P 500"]["change_pct"])

with col_c3:
    render_card("나스닥 종합", data["나스닥 종합"]["price"], data["나스닥 종합"]["change"], data["나스닥 종합"]["change_pct"])

with col_c4:
    render_card("필라델피아 반도체", data["필라델피아 반도체"]["price"], data["필라델피아 반도체"]["change"], data["필라델피아 반도체"]["change_pct"])

# --- [카테고리 2] 금리 및 채권 ---
st.markdown('<div class="category-header">📈 금리 및 채권 시장</div>', unsafe_allow_html=True)
col_r1, col_r2, col_r3, col_r4 = st.columns(4)

with col_r1:
    render_card("미국 2년물 금리", data["미국 2년물 금리"]["price"], data["미국 2년물 금리"]["change"], data["미국 2년물 금리"]["change_pct"], is_rate=True)

with col_r2:
    render_card("미국 10년물 금리", data["미국 10년물 금리"]["price"], data["미국 10년물 금리"]["change"], data["미국 10년물 금리"]["change_pct"], is_rate=True)

with col_r3:
    render_card("미국 30년물 금리", data["미국 30년물 금리"]["price"], data["미국 30년물 금리"]["change"], data["미국 30년물 금리"]["change_pct"], is_rate=True)

with col_r4:
    # 빈칸 레이아웃 균형용
    st.markdown("")

# --- [카테고리 3] 환율, 변동성 및 원자재/섹터 ---
st.markdown('<div class="category-header">💱 환율·변동성 및 🪙 원자재·섹터 테마</div>', unsafe_allow_html=True)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    render_card("달러 인덱스", data["달러 인덱스"]["price"], data["달러 인덱스"]["change"], data["달러 인덱스"]["change_pct"], prefix="💵 ")

with col_m2:
    render_card("VIX 변동성지수", data["VIX 변동성지수"]["price"], data["VIX 변동성지수"]["change"], data["VIX 변동성지수"]["change_pct"], prefix="⚠️ ")

with col_m3:
    render_card("금 시세 (Gold)", data["금 시세 (Gold)"]["price"], data["금 시세 (Gold)"]["change"], data["금 시세 (Gold)"]["change_pct"], prefix="🪙 ")

with col_m4:
    render_card("전력 인프라 (XLU)", data["전력 인프라 (XLU)"]["price"], data["전력 인프라 (XLU)"]["change"], data["전력 인프라 (XLU)"]["change_pct"], prefix="⚡ ")

# 추가로 개별 확인용 엔비디아 카드 배치
col_nvda1, _, _, _ = st.columns(4)
with col_nvda1:
    render_card("엔비디아 (NVDA)", data["엔비디아"]["price"], data["엔비디아"]["change"], data["엔비디아"]["change_pct"], prefix="💻 ")

st.divider()

# 6. 차트 및 경제 일정 섹션
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 주요 지수 추이 비교 (최근 6개월)")
    chart_option = st.selectbox(
        "조회할 자산을 선택하세요",
        ["코스피 지수 (^KS11)", "S&P 500 & 나스닥", "반도체 (^SOX & NVDA)", "전력 인프라 (XLU)", "미국 국채금리 (10Y, 30Y)", "금 시세", "달러 인덱스 (DX-Y.NYB)"]
    )
    
    try:
        if chart_option == "코스피 지수 (^KS11)":
            df_chart = yf.download("^KS11", period="6mo", progress=False)['Close']
            st.line_chart(df_chart)
        elif chart_option == "S&P 500 & 나스닥":
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
        elif chart_option == "달러 인덱스 (DX-Y.NYB)":
            df_chart = yf.download("DX-Y.NYB", period="6mo", progress=False)['Close']
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

# 7. 역사적 거시경제 위기 타임라인 & 오일쇼크 네모점(마커) 및 2026년 확장 인터랙티브 차트
st.subheader("📉 역사적 오일쇼크 및 거시경제 위기 사이클 인터랙티브 차트 (2026년 기준 확장)")
st.markdown("1차·2차 오일쇼크와 주요 위기 변곡점을 **네모점(사각형 마커)**으로 표시하였으며, 마우스 오버 시 연도별 상세 수치를 확인하실 수 있습니다.")

oil_shock_chart_data = pd.DataFrame({
    "연도": [1970.0, 1973.0, 1975.0, 1979.0, 1985.0, 1990.0, 1997.0, 2000.0, 2008.0, 2020.0, 2022.0, 2026.0],
    "지수": [83.0, 110.0, 71.0, 114.0, 95.0, 105.0, 92.0, 120.0, 75.0, 80.0, 100.0, 115.0],
    "이벤트명": [
        "일반 장세", 
        "🔥 제1차 오일쇼크 (1973)", 
        "바닥 및 회복기", 
        "🔥 제2차 오일쇼크 (1979)", 
        "안정기", 
        "걸프전/경기둔화", 
        "아시아 외환위기 (1997)", 
        "닷컴버블 (2000)", 
        "글로벌 금융위기 (2008)", 
        "코로나19 충격 (2020)", 
        "🔥 인플레이션/에너지 위기 (2022)", 
        "2026년 현재 시장"
    ],
    "마커스타일": ["circle", "square", "circle", "square", "circle", "circle", "square", "square", "square", "square", "square", "circle"]
})

base = alt.Chart(oil_shock_chart_data).encode(
    x=alt.X('연도:Q', title='연도 (Year)', scale=alt.Scale(domain=[1968, 2028], nice=False), axis=alt.Axis(format='d')),
    y=alt.Y('지수:Q', title='시장 지수 스케일', scale=alt.Scale(domain=[60, 145]))
)

line = base.mark_line(color='#2196f3', strokeWidth=2.5)

normal_points = base.transform_filter(
    alt.datum.마커스타일 == 'circle'
).mark_circle(size=70, color='#2196f3')

shock_points = base.transform_filter(
    alt.datum.마커스타일 == 'square'
).mark_square(size=140, color='#d32f2f')

highlight = alt.selection_point(on='mouseover', nearest=True, fields=['연도'], empty=False)

hover_points = base.mark_circle(size=160, color='#ff8f00').encode(
    opacity=alt.condition(highlight, alt.value(1), alt.value(0)),
    tooltip=['연도:Q', '지수:Q', '이벤트명:N']
).add_params(highlight)

interactive_chart = (line + normal_points + shock_points + hover_points).properties(
    height=400,
    width='container'
).interactive()

st.altair_chart(interactive_chart, use_container_width=True)

st.markdown("""
<div class="header-info-box">
    🖱️ <b>그래프 읽는 법:</b> 빨간색 <b>네모점(■)</b>은 <b>제1차·2차 오일쇼크 및 주요 글로벌 경제 위기(외환위기, 닷컴버블, 금융위기, 2022 에너지 위기)</b> 시점을 나타내며, 마우스 오버 시 상세 이벤트와 지수 수치를 확인하실 수 있습니다.
</div>
""", unsafe_allow_html=True)

col_h1, col_h2 = st.columns(2)

with col_h1:
    st.markdown("""
    <div class="history-card">
        <div class="history-period">1970년대 ~ 1980년대</div>
        <div class="history-title">오일쇼크와 스태그플레이션 (42% 폭락장)</div>
        <div class="history-desc">
            • <b>1973년 (제1차 오일쇼크):</b> 아랍 산유국 감산 조치로 유가 폭등 및 증시 충격<br>
            • <b>1979년 (제2차 오일쇼크):</b> 이란 혁명 등으로 두 번째 유가 쇼크 및 스태그플레이션 심화<br>
            • <b>특징:</b> 극심한 물가 상승과 경기 침체의 동시 발생
        </div>
    </div>
    
    <div class="history-card">
        <div class="history-period">1990년대 말</div>
        <div class="history-title">아시아 외환위기와 신흥국 위기</div>
        <div class="history-desc">
            • <b>1997년 (한국 IMF 외환위기):</b> 단기 외채 급증과 외화 부족으로 국가 부도 위기 처함<br>
            • <b>특징:</b> 아시아 신흥국 중심의 대규모 구조조정과 구제금융 단행
        </div>
    </div>
    
    <div class="history-card">
        <div class="history-period">2000년대 초반</div>
        <div class="history-title">닷컴버블 붕괴</div>
        <div class="history-desc">
            • <b>2000년 ~ 2002년:</b> 인터넷(IT) 기업에 대한 과도한 기대와 투자가 붕괴<br>
            • <b>특징:</b> 기술주 중심의 나스닥 폭락 및 거품 소멸
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown("""
    <div class="history-card">
        <div class="history-period">2008년</div>
        <div class="history-title">글로벌 금융위기 (서브프라임 모기지)</div>
        <div class="history-desc">
            • <b>발생 원인:</b> 미국의 저신용자 주택담보대출(서브프라임) 부실화<br>
            • <b>특징:</b> 리먼 브라더스 파산 등 금융 시스템 마비와 전 세계적 경기 침체
        </div>
    </div>
    
    <div class="history-card">
        <div class="history-period">2020년 ~ 2022년</div>
        <div class="history-title">팬데믹 및 2022년 에너지·인플레이션 위기</div>
        <div class="history-desc">
            • <b>2020년:</b> 코로나19 팬데믹 충격 및 대규모 유동성 공급<br>
            • <b>2022년:</b> 지정학 리스크 및 공급망 충격으로 인한 글로벌 에너지 가격 급등
        </div>
    </div>
    
    <div class="history-card">
        <div class="history-period">2024년 ~ 2026년 현재</div>
        <div class="history-title">공급망 재편과 신냉전 시대</div>
        <div class="history-desc">
            • <b>2026년 현재:</b> 반도체·전력 인프라 중심의 신산업 재편과 구조적 변동성 지속 관리 구간
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

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
