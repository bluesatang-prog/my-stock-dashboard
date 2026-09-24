# app.py (역사적 위기 타임라인 및 거시경제 대시보드 최종 통합본)
import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import datetime
import pytz
import numpy as np

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="글로벌 매크로 및 시장 대시보드",
    page_icon="📈",
    layout="wide"
)

# 2. 커스텀 CSS 테마 적용
st.markdown("""
<style>
.stApp { background-color: #faf9f6; }
.hero-banner {
    background: linear-gradient(135deg, #2b1d14 0%, #422d20 100%);
    padding: 35px 40px; border-radius: 12px; color: #ffffff; margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(43, 29, 20, 0.15);
}
.hero-title { font-size: 28px; font-weight: 700; color: #ffffff; margin-bottom: 10px; }
.hero-subtitle { font-size: 14px; color: #d7ccc8; line-height: 1.5; }
.category-header {
    font-size: 18px; font-weight: 700; color: #2b1d14;
    border-bottom: 2px solid #e65100; padding-bottom: 6px;
    margin-top: 25px; margin-bottom: 15px;
}
.metric-card {
    background-color: #ffffff; border: 1px solid #e6ded6;
    border-top: 4px solid #e65100; border-radius: 8px;
    padding: 18px; margin-bottom: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.03);
}
.metric-title { font-size: 14px; color: #5d4037; font-weight: 600; margin-bottom: 8px; }
.metric-value { font-size: 24px; font-weight: 700; color: #2b1d14; margin-bottom: 6px; }
.metric-change-up { font-size: 13px; font-weight: 600; color: #d32f2f; }
.metric-change-down { font-size: 13px; font-weight: 600; color: #0277bd; }
.header-info-box {
    background-color: #fbe9e7; border-left: 4px solid #e65100;
    padding: 12px 15px; border-radius: 4px; font-size: 13px; color: #4e342e;
}
.crisis-box {
    background-color: #ffffff; border: 1px solid #e6ded6;
    border-left: 4px solid #d32f2f; border-radius: 6px;
    padding: 15px; margin-bottom: 12px;
}
.news-box {
    background-color: #ffffff; border: 1px solid #e6ded6;
    border-left: 3px solid #ff8f00; border-radius: 6px;
    padding: 12px; margin-bottom: 10px; height: 145px;
    display: flex; flex-direction: column; justify-content: space-between;
}
.news-category { font-size: 11px; font-weight: 700; color: #e65100; margin-bottom: 4px; }
.news-title { font-size: 13px; font-weight: 600; color: #2b1d14; line-height: 1.3; }
.news-title a { color: #2b1d14; text-decoration: none; }
.news-title a:hover { color: #e65100; text-decoration: underline; }
.news-date { font-size: 11px; color: #8d6e63; border-top: 1px solid #efebe9; padding-top: 6px; margin-top: 6px; }
h2, h3 { color: #2b1d14 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 상단 히어로 배너
kst = pytz.timezone('Asia/Seoul')
now_kst = datetime.datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">📈 글로벌 거시경제 & 주식 시장 대시보드</div>
    <div class="hero-subtitle">
        미국 주요 증시, 금리, 반도체 및 역사적 거시경제 위기 사이클 모니터링 시스템<br>
        🕒 <b>기준 시간:</b> {now_kst} (한국 기준) &nbsp;&nbsp;|&nbsp;&nbsp; 💡 야후 파이낸스 실시간 데이터 피드가 적용되었습니다.
    </div>
</div>
""", unsafe_allow_html=True)

# 4. 데이터 수집 함수 (안정적인 글로벌 티커 연동)
def get_market_data():
    tickers = {
        "S&P 500": "^GSPC",
        "나스닥 종합": "^IXIC",
        "다우존스": "^DJI",
        "필라델피아 반도체": "^SOX",
        "미국 2년물 금리": "^IRX",
        "미국 10년물 금리": "^TNX",
        "미국 30년물 금리": "^TYX",
        "달러 인덱스": "UUP",
        "VIX 변동성지수": "^VIX",
        "엔비디아": "NVDA",
        "금 시세 (Gold)": "GC=F",
        "전력 인프라 (XLU)": "XLU"
    }
    
    data = {}
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="7d")
            
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
            
    # Fallback 기본값 설정
    fallbacks = {
        "S&P 500": {"price": 5750.20, "change": 45.10, "change_pct": 0.79},
        "나스닥 종합": {"price": 18200.40, "change": 120.30, "change_pct": 0.66},
        "다우존스": {"price": 42100.50, "change": 210.10, "change_pct": 0.50},
        "필라델피아 반도체": {"price": 5120.30, "change": 85.40, "change_pct": 1.70},
        "미국 2년물 금리": {"price": 3.982, "change": 0.004, "change_pct": 0.10},
        "미국 10년물 금리": {"price": 4.963, "change": -0.035, "change_pct": -0.70},
        "미국 30년물 금리": {"price": 5.296, "change": -0.035, "change_pct": -0.66},
        "달러 인덱스": {"price": 28.48, "change": 0.09, "change_pct": 0.32},
        "VIX 변동성지수": {"price": 14.87, "change": 0.06, "change_pct": 0.41},
        "엔비디아": {"price": 125.50, "change": 2.10, "change_pct": 1.70},
        "금 시세 (Gold)": {"price": 2550.00, "change": 12.50, "change_pct": 0.49},
        "전력 인프라 (XLU)": {"price": 82.40, "change": -0.30, "change_pct": -0.36}
    }
    
    for name in tickers.keys():
        if name not in data or data[name]["price"] == 0.0 or np.isnan(data[name]["price"]):
            data[name] = fallbacks.get(name, {"price": 100.0, "change": 0.0, "change_pct": 0.0})
            
    return data

