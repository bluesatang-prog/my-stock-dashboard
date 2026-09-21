import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import datetime
import pytz
import requests
from bs4 import BeautifulSoup

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="글로벌 매크로 및 시장 대시보드",
    page_icon="🇰🇷",
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
    <div class="hero-title">🇰🇷 글로벌 거시경제 & 주식 시장 대시보드</div>
    <div class="hero-subtitle">
        대한민국 코스피(네이버 금융 연동), 미국 국채금리, 반도체 및 핵심 경제 지표 실시간 모니터링 시스템<br>
        🕒 <b>기준 시간:</b> {now_kst} (한국 기준) &nbsp;&nbsp;|&nbsp;&nbsp; 💡 코스피는 네이버 금융 실시간 크로링, 해외 지표는 야후 파이낸스를 이용합니다.
    </div>
</div>
""", unsafe_allow_html=True)

# 4. 네이버 금융에서 코스피 실시간 데이터 크롤링 함수
def get_naver_kospi():
    try:
        url = "https://finance.naver.com/sise/sise_index.naver?code=KOSPI"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 코스피 현재지수 크롤링
            now_val_tag = soup.find('em', id='now_value')
            change_val_tag = soup.find('em', id='change_value')
            change_rate_tag = soup.find('em', id='change_rate')
            
            if now_val_tag:
                price = float(now_val_tag.text.replace(',', ''))
                change = 0.0
                change_pct = 0.0
                
                if change_val_tag:
                    change_text = change_val_tag.text.replace(',', '').strip()
                    # 상승/하락 부호 확인
                    parent_span = change_val_tag.find_parent('span')
                    sign = 1
                    if parent_span and 'nv_down' in parent_span.get('class', []):
                        sign = -1
                    change = float(change_text) * sign
                
                if change_rate_tag:
                    rate_text = change_rate_tag.text.replace('%', '').strip()
                    parent_span = change_rate_tag.find_parent('span')
                    sign = 1
                    if parent_span and 'nv_down' in parent_span.get('class', []):
                        sign = -1
                    change_pct = float(rate_text) * sign
                
                return {"price": price, "change": change, "change_pct": change_pct}
    except Exception as e:
        print(f"Naver Kospi Error: {e}")
    return {"price": 0.0, "change": 0.0, "change_pct": 0.0}

# 5. 글로벌 데이터 수집 함수 (야후 파이낸스)
def get_market_data():
    tickers = {
        "미국 2년물 금리": "^IRX",
        "미국 10년물 금리": "^TNX",
        "미국 30년물 금리": "^TYX",
        "달러 인덱스": "UUP",
        "VIX 변동성지수": "^VIX",
        "S&P 500": "^GSPC",
        "나스닥 종합": "^IXIC",
        "필라델피아 반도체": "^SOX",
        "엔비디아": "NVDA",
        "금 시세 (Gold)": "GC=F",
        "전력 인프라 (XLU)": "XLU"
    }
    
    data = {}
    # 코스피는 네이버 금융에서 우선 수집
    data["코스피 지수"] = get_naver_kospi()

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
            
    return data

with st.spinner("네이버 금융 및 야후 파이낸스 실시간 데이터를 불러오는 중입니다..."):
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
    
    html_code = f"""
    <div class="metric-card">
        <div class="metric-title">{prefix}{title}</div>
        <div class="metric-value">{price_str}</div>
        <div class="{change_class}">{sign} {formatted_change}</div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# 6. 주요 지표 섹션 배치
st.subheader("📌 주요 거시경제 및 시장 지표 (카테고리별 분류)")

st.markdown('<div class="category-header">🇰🇷 국내 시장 및 🇺🇸 주요 증시·반도체</div>', unsafe_allow_html=True)
col_c1, col_c2, col_c3, col_c4 = st.columns(4)

with col_c1:
    d = safe_get("코스피 지수")
    render_card("코스피 지수", d["price"], d["change"], d["change_pct"], prefix="🇰🇷 ")

with col_c2:
    d = safe_get("S&P 500")
    render_card("S&P 500", d["price"], d["change"], d["change_pct"])

with col_c3:
    d = safe_get("나스닥 종합")
    render_card("나스닥 종합", d["price"], d["change"], d["change_pct"])

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

# 7. 차트 및 경제 일정 섹션
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 주요 지수 추이 비교 (최근 6개월)")
    chart_option = st.selectbox(
        "조회할 자산을 선택하세요",
        ["코스피 지수 (^KS11)", "S&P 500 & 나스닥", "반도체 (^SOX & NVDA)", "전력 인프라 (XLU)", "미국 국채금리 (10Y, 30Y)", "금 시세", "달러 인덱스 (UUP)"]
    )
    
    try:
        if chart_option == "코스피 지수 (^KS11)":
            df_chart = yf.download("^KS11", period="6mo", progress=False)['Close']
            if isinstance(df_chart, pd.DataFrame): df_chart = df_chart.squeeze()
            st.line_chart(df_chart)
        elif chart_option == "S&P 500 & 나스닥":
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
            "날짜": ["2026-10-22 (목)", "2026-10-27 (화)", "2026-10-28 (수)", "2026-10-29 (목)", "2026-10-29 (목)", "2026-11-12 (목)", "2026-10월 말~11월", "2026-10월 말~11월"],
            "기업/이벤트": ["테슬라", "알파벳", "메타/마이크로소프트", "아마존", "삼성전자/SK하이닉스", "엔비디아", "키옥시아 실적", "미국 FOMC 회의"],
            "국가/중요도": ["🇺🇸 미국 (🔥 높음)", "🇺🇸 미국 (🔥 높음)", "🇺🇸 미국 (🚨 최고)", "🇺🇸 미국 (🔥 높음)", "🇰🇷 대한민국 (🚨 최고)", "🇺🇸 미국 (🚨 최고)", "🇯🇵 일본 (보통)", "🇺🇸 미국 (🚨 최고)"]
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

# 8. 미국 핵심 경제지표 가이드
st.subheader("🇺🇸 미국 핵심 경제지표 가이드")
guide_data = {
    "카테고리": ["통화정책", "물가/소비", "물가/소비", "고용시장", "고용시장", "경기/생산", "경기/생산"],
    "핵심 경제지표": ["FOMC 금리 결정", "소비자물가지수(CPI)", "개인소비지출(PCE)", "비농업 고용 및 실업률", "신규 실업수당 청구", "GDP", "ISM 제조업 PMI"],
    "발표 시기": ["연 8회", "매월 중순", "매월 말", "매월 첫째 주 금요일", "매주 목요일", "분기별", "매월 초"],
    "투자자 해석 방법 및 중요도": [
        "🔥 최고: 연준의 금리 방향성 결정",
        "🔥 매우 높음: 인플레이션 대표 지표",
        "🔥 매우 높음: 연준 신뢰 물가 지표",
        "🔥 매우 높음: 미국 경제 체력 검증",
        "💡 높음: 주간 고용 시장 속보",
        "💡 보통: 실질 경제 성장 확인",
        "💡 보통: 경기 확장/수축 선행 지표"
    ]
}
st.table(pd.DataFrame(guide_data))

st.divider()

# 9. 역사적 위기 타임라인 차트
st.subheader("📉 역사적 오일쇼크 및 거시경제 위기 사이클 인터랙티브 차트")
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

st.divider()

# 10. 뉴스 아카이브
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
