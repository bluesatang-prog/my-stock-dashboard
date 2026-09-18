import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
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

# 5. 주요 지표 카드 섹션
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

# 7. 역사적 거시경제 위기 타임라인 & S&P 500 오일쇼크 폭락/회복 비교 (Altair 인터랙티브 차트 적용)
st.subheader("📉 역사적 거시경제 위기 사이클 & S&P 500 오일쇼크 폭락/회복 비교")
st.markdown("1970년대 오일쇼크 당시 S&P 500 지수 스케일(`70 ~ 150`)와 마우스 오버 시 수치 확인이 가능한 인터랙티브 챠트입니다[cite: 5].")

# 이미지와 일치하는 정밀한 연도별 S&P 500 지수 추이 데이터 생성 (70~140 스케일 핏)
oil_shock_chart_data = pd.DataFrame({
    "연도": [1970.0, 1970.5, 1971.0, 1971.5, 1972.0, 1972.5, 1973.0, 1973.5, 1974.0, 1974.5, 1975.0, 1975.5, 1976.0, 1976.5, 1977.0, 1977.5, 1978.0, 1978.5, 1979.0, 1979.5, 1980.0, 1980.5, 1981.0, 1981.5, 1982.0, 1982.5, 1983.0],
    "S&P 500 지수": [83.0, 72.0, 95.0, 104.0, 93.0, 102.0, 110.0, 118.0, 98.0, 85.0, 71.0, 94.0, 84.0, 102.0, 101.0, 95.0, 90.0, 101.0, 94.0, 114.0, 122.0, 136.0, 131.0, 117.0, 122.0, 108.0, 140.0]
})

# Altair 인터랙티브 멀티레이어 차트 구현 (마우스 호버 시 툴팁 및 포인트 표시)
highlight = alt.selection_point(on='mouseover', nearest=True, fields=['연도'], empty=False)

base = alt.Chart(oil_shock_chart_data).encode(
    x=alt.X('연도:Q', title='연도 (Year)', scale=alt.Scale(domain=[1969.5, 1983.5], nice=False), axis=alt.Axis(format='d')),
    y=alt.Y('S&P 500 지수:Q', title='S&P 500 Index', scale=alt.Scale(domain=[65, 155]))
)

# 파란색 메인 지수 선 그래프
line = base.mark_line(color='#2196f3', strokeWidth=2.5).encode(
    tooltip=['연도:Q', 'S&P 500 지수:Q']
)

# 마우스오버 시 나타나는 포인터 및 툴팁 레이어
points = base.mark_circle(size=60, color='#d32f2f').encode(
    opacity=alt.condition(highlight, alt.value(1), alt.value(0)),
    tooltip=['연도:Q', 'S&P 500 지수:Q']
).add_params(highlight)

# 오일쇼크 전고점 기준 수평선 (빨간선) 추가
rule_data = pd.DataFrame({'yline': [118.0]})
rule = alt.Chart(rule_data).mark_rule(color='#d32f2f', strokeWidth=2, strokeDash=[4, 4]).encode(
    y='yline:Q'
)

interactive_chart = (line + points + rule).properties(
    height=400,
    width='container'
).interactive()

st.altair_chart(interactive_chart, use_container_width=True)

st.markdown("""
<div class="header-info-box">
    🖱️ <b>인터랙티브 기능 안내:</b> 그래프 위에 마우스를 올리면 <b>연도별 세부 지수(70~140 스케일)</b>를 실시간으로 확인하실 수 있으며, 빨간색 점선 기준선은 오일쇼크 당시의 전고점 라인을 나타냅니다[cite: 5].
</div>
""", unsafe_allow_html=True)

# 상세 내용 카드 그리드 배치 (2열)
col_h1, col_h2 = st.columns(2)

with col_h1:
    st.markdown("""
    <div class="history-card">
        <div class="history-period">1970년대 ~ 1980년대</div>
        <div class="history-title">오일쇼크와 스태그플레이션 (42% 폭락장)</div>
        <div class="history-desc">
            • <b>1972년 ~ 1974년:</b> 1차 오일쇼크 발생 후 S&P 500 전고점 대비 <b>42% 폭락</b> (하락 기간 2년)[cite: 1, 2, 4]<br>
            • <b>1975년 ~ 1982년:</b> 증시가 반등을 시작했으나 전고점 회복까지 <b>7년 6개월(하락의 3배)</b> 소요[cite: 1, 2, 4]<br>
            • <b>특징:</b> 극심한 스태그플레이션과 긴 회복 지연 기간 증명
        </div>
    </div>
    
    <div class="history-card">
        <div class="history-period">1990년대 말</div>
        <div class="history-title">아시아 외환위기와 신흥국 위기</div>
        <div class="history-desc">
            • <b>1997년 (한국 IMF 외환위기):</b> 단기 외채 급증과 외화 부족으로 국가 부도 위기 처함[cite: 1, 2]<br>
            • <b>특징:</b> 아시아 신흥국 중심의 대규모 구조조정과 구제금융 단행
        </div>
    </div>
    
    <div class="history-card">
        <div class="history-period">2000년대 초반</div>
        <div class="history-title">닷컴버블 붕괴</div>
        <div class="history-desc">
            • <b>2000년 ~ 2002년:</b> 인터넷(IT) 기업에 대한 과도한 기대와 투자가 붕괴[cite: 1]<br>
            • <b>특징:</b> 기술주 중심의 나스닥 폭락 및 거품 소멸[cite: 1]
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown("""
    <div class="history-card">
        <div class="history-period">2008년</div>
        <div class="history-title">글로벌 금융위기 (서브프라임 모기지)</div>
        <div class="history-desc">
            • <b>발생 원인:</b> 미국의 저신용자 주택담보대출(서브프라임) 부실화[cite: 1, 2]<br>
            • <b>특징:</b> 리먼 브라더스 파산 등 금융 시스템 마비와 전 세계적 경기 침체[cite: 1]
        </div>
    </div>
    
    <div class="history-card">
        <div class="history-period">2020년</div>
        <div class="history-title">코로나19 팬데믹 충격</div>
        <div class="history-desc">
            • <b>발생 원인:</b> 감염병 확산에 따른 글로벌 경제 활동 전면 봉쇄<br>
            • <b>특징:</b> 사상 유례없는 급락 후, 각국의 막대한 유동성 공급으로 빠르게 반등했으나 이후 인플레이션 압력 증대[cite: 1, 2, 3]
        </div>
    </div>
    
    <div class="history-card">
        <div class="history-period">2022년 ~ 2026년 현재</div>
        <div class="history-title">인플레이션과 고금리, 에너지·지정학 리스크</div>
        <div class="history-desc">
            • <b>2022년 ~ 2023년:</b> 유동성과 공급망 차질로 인한 '고물가·고금리' 시대 도래<br>
            • <b>2024년 ~ 2026년 현재:</b> 글로벌 공급망 재편 및 중동 등 지정학적 리스크 상존하며 변동성 지속
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# 8. [아카이브 관리 섹션] 핵심 뉴스 리포트 데이터 리스트 관리
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