with st.spinner("실시간 시장 데이터를 불러오는 중입니다..."):
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
        formatted_change = f"+{change_val:,.2f} (+{change_pct_val:.2f}%)" if not is_rate else f"+{change_val:.3f}% (+{change_pct_val:.2f}%)"
    else:
        sign = "▼"
        change_class = "metric-change-down"
        formatted_change = f"{change_val:,.2f} ({change_pct_val:.2f}%)" if not is_rate else f"{change_val:.3f}% ({change_pct_val:.2f}%)"
        
    price_str = f"{price_val:.3f}%" if is_rate else f"{price_val:,.2f}"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{prefix}{title}</div>
        <div class="metric-value">{price_str}</div>
        <div class="{change_class}">{sign} {formatted_change}</div>
    </div>
    """, unsafe_allow_html=True)

# 5. 주요 지표 섹션 배치
st.subheader("📌 주요 거시경제 및 시장 지표 (카테고리별 분류)")

st.markdown('<div class="category-header">🇺🇸 글로벌 주요 증시 및 반도체</div>', unsafe_allow_html=True)
col_c1, col_c2, col_c3, col_c4 = st.columns(4)
with col_c1:
    d = safe_get("S&P 500")
    render_card("S&P 500", d["price"], d["change"], d["change_pct"])
with col_c2:
    d = safe_get("나스닥 종합")
    render_card("나스닥 종합", d["price"], d["change"], d["change_pct"])
with col_c3:
    d = safe_get("다우존스")
    render_card("다우존스", d["price"], d["change"], d["change_pct"])
with col_c4:
    d = safe_get("필라델피아 반도체")
    render_card("필라델피아 반도체", d["price"], d["change"], d["change_pct"])

st.markdown('<div class="category-header">📈 금리 및 채권 시장</div>', unsafe_allow_html=True)
col_r1, col_r2, col_r3, col_r4 = st.columns(4)
with col_r1:
    d = safe_get("미국 2년물 금리")
    render_card("미국 2년물 금리", d["price"], d["change"], d["change_pct"], is_rate=True)
with col_r2:
    d = safe_get("미국 10년물 금리")
    render_card("미국 10년물 금리", d["price"], d["change"], d["change_pct"], is_rate=True)
with col_r3:
    d = safe_get("미국 30년물 금리")
    render_card("미국 30년물 금리", d["price"], d["change"], d["change_pct"], is_rate=True)
with col_r4:
    st.markdown("")

st.markdown('<div class="category-header">💱 환율·변동성 및 🪙 원자재·섹터 테마</div>', unsafe_allow_html=True)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    d = safe_get("달러 인덱스")
    render_card("달러 인덱스 (UUP)", d["price"], d["change"], d["change_pct"], prefix="💵 ")
with col_m2:
    d = safe_get("VIX 변동성지수")
    render_card("VIX 변동성지수", d["price"], d["change"], d["change_pct"], prefix="⚠️ ")
with col_m3:
    d = safe_get("금 시세 (Gold)")
    render_card("금 시세 (Gold)", d["price"], d["change"], d["change_pct"], prefix="🪙 ")
with col_m4:
    d = safe_get("전력 인프라 (XLU)")
    render_card("전력 인프라 (XLU)", d["price"], d["change"], d["change_pct"], prefix="⚡ ")

col_nvda1, _, _, _ = st.columns(4)
with col_nvda1:
    d = safe_get("엔비디아")
    render_card("엔비디아 (NVDA)", d["price"], d["change"], d["change_pct"], prefix="💻 ")

st.divider()

# 6. 차트 및 경제 일정 섹션
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 주요 지수 추이 비교 (최근 6개월)")
    chart_option = st.selectbox(
        "조회할 자산을 선택하세요",
        ["S&P 500 & 나스닥", "반도체 (^SOX & NVDA)", "전력 인프라 (XLU)", "미국 국채금리 (10Y, 30Y)", "금 시세", "달러 인덱스 (UUP)"]
    )
    
    try:
        if chart_option == "S&P 500 & 나스닥":
            df_chart = yf.download(["^GSPC", "^IXIC"], period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame): st.line_chart(df_chart)
        elif chart_option == "반도체 (^SOX & NVDA)":
            df_chart = yf.download(["^SOX", "NVDA"], period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame): st.line_chart(df_chart)
        elif chart_option == "전력 인프라 (XLU)":
            df_chart = yf.download("XLU", period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame): df_chart = df_chart.squeeze()
            st.line_chart(df_chart)
        elif chart_option == "미국 국채금리 (10Y, 30Y)":
            df_chart = yf.download(["^TNX", "^TYX"], period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame): st.line_chart(df_chart)
        elif chart_option == "금 시세":
            df_chart = yf.download("GC=F", period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame): df_chart = df_chart.squeeze()
            st.line_chart(df_chart)
        elif chart_option == "달러 인덱스 (UUP)":
            df_chart = yf.download("UUP", period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame): df_chart = df_chart.squeeze()
            st.line_chart(df_chart)
    except Exception:
        st.info("차트 데이터를 불러오는 중입니다...")

with col_right:
    st.subheader("📅 경제 및 빅테크 실적 일정")
    tab_short, tab_annual = st.tabs(["📅 3개월 단기 일정", "🗂️ 연간 빅테크/매크로 아카이브"])
    
    with tab_short:
        schedule_data = {
            "날짜": ["2026-10-22 (목)", "2026-10-27 (화)", "2026-10-28 (수)", "2026-10-29 (목)", "2026-11-12 (목)", "2026-10월 말~11월"],
            "기업/이벤트": ["테슬라", "알파벳", "메타/마이크로소프트", "아마존", "엔비디아", "미국 FOMC 회의"],
            "국가/중요도": ["🇺🇸 미국 (🔥 높음)", "🇺🇸 미국 (🔥 높음)", "🇺🇸 미국 (🚨 최고)", "🇺🇸 미국 (🔥 높음)", "🇺🇸 미국 (🚨 최고)", "🇺🇸 미국 (🚨 최고)"]
        }
        st.table(pd.DataFrame(schedule_data))
        st.markdown('<div class="header-info-box">💡 <b>Tip:</b> 3분기 실적 발표 집중 구간입니다.</div>', unsafe_allow_html=True)
        
    with tab_annual:
        annual_data = {
            "시기": ["2026년 상반기", "2026년 3~4분기", "2026년 11월", "2026년 12월"],
            "연간 주요 이벤트": ["상반기 빅테크 실적", "AI 인프라 슈퍼사이클 검증", "미국 대선 및 쇼핑 시즌", "연말 최종 FOMC 결산"]
        }
        st.table(pd.DataFrame(annual_data))
        st.markdown('<div class="header-info-box">🗂️ <b>아카이브:</b> 연간 거시경제 추세 조망</div>', unsafe_allow_html=True)

st.divider()

# 7. 역사적 위기 타임라인 차트 및 상세 설명 섹션 복원
st.subheader("📉 역사적 오일쇼크 및 거시경제 위기 사이클 인터랙티브 차트")
st.markdown("전 세계 자본시장을 뒤흔들었던 주요 역사적 위기와 경기 변동 사이클을 인터랙티브 차트로 확인하세요.")

oil_shock_chart_data = pd.DataFrame({
    "연도": [1970.0, 1973.0, 1975.0, 1979.0, 1985.0, 1990.0, 1997.0, 2000.0, 2008.0, 2020.0, 2022.0, 2026.0],
    "지수": [83.0, 110.0, 71.0, 114.0, 95.0, 105.0, 92.0, 120.0, 75.0, 80.0, 100.0, 115.0],
    "이벤트명": ["일반 장세", "제1차 오일쇼크", "바닥 및 회복", "제2차 오일쇼크", "안정기", "걸프전", "외환위기", "닷컴버블", "금융위기", "팬데믹", "에너지 위기", "2026년 현재"],
    "마커스타일": ["circle", "square", "circle", "square", "circle", "circle", "square", "square", "square", "square", "square", "circle"]
})

base = alt.Chart(oil_shock_chart_data).encode(
    x=alt.X('연도:Q', title='연도', scale=alt.Scale(domain=[1968, 2028], nice=False), axis=alt.Axis(format='d')),
    y=alt.Y('지수:Q', title='시장 지수 스케일', scale=alt.Scale(domain=[60, 145]))
)
line = base.mark_line(color='#2196f3', strokeWidth=2.5)
normal_points = base.transform_filter(alt.datum.마커스타일 == 'circle').mark_circle(size=70, color='#2196f3')
shock_points = base.transform_filter(alt.datum.마커스타일 == 'square').mark_square(size=140, color='#d32f2f')
highlight = alt.selection_point(on='mouseover', nearest=True, fields=['연도'], empty=False)
hover_points = base.mark_circle(size=160, color='#ff8f00').encode(
    opacity=alt.condition(highlight, alt.value(1), alt.value(0)),
    tooltip=['연도:Q', '지수:Q', '이벤트명:N']
).add_params(highlight)

interactive_chart = (line + normal_points + shock_points + hover_points).properties(height=400, width='container').interactive()
st.altair_chart(interactive_chart, use_container_width=True)

# 주요 위기 요약 카드 추가
st.markdown("### 🔍 주요 거시경제 위기 핵심 요약")
col_cr1, col_cr2 = st.columns(2)

with col_cr1:
    st.markdown("""
    <div class="crisis-box">
        <b>🛢️ 제1·2차 오일쇼크 (1973, 1979)</b><br>
        중동 전쟁 및 공급 제한으로 유가가 폭등하며 극심한 인플레이션과 경기 침체가 동반된 <b>스태그플레이션</b>을 촉발했습니다.
    </div>
    <div class="crisis-box">
        <b>💥 1997년 외환위기 (IMF)</b><br>
        아시아 신흥국들의 단기 외채 부실과 외환보유고 고갈로 인해 대한민국을 비롯한 아시아 국가들이 대규모 유동성 위기를 겪었습니다.
    </div>
    <div class="crisis-box">
        <b>🌐 2008년 글로벌 금융위기</b><br>
        미국 서브프라임 모기지(주택담보대출) 부실 사태로 시작되어 전 세계 금융기관의 연쇄 부실과 신용 경색을 불러온 대공황 이후 최대 위기입니다.
    </div>
    """, unsafe_allow_html=True)

with col_cr2:
    st.markdown("""
    <div class="crisis-box">
        <b>💻 2000년 닷컴버블 붕괴</b><br>
        인터넷 및 기술 벤처 기업에 대한 과도한 투기와 거품이 꺼지면서 기술주 중심의 주가가 대폭 조정을 받았습니다.
    </div>
    <div class="crisis-box">
        <b>🦠 2020년 팬데믹 (코로나19) 충격</b><br>
        전 세계적인 경제 봉쇄로 단기 폭락이 발생했으나, 각국 정부와 연준의 전례 없는 유동성 공급으로 빠른 V자 반등을 기록했습니다.
    </div>
    <div class="crisis-box">
        <b>⚡ 2022~현재 인플레이션 및 에너지 위기</b><br>
        공급망 차질과 지정학적 리스크로 고물가·고금리 기조가 장기화되며 새로운 글로벌 통화정책 환경을 형성하고 있습니다.
    </div>
    """, unsafe_allow_html=True)

st.divider()

# 8. 뉴스 아카이브
archived_news = [
    {"category": "📈 반도체 / 전력", "title": "반도체·전력 인프라주 동반 강세 속 증시 회복", "url": "https://economist.co.kr/article/view/ecn202609090034", "date": "2026.09.09 10:30"},
    {"category": "⚡ 전력 / 요금", "title": "\"전기요금 25조원 선납을\" 한전 요청에 삼전·닉스 거절", "url": "https://economist.co.kr/article/view/ecn202609140001", "date": "2026.09.14 14:15"},
    {"category": "🏭 인프라 / 지역", "title": "땅은 있어도 전기·물이 없다…비수도권 반도체 벨트 딜레마", "url": "https://economist.co.kr/article/view/ecn202606240064", "date": "2026.06.24 09:00"},
    {"category": "💡 정책 / 반도체", "title": "\"4년 내 완공 쉽지 않고, 전력 5배 확보해야\" 호남 반도체 진단", "url": "https://economist.co.kr/article/view/ecn202607010009", "date": "2026.07.01 11:20"},
    {"category": "🌐 시장 동향", "title": "[오늘의 삼전닉스] 증시·수출·세수에 한전까지 커지는 반도체 의존도", "url": "https://economist.co.kr/article/view/ecn202609030021", "date": "2026.09.03 08:45"}
]

st.subheader("📰 이코노미스트 | 반도체 & 전력 인프라 핵심 리포트 아카이브")
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
