from __future__ import annotations

import os
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


# =============================================================================
# 01. 기본 설정
# =============================================================================
PROJECT_DIR = Path(__file__).resolve().parent

AI_DATA_CANDIDATES = [
    PROJECT_DIR / "output" / "mydata_v6" / "customer_financial_health_with_ai.csv.gz",
    PROJECT_DIR / "output" / "customer_financial_health_with_ai.csv.gz",
]

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "fintech_realistic_class")

st.set_page_config(
    page_title="MyData 자산현황",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =============================================================================
# 02. 모바일 금융앱 스타일
# =============================================================================
st.markdown(
    """
<style>
:root{
    --bg:#f3f5f7;
    --card:#ffffff;
    --text:#171b20;
    --muted:#677381;
    --line:#e8ebee;
    --mint:#00a88f;
    --mint2:#00977f;
    --mint-soft:#e7f7f4;
    --blue:#5969f4;
    --blue-soft:#eef0ff;
    --pink:#eb3d83;
    --orange:#f5b313;
    --green:#3b941e;
    --danger:#df4c58;
}
html,body,[class*="css"]{
    font-family:Pretendard,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
.stApp{background:var(--bg);color:var(--text);}
.block-container{
    max-width:760px;
    padding:1rem 1rem 6rem;
}
#MainMenu,footer,header{visibility:hidden;}
div[data-testid="stSelectbox"] label{display:none;}
div[data-baseweb="select"]>div{
    background:white!important;
    border:1px solid #e4e8ec!important;
    border-radius:15px!important;
    min-height:46px!important;
}
div[data-testid="stRadio"]>div{
    background:#fff;
    padding:.35rem;
    border-radius:16px;
    box-shadow:0 5px 18px rgba(25,35,45,.035);
    gap:.25rem;
}
div[data-testid="stRadio"] label{
    border-radius:12px;
    padding:.32rem .5rem;
    font-weight:800;
}
div[data-testid="stRadio"] label:has(input:checked){
    background:var(--mint-soft);
    color:#087b6a;
}
.stAlert{border-radius:18px;}

.app-head{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin:.2rem 0 .8rem;
}
.app-title{
    font-size:2rem;
    font-weight:950;
    letter-spacing:-.05em;
}
.app-badge{
    background:var(--mint-soft);
    color:#078272;
    font-weight:900;
    padding:.5rem .75rem;
    border-radius:14px;
    font-size:.86rem;
}
.subline{
    font-size:.78rem;
    color:#87919b;
    margin-top:-.35rem;
    margin-bottom:.8rem;
}

.hero{
    background:#fff;
    border-radius:26px;
    padding:1.55rem 1.4rem;
    margin:.8rem 0 1rem;
    box-shadow:0 9px 26px rgba(26,35,45,.045);
}
.hero-label{
    font-size:1.08rem;
    font-weight:900;
}
.hero-money{
    font-size:2.2rem;
    font-weight:950;
    letter-spacing:-.055em;
    margin:.45rem 0 .25rem;
}
.hero-sub{
    color:var(--muted);
    font-size:.84rem;
    line-height:1.55;
}
.hero-row{
    display:flex;
    flex-wrap:wrap;
    gap:.42rem;
    margin-top:.8rem;
}
.chip{
    display:inline-flex;
    align-items:center;
    padding:.42rem .65rem;
    border-radius:999px;
    font-size:.78rem;
    font-weight:850;
}
.chip-mint{background:var(--mint-soft);color:#087d6c;}
.chip-blue{background:var(--blue-soft);color:#4c5ee7;}
.chip-gray{background:#f0f2f4;color:#67727f;}
.chip-pink{background:#fff0f6;color:#ce3472;}

.section{
    font-size:1.4rem;
    font-weight:950;
    letter-spacing:-.045em;
    margin:1.7rem 0 .72rem;
}
.card{
    background:#fff;
    border-radius:25px;
    padding:1.35rem 1.3rem;
    margin:.72rem 0;
    box-shadow:0 8px 24px rgba(25,35,45,.04);
}
.card-blue{
    background:#eaf4ff;
    border-radius:25px;
    padding:1.3rem;
    margin:.72rem 0;
}
.card-title{
    font-size:1.15rem;
    font-weight:930;
    letter-spacing:-.025em;
}
.card-desc{
    color:var(--muted);
    font-size:.84rem;
    line-height:1.55;
}
.big-number{
    font-size:1.85rem;
    font-weight:950;
    letter-spacing:-.045em;
    margin:.35rem 0 .1rem;
}
.delta-down{color:var(--blue);font-weight:900;}
.delta-up{color:var(--pink);font-weight:900;}
.mint{color:var(--mint);}

.asset-line{
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:1rem;
    padding:1rem 0;
    border-bottom:1px solid #edf0f2;
}
.asset-line:last-child{border-bottom:none;}
.asset-left{}
.asset-name{
    font-size:1.05rem;
    font-weight:900;
}
.asset-count{
    color:var(--mint);
    font-weight:900;
}
.asset-value{
    text-align:right;
    font-size:1.08rem;
    font-weight:900;
}
.asset-note{
    margin-top:.32rem;
    background:#f5f6f7;
    border-radius:15px;
    padding:.72rem .85rem;
    font-size:.82rem;
    color:#34404a;
}

.grid2{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:.72rem;
}
.mini{
    background:#fff;
    border-radius:22px;
    padding:1rem;
    box-shadow:0 7px 20px rgba(25,35,45,.035);
}
.mini-label{
    color:#4e5965;
    font-size:.86rem;
    font-weight:850;
}
.mini-value{
    margin-top:.34rem;
    font-size:1.32rem;
    font-weight:950;
    letter-spacing:-.035em;
}
.mini-note{
    color:var(--muted);
    font-size:.76rem;
    margin-top:.25rem;
    line-height:1.4;
}

.divider{
    height:1px;
    background:var(--line);
    margin:1rem 0;
}
.feature{
    display:flex;
    justify-content:space-between;
    gap:1rem;
    padding:.72rem 0;
    border-bottom:1px solid #edf0f2;
    font-size:.87rem;
}
.feature:last-child{border-bottom:none;}
.feature-key{color:#65717e;}
.feature-val{font-weight:900;text-align:right;}

.asset-layout{
    display:grid;
    grid-template-columns:155px 1fr;
    gap:1rem;
    align-items:center;
}
.donut{
    width:145px;height:145px;border-radius:50%;position:relative;margin:auto;
}
.donut:after{
    content:"";
    position:absolute;
    inset:34px;
    background:#fff;
    border-radius:50%;
}
.legend{
    display:flex;
    justify-content:space-between;
    gap:.5rem;
    align-items:center;
    padding:.3rem 0;
    font-size:.83rem;
}
.legend-left{
    display:flex;
    align-items:center;
    gap:.4rem;
    color:#5f6b78;
}
.dot{width:9px;height:9px;border-radius:50%;}

.bar-area{
    height:165px;
    display:flex;
    align-items:flex-end;
    gap:10px;
    margin-top:1rem;
    border-bottom:2px solid #edf0f2;
}
.bar-item{
    flex:1;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:flex-end;
    height:100%;
}
.bar{
    width:70%;
    min-width:20px;
    background:#d9f3ef;
    border:2px solid #00a88f;
    border-bottom:none;
    border-radius:12px 12px 0 0;
}
.bar.latest{background:#00a88f;}
.bar-label{
    font-size:.73rem;
    color:#697583;
    margin-top:.35rem;
    white-space:nowrap;
}
.pnl{
    display:flex;
    justify-content:space-between;
    gap:.6rem;
    align-items:center;
    padding:.75rem 0;
    border-bottom:1px solid #edf0f2;
}
.pnl:last-child{border-bottom:none;}
.pnl-name{font-weight:900;}
.pnl-value{text-align:right;font-weight:900;}

.score-row{
    display:flex;
    justify-content:space-between;
    align-items:flex-end;
    gap:1rem;
}
.score{
    font-size:2.75rem;
    font-weight:950;
    letter-spacing:-.06em;
}
.score small{
    color:var(--muted);
    font-size:.95rem;
    font-weight:850;
}
.grade{
    color:var(--mint);
    font-size:1.2rem;
    font-weight:950;
}
.track{
    height:10px;
    border-radius:100px;
    background:#edf0f2;
    overflow:hidden;
    margin-top:.8rem;
}
.fill{
    height:100%;
    background:linear-gradient(90deg,#0db69a,#47ccb7);
    border-radius:100px;
}
.action{
    display:flex;
    gap:.75rem;
    align-items:flex-start;
    padding:.85rem 0;
    border-bottom:1px solid #edf0f2;
}
.action:last-child{border-bottom:none;}
.action-no{
    width:28px;height:28px;flex:0 0 28px;
    display:flex;align-items:center;justify-content:center;
    border-radius:50%;
    background:var(--mint-soft);
    color:#087d6c;
    font-weight:950;
}
.action-text{
    font-size:.9rem;
    font-weight:750;
    line-height:1.5;
}
.footer{
    color:#89939e;
    text-align:center;
    font-size:.74rem;
    line-height:1.55;
    margin:1.5rem 0;
}
@media(max-width:600px){
    .block-container{padding-left:.75rem;padding-right:.75rem;}
    .hero-money{font-size:1.85rem;}
    .asset-layout{grid-template-columns:130px 1fr;}
    .donut{width:125px;height:125px;}
    .donut:after{inset:30px;}
}
</style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# 03. 공통 유틸리티
# =============================================================================
def safe_num(value, default=np.nan) -> float:
    value = pd.to_numeric(value, errors="coerce")
    return float(value) if pd.notna(value) else float(default)


def won(value: float, short: bool = False) -> str:
    if not np.isfinite(value):
        return "-"
    sign = "-" if value < 0 else ""
    a = abs(value)

    if short:
        if a >= 100_000_000:
            return f"{sign}{a / 100_000_000:.1f}억원"
        if a >= 10_000:
            return f"{sign}{a / 10_000:,.0f}만원"
    return f"{value:,.0f}원"


def pct(value: float, digits: int = 1) -> str:
    if not np.isfinite(value):
        return "-"
    return f"{value * 100:.{digits}f}%"


def clamp(value: float, low=0.0, high=100.0) -> float:
    if not np.isfinite(value):
        return 0.0
    return float(np.clip(value, low, high))


def feature_row(key: str, value: str) -> str:
    return (
        f'<div class="feature">'
        f'<span class="feature-key">{escape(str(key))}</span>'
        f'<span class="feature-val">{escape(str(value))}</span>'
        f'</div>'
    )


def find_ai_path() -> Path | None:
    for path in AI_DATA_CANDIDATES:
        if path.exists():
            return path
    return None


# =============================================================================
# 04. DB 연결
# =============================================================================
@st.cache_resource
def get_engine():
    url = URL.create(
        "mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        query={"charset": "utf8mb4"},
    )
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=1800,
    )


@st.cache_data(ttl=600, show_spinner=False)
def query_df(sql: str, params_tuple: tuple = ()) -> pd.DataFrame:
    params = dict(params_tuple)
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


def one_row(sql: str, cid: int) -> pd.Series:
    df = query_df(sql, (("cid", int(cid)),))
    return df.iloc[0] if not df.empty else pd.Series(dtype="object")


def ensure_numeric_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """숫자 연산이 필요한 컬럼만, 실제 dtype이 숫자형이 아닐 때 변환합니다."""
    for col in columns:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def ensure_datetime_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """날짜 연산이 필요한 컬럼만, datetime형이 아닐 때 변환합니다."""
    if column in df.columns and not pd.api.types.is_datetime64_any_dtype(df[column]):
        df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


# =============================================================================
# 05. AI 결과 CSV (선택)
# =============================================================================
@st.cache_data(show_spinner=False)
def load_ai_data(path_text: str) -> pd.DataFrame:
    # MVP 화면에서 실제 사용하는 AI 결과 컬럼만 읽습니다.
    # usecols를 callable로 지정하면 파일에 일부 선택 컬럼이 없어도 오류 없이 건너뜁니다.
    needed_cols = {
        "customer_id",
        "financial_health_score",
        "financial_health_grade",
        "next_month_stress_probability",
        "ai_stress_level",
        "ai_recommendation",
        "diagnosis_summary",
        "score_cashflow",
        "score_liquidity",
        "score_debt",
        "score_spending",
        "score_saving",
        "score_investment",
        "score_family_burden",
        "score_resilience",
    }
    df = pd.read_csv(path_text, usecols=lambda col: col in needed_cols)

    if "customer_id" in df.columns and not pd.api.types.is_numeric_dtype(df["customer_id"]):
        df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")

    numeric_cols = [
        "financial_health_score",
        "next_month_stress_probability",
        "score_cashflow",
        "score_liquidity",
        "score_debt",
        "score_spending",
        "score_saving",
        "score_investment",
        "score_family_burden",
        "score_resilience",
    ]
    ensure_numeric_columns(df, numeric_cols)
    return df


# =============================================================================
# 06. 고객별 DB 데이터 조회
# =============================================================================
SQL_CUSTOMERS = """
SELECT
    c.customer_id,
    c.name,
    c.region
FROM customers c
ORDER BY c.customer_id
LIMIT 5000
"""

# 상단 총자산 카드와 여러 화면에서 공통으로 쓰는 값은 상세 행 전체를 읽지 않고
# DB에서 집계한 1행만 가져옵니다. 고객을 바꿀 때 가장 먼저 실행되는 쿼리입니다.
SQL_OVERVIEW = """
SELECT
    COALESCE((
        SELECT SUM(a.balance)
        FROM accounts a
        WHERE a.customer_id = :cid
          AND UPPER(a.currency) = 'KRW'
    ), 0) AS deposit_krw,

    COALESCE((
        SELECT SUM(ia.cash_balance)
        FROM investment_accounts ia
        WHERE ia.customer_id = :cid
    ), 0) AS investment_cash,

    COALESCE((
        SELECT SUM(sp.current_value)
        FROM customer_stock_positions sp
        WHERE sp.customer_id = :cid
    ), 0) AS stock_value,

    COALESCE((
        SELECT SUM(re.estimated_value)
        FROM customer_real_estate re
        WHERE re.customer_id = :cid
    ), 0) AS real_estate_value,

    COALESCE(
        (
            SELECT ds.total_financial_debt
            FROM customer_debt_summary ds
            WHERE ds.customer_id = :cid
            LIMIT 1
        ),
        (
            SELECT SUM(l.outstanding_balance)
            FROM loans l
            WHERE l.customer_id = :cid
        ),
        0
    ) AS total_debt,

    (SELECT COUNT(*) FROM accounts a WHERE a.customer_id = :cid) AS account_count,
    (SELECT COUNT(*) FROM investment_accounts ia WHERE ia.customer_id = :cid) AS investment_account_count,
    (SELECT COUNT(DISTINCT sp.stock_code) FROM customer_stock_positions sp WHERE sp.customer_id = :cid) AS stock_count,
    (SELECT COUNT(*) FROM loans l WHERE l.customer_id = :cid) AS loan_count,
    (SELECT COUNT(*) FROM customer_real_estate re WHERE re.customer_id = :cid) AS real_estate_count,
    (SELECT COUNT(*) FROM cards c WHERE c.customer_id = :cid) AS card_count,

    COALESCE((
        SELECT SUM(c.available_limit)
        FROM cards c
        WHERE c.customer_id = :cid
    ), 0) AS available_card_limit,

    COALESCE((
        SELECT MAX(l.overdue_days)
        FROM loans l
        WHERE l.customer_id = :cid
    ), 0) AS max_overdue_days,

    (
        SELECT COUNT(*)
        FROM loans l
        WHERE l.customer_id = :cid
          AND l.maturity_date >= CURDATE()
          AND l.maturity_date <= DATE_ADD(CURDATE(), INTERVAL 1 YEAR)
    ) AS maturing_1y,

    (
        SELECT GROUP_CONCAT(DISTINCT UPPER(a.currency) ORDER BY UPPER(a.currency) SEPARATOR ',')
        FROM accounts a
        WHERE a.customer_id = :cid
          AND UPPER(a.currency) <> 'KRW'
    ) AS fx_currencies,

    (
        SELECT cf.net_cashflow
        FROM customer_monthly_cashflow cf
        WHERE cf.customer_id = :cid
        ORDER BY cf.month DESC
        LIMIT 1
    ) AS latest_net_cashflow,

    (
        SELECT AVG(recent_cf.total_outflow)
        FROM (
            SELECT cf.total_outflow
            FROM customer_monthly_cashflow cf
            WHERE cf.customer_id = :cid
            ORDER BY cf.month DESC
            LIMIT 6
        ) AS recent_cf
    ) AS avg_outflow_6m,

    (
        SELECT CASE
            WHEN SUM(GREATEST(COALESCE(sp.current_value, 0), 0)) > 0 THEN
                SUM(POWER(GREATEST(COALESCE(sp.current_value, 0), 0), 2)) /
                POWER(SUM(GREATEST(COALESCE(sp.current_value, 0), 0)), 2)
            ELSE NULL
        END
        FROM customer_stock_positions sp
        WHERE sp.customer_id = :cid
    ) AS stock_hhi
"""

# 금융건강 화면에서 실제 표시하는 프로필 컬럼만 조회합니다.
SQL_PROFILE = """
SELECT
    age,
    employment_type,
    household_annual_income,
    credit_score,
    investment_risk_profile
FROM customer_financial_profiles
WHERE customer_id = :cid
LIMIT 1
"""

# 투자 화면과 자산 화면의 종목 구성·손익 계산에 필요한 컬럼만 조회합니다.
SQL_STOCKS = """
SELECT
    stock_code,
    company_name,
    industry,
    purchase_price_actual_close,
    quantity,
    current_value,
    unrealized_return_rate,
    momentum_6m
FROM customer_stock_positions
WHERE customer_id = :cid
ORDER BY current_value DESC
"""

# 자산 화면의 최근 자금흐름 그래프에 필요한 12개월 데이터만 조회합니다.
SQL_CASHFLOW = """
SELECT
    month,
    total_outflow,
    net_cashflow,
    month_end_balance
FROM customer_monthly_cashflow
WHERE customer_id = :cid
ORDER BY month DESC
LIMIT 12
"""

# 금융건강/AI 진단에서 사용하는 부채 지표만 조회합니다.
SQL_DEBT = """
SELECT
    total_financial_debt,
    dsr_income,
    housing_education_burden_ratio,
    debt_to_asset
FROM customer_debt_summary
WHERE customer_id = :cid
LIMIT 1
"""

# 실제 DB의 Serving용 AI 결과 요약 테이블입니다.
SQL_AI_HEALTH = """
SELECT
    financial_health_score,
    financial_health_grade,
    next_month_stress_probability,
    ai_stress_level,
    ai_recommendation,
    diagnosis_summary,
    score_cashflow,
    score_liquidity,
    score_debt,
    score_spending,
    score_saving,
    score_investment,
    score_family_burden,
    score_resilience
FROM customer_health_summary
WHERE customer_id = :cid
LIMIT 1
"""

# 소비 화면에서 카드별 사용 비중의 표시 이름을 만들 때 필요한 컬럼만 조회합니다.
SQL_CARDS = """
SELECT
    card_id,
    card_brand,
    card_type
FROM cards
WHERE customer_id = :cid
ORDER BY card_id
"""

# 소비 분석에 필요한 최근 90일 계좌 거래만 DB에서 직접 제한해 가져옵니다.
SQL_TRANSACTIONS = """
SELECT
    transaction_at,
    transaction_type,
    amount,
    channel,
    transaction_status,
    fraud_label
FROM transactions
WHERE customer_id = :cid
  AND transaction_at >= DATE_SUB(
      (SELECT MAX(t2.transaction_at)
       FROM transactions t2
       WHERE t2.customer_id = :cid),
      INTERVAL 90 DAY
  )
ORDER BY transaction_at DESC
"""

# 소비 분석에 필요한 최근 90일 승인 카드결제만 조회합니다.
SQL_CARD_PAYMENTS = """
SELECT
    cp.card_id,
    cp.payment_at,
    cp.amount,
    cp.is_overseas,
    cp.is_online,
    cp.installment_months,
    cp.fraud_label,
    cp.expense_category,
    m.merchant_name,
    m.merchant_category
FROM card_payments cp
LEFT JOIN merchants m
    ON cp.merchant_id = m.merchant_id
WHERE cp.customer_id = :cid
  AND cp.is_approved = 1
  AND cp.payment_at >= DATE_SUB(
      (SELECT MAX(cp2.payment_at)
       FROM card_payments cp2
       WHERE cp2.customer_id = :cid
         AND cp2.is_approved = 1),
      INTERVAL 90 DAY
  )
ORDER BY cp.payment_at DESC
"""


# =============================================================================
# 07. 시각화 함수
# =============================================================================
def donut_html(items: list[tuple[str, float, str]]) -> str:
    clean = [
        (name, max(float(value), 0.0), color)
        for name, value, color in items
        if np.isfinite(value) and value > 0
    ]
    total = sum(v for _, v, _ in clean)
    if total <= 0:
        return '<div class="card-desc">표시할 자산 데이터가 없습니다.</div>'

    stops = []
    legends = []
    start = 0.0

    for name, value, color in clean:
        share = value / total * 100
        end = start + share
        stops.append(f"{color} {start:.2f}% {end:.2f}%")
        legends.append(
            f'<div class="legend">'
            f'<span class="legend-left"><span class="dot" style="background:{color}"></span>{escape(name)}</span>'
            f'<strong>{share:.1f}%</strong>'
            f'</div>'
        )
        start = end

    return (
        '<div class="asset-layout">'
        f'<div class="donut" style="background:conic-gradient({", ".join(stops)});"></div>'
        f'<div>{"".join(legends)}</div>'
        '</div>'
    )


def bars_html(cashflow: pd.DataFrame) -> str:
    if cashflow.empty or "month_end_balance" not in cashflow.columns:
        return '<div class="card-desc">월별 잔액 데이터가 없습니다.</div>'

    hist = cashflow.copy()
    hist["month"] = pd.to_datetime(hist["month"], errors="coerce")
    hist["month_end_balance"] = pd.to_numeric(hist["month_end_balance"], errors="coerce")
    hist = hist.dropna(subset=["month", "month_end_balance"]).sort_values("month").tail(6)

    if hist.empty:
        return '<div class="card-desc">월별 잔액 데이터가 없습니다.</div>'

    vals = hist["month_end_balance"].clip(lower=0)
    vmax = max(float(vals.max()), 1.0)

    parts = ['<div class="bar-area">']
    for i, (_, r) in enumerate(hist.iterrows()):
        value = max(safe_num(r["month_end_balance"], 0), 0)
        height = max(8, value / vmax * 92)
        latest = " latest" if i == len(hist) - 1 else ""
        label = f"{int(r['month'].month)}월"
        parts.append(
            f'<div class="bar-item">'
            f'<div class="bar{latest}" style="height:{height:.1f}%;" title="{won(value)}"></div>'
            f'<div class="bar-label">{label}</div>'
            f'</div>'
        )
    parts.append("</div>")
    return "".join(parts)


def radar_svg(values: list[float], labels: list[str]) -> str:
    values = [clamp(v) for v in values]
    cx, cy, radius = 150.0, 132.0, 90.0
    angles = np.deg2rad([-90, 30, 150])

    def pts(vs):
        out = []
        for val, angle in zip(vs, angles):
            rr = radius * (val / 100)
            x = cx + rr * np.cos(angle)
            y = cy + rr * np.sin(angle)
            out.append(f"{x:.1f},{y:.1f}")
        return " ".join(out)

    grids = "".join(
        f'<polygon points="{pts([level]*3)}" fill="none" stroke="#dde2e6" stroke-width="1.4"/>'
        for level in (33, 66, 100)
    )
    label_positions = [(150, 20), (268, 218), (32, 218)]
    texts = "".join(
        f'<text x="{x}" y="{y}" text-anchor="middle" font-size="15" font-weight="700" fill="#3f4851">{escape(label)}</text>'
        for label, (x, y) in zip(labels, label_positions)
    )

    return f"""
<svg viewBox="0 0 300 240" width="100%" role="img">
    {grids}
    <polygon points="{pts(values)}"
             fill="rgba(0,168,143,.20)"
             stroke="#00a88f"
             stroke-width="3"/>
    {texts}
</svg>
"""


def pnl_top3_html(stocks: pd.DataFrame) -> str:
    if stocks.empty:
        return '<div class="card-desc">보유 주식 데이터가 없습니다.</div>'

    s = stocks.copy()
    for c in ["current_value", "quantity", "purchase_price_actual_close"]:
        s[c] = pd.to_numeric(s[c], errors="coerce")

    s["cost_value"] = s["quantity"] * s["purchase_price_actual_close"]
    s["pnl"] = s["current_value"] - s["cost_value"]
    s = s.dropna(subset=["pnl"]).assign(abs_pnl=lambda x: x["pnl"].abs())
    s = s.sort_values("abs_pnl", ascending=False).head(3)

    if s.empty:
        return '<div class="card-desc">손익을 계산할 수 있는 주식 데이터가 없습니다.</div>'

    html = []
    for _, r in s.iterrows():
        pnl = safe_num(r["pnl"], 0)
        cls = "delta-up" if pnl >= 0 else "delta-down"
        arrow = "▲" if pnl >= 0 else "▼"
        html.append(
            f'<div class="pnl">'
            f'<div><div class="pnl-name">{escape(str(r.get("company_name", r.get("stock_code", ""))))}</div>'
            f'<div class="card-desc">{escape(str(r.get("stock_code", "")))}</div></div>'
            f'<div class="pnl-value">{won(safe_num(r.get("current_value"), 0))}'
            f'<div class="{cls}" style="margin-top:.25rem;">{arrow} {won(abs(pnl))}</div></div>'
            f'</div>'
        )
    return "".join(html)




def category_bars_html(series: pd.Series, max_items: int = 6) -> str:
    s = pd.to_numeric(series, errors="coerce").dropna()
    s = s[s > 0].sort_values(ascending=False).head(max_items)
    if s.empty:
        return '<div class="card-desc">표시할 지출 데이터가 없습니다.</div>'

    total = float(s.sum())
    max_value = float(s.max()) if len(s) else 1.0
    parts = []
    for name, value in s.items():
        share = value / total * 100 if total > 0 else 0
        width = max(4.0, value / max_value * 100)
        parts.append(
            f'<div style="margin:.82rem 0;">'
            f'<div style="display:flex;justify-content:space-between;gap:.7rem;font-size:.85rem;">'
            f'<strong>{escape(str(name))}</strong>'
            f'<span>{won(float(value))} · {share:.1f}%</span></div>'
            f'<div class="track" style="height:9px;margin-top:.34rem;">'
            f'<div class="fill" style="width:{width:.1f}%"></div></div>'
            f'</div>'
        )
    return "".join(parts)


def account_type_label(value: object) -> str:
    raw = str(value or "기타").strip()
    key = raw.upper().replace("-", "_").replace(" ", "_")
    mapping = {
        "TRANSFER_OUT": "이체/송금",
        "OUT_TRANSFER": "이체/송금",
        "WITHDRAWAL": "현금인출",
        "ATM_WITHDRAWAL": "현금인출",
        "PAYMENT": "계좌결제",
        "AUTOPAY": "자동이체",
        "AUTO_PAYMENT": "자동이체",
        "DIRECT_DEBIT": "자동이체",
        "FEE": "수수료",
    }
    return mapping.get(key, raw)


def card_category_label(value: object) -> str:
    raw = str(value or "기타").strip()
    key = raw.upper().replace("-", "_").replace(" ", "_")
    mapping = {
        "FOOD": "식비", "DINING": "외식", "RESTAURANT": "외식",
        "GROCERY": "장보기", "GROCERIES": "장보기",
        "SHOPPING": "쇼핑", "RETAIL": "쇼핑",
        "TRANSPORT": "교통", "TRANSPORTATION": "교통",
        "EDUCATION": "교육", "MEDICAL": "의료", "HEALTH": "의료",
        "TRAVEL": "여행", "ENTERTAINMENT": "문화/여가",
        "UTILITIES": "공과금", "TELECOM": "통신",
        "CAFE": "카페", "COFFEE": "카페",
        "ACCOMMODATION": "숙박", "FUEL": "주유",
        "ETC": "기타", "OTHER": "기타",
    }
    return mapping.get(key, raw)


def prepare_account_spending(transactions: pd.DataFrame, days: int = 90) -> pd.DataFrame:
    if transactions.empty:
        return transactions.copy()

    x = transactions.copy()
    ensure_datetime_column(x, "transaction_at")
    ensure_numeric_columns(x, ["amount"])
    x = x.dropna(subset=["transaction_at", "amount"])

    if "fraud_label" in x.columns:
        fraud = pd.to_numeric(x["fraud_label"], errors="coerce").fillna(0)
        x = x[fraud.eq(0)]

    if "transaction_status" in x.columns:
        status = x["transaction_status"].astype(str).str.lower()
        failed = status.str.contains("fail|cancel|reject|declin|실패|취소|거절", regex=True, na=False)
        x = x[~failed]

    if x.empty:
        return x

    type_text = x["transaction_type"].astype(str).str.lower()
    out_pattern = r"withdraw|transfer.?out|out.?transfer|debit|payment|autopay|direct.?debit|fee|출금|송금|지출|결제|자동이체|이체출"
    in_pattern = r"deposit|transfer.?in|in.?transfer|credit|salary|income|interest|입금|급여|수입|이자"

    negative_amount = x["amount"] < 0
    explicit_out = type_text.str.contains(out_pattern, regex=True, na=False)
    explicit_in = type_text.str.contains(in_pattern, regex=True, na=False)
    x = x[negative_amount | (explicit_out & ~explicit_in)].copy()

    if x.empty:
        return x

    latest = x["transaction_at"].max()
    x = x[x["transaction_at"] >= latest - pd.Timedelta(days=days)].copy()
    x["spend_amount"] = x["amount"].abs()
    x["spend_category"] = x["transaction_type"].map(account_type_label)
    x["channel_clean"] = x["channel"].fillna("기타").astype(str).replace("", "기타")
    x["is_weekend"] = x["transaction_at"].dt.dayofweek >= 5
    x["month"] = x["transaction_at"].dt.to_period("M").astype(str)
    return x


def prepare_card_spending(payments: pd.DataFrame, days: int = 90) -> pd.DataFrame:
    if payments.empty:
        return payments.copy()

    x = payments.copy()
    ensure_datetime_column(x, "payment_at")
    ensure_numeric_columns(x, ["amount"])
    x = x.dropna(subset=["payment_at", "amount"])
    x = x[x["amount"] > 0].copy()

    if "fraud_label" in x.columns:
        fraud = pd.to_numeric(x["fraud_label"], errors="coerce").fillna(0)
        x = x[fraud.eq(0)]

    if x.empty:
        return x

    latest = x["payment_at"].max()
    x = x[x["payment_at"] >= latest - pd.Timedelta(days=days)].copy()

    expense = x.get("expense_category", pd.Series(index=x.index, dtype="object"))
    merchant_cat = x.get("merchant_category", pd.Series(index=x.index, dtype="object"))
    expense = expense.replace(r"^\s*$", np.nan, regex=True)
    merchant_cat = merchant_cat.replace(r"^\s*$", np.nan, regex=True)
    x["spend_category"] = expense.fillna(merchant_cat).fillna("기타").map(card_category_label)
    x["is_online"] = pd.to_numeric(x.get("is_online", 0), errors="coerce").fillna(0).astype(int)
    x["is_overseas"] = pd.to_numeric(x.get("is_overseas", 0), errors="coerce").fillna(0).astype(int)
    x["installment_months"] = pd.to_numeric(x.get("installment_months", 0), errors="coerce").fillna(0)
    x["is_weekend"] = x["payment_at"].dt.dayofweek >= 5
    x["month"] = x["payment_at"].dt.to_period("M").astype(str)
    return x


def tendency_chips_account(spend: pd.DataFrame) -> str:
    if spend.empty:
        return '<span class="chip chip-gray">분석 데이터 부족</span>'
    chips = []
    by_cat = spend.groupby("spend_category")["spend_amount"].sum().sort_values(ascending=False)
    total = float(by_cat.sum())
    if len(by_cat) and total > 0:
        top = str(by_cat.index[0])
        share = float(by_cat.iloc[0] / total)
        chips.append(f'<span class="chip chip-mint">{escape(top)} {share*100:.0f}%</span>')
    by_channel = spend.groupby("channel_clean")["spend_amount"].sum().sort_values(ascending=False)
    if len(by_channel):
        chips.append(f'<span class="chip chip-blue">주요 채널 {escape(str(by_channel.index[0]))}</span>')
    weekend = float(spend["is_weekend"].mean()) if len(spend) else 0
    if weekend >= .35:
        chips.append(f'<span class="chip chip-pink">주말 지출 {weekend*100:.0f}%</span>')
    return "".join(chips)


def tendency_chips_card(spend: pd.DataFrame) -> str:
    if spend.empty:
        return '<span class="chip chip-gray">분석 데이터 부족</span>'
    chips = []
    total = float(spend["amount"].sum())
    by_cat = spend.groupby("spend_category")["amount"].sum().sort_values(ascending=False)
    if len(by_cat) and total > 0:
        top = str(by_cat.index[0])
        share = float(by_cat.iloc[0] / total)
        chips.append(f'<span class="chip chip-mint">{escape(top)} {share*100:.0f}%</span>')
    online = float(spend["is_online"].mean()) if len(spend) else 0
    overseas = float(spend["is_overseas"].mean()) if len(spend) else 0
    installment = float((spend["installment_months"] > 1).mean()) if len(spend) else 0
    chips.append(f'<span class="chip chip-blue">온라인 {online*100:.0f}%</span>')
    if overseas > 0:
        chips.append(f'<span class="chip chip-gray">해외 {overseas*100:.0f}%</span>')
    if installment > 0:
        chips.append(f'<span class="chip chip-pink">할부 {installment*100:.0f}%</span>')
    return "".join(chips)


# =============================================================================
# 08. DB 연결 확인 / 고객 선택
# =============================================================================
try:
    customers = query_df(SQL_CUSTOMERS)
except Exception as exc:
    st.error(
        "MySQL DB에 연결하지 못했습니다.\n\n"
        f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}\n\n"
        f"오류: {exc}"
    )
    st.code(
        "set DB_HOST=127.0.0.1\n"
        "set DB_PORT=3306\n"
        "set DB_USER=root\n"
        "set DB_PASSWORD=비밀번호\n"
        "set DB_NAME=fintech_realistic_class\n\n"
        "streamlit run app.py",
        language="bat",
    )
    st.stop()

if customers.empty:
    st.error("customers 테이블에 표시할 고객이 없습니다.")
    st.stop()

if not pd.api.types.is_numeric_dtype(customers["customer_id"]):
    customers["customer_id"] = pd.to_numeric(customers["customer_id"], errors="coerce")
customers = customers.dropna(subset=["customer_id"])
if not pd.api.types.is_integer_dtype(customers["customer_id"]):
    customers["customer_id"] = customers["customer_id"].astype(int)

customer_map = {}
for _, r in customers.iterrows():
    cid = int(r["customer_id"])
    name = str(r.get("name", "") or "").strip()
    region = str(r.get("region", "") or "").strip()
    label = f"{cid}"
    if name and name.lower() != "nan":
        label += f" · {name}"
    if region and region.lower() != "nan":
        label += f" · {region}"
    customer_map[cid] = label

st.markdown(
    """
<div class="app-head">
    <div class="app-title">자산</div>
    <div class="app-badge">MyData AI</div>
</div>
""",
    unsafe_allow_html=True,
)

selected_customer = st.selectbox(
    "고객",
    list(customer_map.keys()),
    format_func=lambda x: customer_map[x],
    label_visibility="collapsed",
)

st.markdown(
    f'<div class="subline">fintech_realistic_class DB · customer_id {selected_customer}</div>',
    unsafe_allow_html=True,
)


# =============================================================================
# 09. 공통 자산 요약 로드
# =============================================================================
# 고객을 선택하면 먼저 화면 공통으로 필요한 합계/건수만 1행으로 조회합니다.
# 계좌, 주식, 대출 같은 상세 행은 아래에서 선택한 화면에 따라 별도로 읽습니다.
with st.spinner("고객 자산 요약을 불러오는 중..."):
    overview = one_row(SQL_OVERVIEW, selected_customer)

# DB 집계값은 계산에 사용할 때만 숫자로 안전하게 해석합니다.
deposit_krw = safe_num(overview.get("deposit_krw"), 0)
investment_cash = safe_num(overview.get("investment_cash"), 0)
stock_value = safe_num(overview.get("stock_value"), 0)
real_estate_value = safe_num(overview.get("real_estate_value"), 0)
total_debt = safe_num(overview.get("total_debt"), 0)

total_asset = deposit_krw + investment_cash + stock_value + real_estate_value
financial_asset = deposit_krw + investment_cash + stock_value
net_worth = total_asset - total_debt

account_count = int(safe_num(overview.get("account_count"), 0))
investment_account_count = int(safe_num(overview.get("investment_account_count"), 0))
stock_count = int(safe_num(overview.get("stock_count"), 0))
loan_count = int(safe_num(overview.get("loan_count"), 0))
real_estate_count = int(safe_num(overview.get("real_estate_count"), 0))
card_count = int(safe_num(overview.get("card_count"), 0))
available_card_limit = safe_num(overview.get("available_card_limit"), 0)
max_overdue_days = safe_num(overview.get("max_overdue_days"), 0)
maturing_1y = int(safe_num(overview.get("maturing_1y"), 0))
latest_net_cashflow = safe_num(overview.get("latest_net_cashflow"), np.nan)
avg_outflow = safe_num(overview.get("avg_outflow_6m"), np.nan)

liquidity_months_db = (
    max(deposit_krw + investment_cash, 0) / avg_outflow
    if np.isfinite(avg_outflow) and avg_outflow > 0
    else np.nan
)

stock_hhi = safe_num(overview.get("stock_hhi"), np.nan)
diversification = clamp((1 - stock_hhi) * 125) if np.isfinite(stock_hhi) else 0.0

fx_text_raw = str(overview.get("fx_currencies", "") or "").strip()
fx_currencies = [x for x in fx_text_raw.split(",") if x] if fx_text_raw and fx_text_raw.lower() != "nan" else []
fx_text = ", ".join(fx_currencies[:3])
if len(fx_currencies) > 3:
    fx_text += f" 외 {len(fx_currencies)-3}개"


# =============================================================================
# 10. 상단 총자산 카드
# =============================================================================
st.markdown(
    f"""
<div class="hero">
    <div class="hero-label">총 자산</div>
    <div class="hero-money">{won(total_asset)}</div>
    <div class="hero-sub">
        원화 계좌 + 투자예수금 + 주식 평가액 + 부동산 추정가 기준<br>
        외화계좌는 환율 데이터가 없어 총자산 합계에서 제외
    </div>
    <div class="hero-row">
        <span class="chip chip-mint">금융자산 {won(financial_asset, short=True)}</span>
        <span class="chip chip-blue">부채 {won(total_debt, short=True)}</span>
        <span class="chip chip-gray">순자산 {won(net_worth, short=True)}</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# 11. 화면 전환
# =============================================================================
page = st.radio(
    "화면",
    ["자산", "투자", "소비", "금융건강", "AI 진단"],
    horizontal=True,
    label_visibility="collapsed",
)


# =============================================================================
# 12. 선택한 화면에 필요한 상세 데이터만 로드
# =============================================================================
# 각 변수는 해당 화면에서만 실제 DB 조회가 발생합니다.
profile = pd.Series(dtype="object")
debt_summary = pd.Series(dtype="object")
ai_row = pd.Series(dtype="object")
stocks = pd.DataFrame()
cashflow_sorted = pd.DataFrame()
cards = pd.DataFrame()
account_spend_90 = pd.DataFrame()
card_spend_90 = pd.DataFrame()

stock_return = np.nan
growth_score = 50.0
liquidity_score = clamp((liquidity_months_db / 6.0) * 100) if np.isfinite(liquidity_months_db) else 0.0
latest_month_end = np.nan
cash_balance_delta = np.nan

if page == "자산":
    # 자산 화면에서는 종목 손익 Top3와 월별 자금흐름만 상세 행이 필요합니다.
    with st.spinner("자산 상세 데이터를 불러오는 중..."):
        stocks = query_df(SQL_STOCKS, (("cid", selected_customer),))
        cashflow = query_df(SQL_CASHFLOW, (("cid", selected_customer),))

    ensure_numeric_columns(stocks, [
        "current_value", "quantity", "purchase_price_actual_close",
        "unrealized_return_rate", "momentum_6m",
    ])
    ensure_numeric_columns(cashflow, ["total_outflow", "net_cashflow", "month_end_balance"])
    ensure_datetime_column(cashflow, "month")

    cashflow_sorted = cashflow.sort_values("month") if not cashflow.empty else cashflow
    latest_cf = cashflow_sorted.iloc[-1] if not cashflow_sorted.empty else pd.Series(dtype="object")
    prev_cf = cashflow_sorted.iloc[-2] if len(cashflow_sorted) >= 2 else pd.Series(dtype="object")

    latest_month_end = safe_num(latest_cf.get("month_end_balance"), np.nan)
    prev_month_end = safe_num(prev_cf.get("month_end_balance"), np.nan)
    cash_balance_delta = (
        latest_month_end - prev_month_end
        if np.isfinite(latest_month_end) and np.isfinite(prev_month_end)
        else np.nan
    )

elif page == "투자":
    # 투자 화면은 보유 종목 상세만 읽으면 됩니다.
    with st.spinner("투자 데이터를 불러오는 중..."):
        stocks = query_df(SQL_STOCKS, (("cid", selected_customer),))

    ensure_numeric_columns(stocks, [
        "current_value", "quantity", "purchase_price_actual_close",
        "unrealized_return_rate", "momentum_6m",
    ])

    if not stocks.empty:
        cost = (stocks["quantity"] * stocks["purchase_price_actual_close"]).sum()
        if pd.notna(cost) and cost > 0:
            stock_return = (stock_value - cost) / cost

        if stock_value > 0:
            weights = (stocks["current_value"].clip(lower=0) / stock_value).fillna(0)
            hhi = float((weights ** 2).sum())
            diversification = clamp((1 - hhi) * 125)

        temp = stocks[["current_value", "momentum_6m"]].dropna()
        if stock_value > 0 and not temp.empty and temp["current_value"].sum() > 0:
            weighted_momentum = np.average(
                temp["momentum_6m"],
                weights=temp["current_value"].clip(lower=0),
            )
            growth_score = clamp(50 + weighted_momentum * 120)

elif page == "소비":
    # 대량 거래 데이터는 소비 화면을 열었을 때만 조회합니다.
    # SQL 단계에서 이미 최근 90일로 제한되어 있어 불필요한 과거 행을 전송하지 않습니다.
    with st.spinner("최근 90일 소비 데이터를 불러오는 중..."):
        transactions = query_df(SQL_TRANSACTIONS, (("cid", selected_customer),))
        card_payments = query_df(SQL_CARD_PAYMENTS, (("cid", selected_customer),))
        cards = query_df(SQL_CARDS, (("cid", selected_customer),))

    account_spend_90 = prepare_account_spending(transactions, days=90)
    card_spend_90 = prepare_card_spending(card_payments, days=90)

elif page == "금융건강":
    # 금융건강 화면에서는 고객 프로필과 부채 요약만 DB에서 읽습니다.
    with st.spinner("금융건강 데이터를 불러오는 중..."):
        profile = one_row(SQL_PROFILE, selected_customer)
        debt_summary = one_row(SQL_DEBT, selected_customer)

elif page == "AI 진단":
    # AI 진단의 DB 기반 위험 신호는 부채 요약만 추가로 필요합니다.
    with st.spinner("AI 진단용 금융지표를 불러오는 중..."):
        debt_summary = one_row(SQL_DEBT, selected_customer)

# 실제 DB에는 customer_health_summary가 있으므로 DB 결과를 우선 사용합니다.
# 과거 강의안과의 호환을 위해 DB 조회가 실패할 때만 CSV를 fallback으로 읽습니다.
if page in {"투자", "금융건강", "AI 진단"}:
    try:
        ai_row = one_row(SQL_AI_HEALTH, selected_customer)
    except Exception:
        ai_path = find_ai_path()
        if ai_path is not None:
            try:
                ai_df = load_ai_data(str(ai_path))
                matched = ai_df[ai_df["customer_id"].eq(selected_customer)]
                if not matched.empty:
                    ai_row = matched.iloc[-1]
            except Exception:
                pass

# AI 결과 공통 값
health_score = safe_num(ai_row.get("financial_health_score"), np.nan) if len(ai_row) else np.nan
health_grade = str(ai_row.get("financial_health_grade", "") or "").strip() if len(ai_row) else ""
stress_prob = safe_num(ai_row.get("next_month_stress_probability"), np.nan) if len(ai_row) else np.nan
stress_level = str(ai_row.get("ai_stress_level", "") or "").strip() if len(ai_row) else ""
ai_recommendation = str(ai_row.get("ai_recommendation", "") or "").strip() if len(ai_row) else ""
diagnosis_summary = str(ai_row.get("diagnosis_summary", "") or "").strip() if len(ai_row) else ""

if len(ai_row) and np.isfinite(safe_num(ai_row.get("score_liquidity"), np.nan)):
    liquidity_score = clamp(safe_num(ai_row.get("score_liquidity")))


# =============================================================================
# 13. 자산 화면
# =============================================================================
if page == "자산":
    st.markdown('<div class="section">금융자산</div>', unsafe_allow_html=True)

    asset_lines = [
        (
            f"내 계좌 <span class='asset-count'>{account_count}</span>",
            deposit_krw,
            "원화 계좌 잔액",
        ),
        (
            f"투자 <span class='asset-count'>{stock_count}</span>",
            stock_value + investment_cash,
            f"주식 {stock_count}종목 · 투자계좌 {investment_account_count}개",
        ),
        (
            f"대출 <span class='asset-count'>{loan_count}</span>",
            total_debt,
            "현재 금융부채",
        ),
    ]

    if fx_currencies:
        asset_lines.append(
            (
                f"외화 <span class='asset-count'>{len(fx_currencies)}</span>",
                np.nan,
                f"보유통화 {fx_text or '-'} · 환율 미적용",
            )
        )

    html = ['<div class="card">']
    for name, value, note in asset_lines:
        display_value = won(value) if np.isfinite(value) else "환율 미적용"
        html.append(
            f'<div class="asset-line">'
            f'<div class="asset-left"><div class="asset-name">{name}</div>'
            f'<div class="card-desc" style="margin-top:.28rem;">{escape(note)}</div></div>'
            f'<div class="asset-value">{display_value}</div>'
            f'</div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

    st.markdown('<div class="section">계좌 관리</div>', unsafe_allow_html=True)

    delta_html = ""
    if np.isfinite(cash_balance_delta):
        cls = "delta-up" if cash_balance_delta >= 0 else "delta-down"
        arrow = "▲" if cash_balance_delta >= 0 else "▼"
        delta_html = f'<div class="{cls}" style="font-size:1.25rem;margin-top:.2rem;">{arrow} {won(abs(cash_balance_delta))}</div>'

    st.markdown(
        f"""
<div class="card">
    <div class="card-title">자금흐름</div>
    <div class="big-number">{won(latest_month_end)}</div>
    {delta_html}
    <div class="card-desc">최근 월말 잔액 · 전월 대비 변화</div>
    {bars_html(cashflow_sorted)}
</div>
""",
        unsafe_allow_html=True,
    )

    # 만기대출 건수와 카드 가용한도는 공통 요약 SQL에서 이미 집계했습니다.

    st.markdown(
        f"""
<div class="grid2">
    <div class="mini">
        <div class="mini-label">만기</div>
        <div class="mini-value"><span class="mint">{maturing_1y}</span>개</div>
        <div class="mini-note">1년 이내 만기 대출</div>
    </div>
    <div class="mini">
        <div class="mini-label">카드</div>
        <div class="mini-value"><span class="mint">{card_count}</span>개</div>
        <div class="mini-note">가용한도 {won(available_card_limit, short=True)}</div>
    </div>
    <div class="mini">
        <div class="mini-label">최근 순현금흐름</div>
        <div class="mini-value">{won(latest_net_cashflow, short=True)}</div>
        <div class="mini-note">최근 월 수입 - 총지출</div>
    </div>
    <div class="mini">
        <div class="mini-label">유동성</div>
        <div class="mini-value">{liquidity_months_db:.1f}개월</div>
        <div class="mini-note">현금성자산 ÷ 최근 지출</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if real_estate_count:
        st.markdown('<div class="section">실물자산</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="card">
    <div class="asset-line">
        <div>
            <div class="asset-name">부동산 <span class="asset-count">{real_estate_count}</span></div>
            <div class="card-desc" style="margin-top:.3rem;">DB 추정 시가 합계</div>
        </div>
        <div class="asset-value">{won(real_estate_value)}</div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section">자산현황</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="card">
    <div class="card-title">자산변동</div>
    <div class="card-desc">월별 총자산 시계열은 없어, DB에 있는 월말 현금성 잔액 변화를 표시합니다.</div>
    {bars_html(cashflow_sorted)}
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="card">
    <div class="card-title">투자 손익 Top3</div>
    {pnl_top3_html(stocks)}
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="card">
    <div class="card-title">총자산 구성</div>
    {donut_html([
        ("원화 계좌", deposit_krw, "#00a88f"),
        ("투자예수금", investment_cash, "#7e88f7"),
        ("주식", stock_value, "#db59bd"),
        ("부동산", real_estate_value, "#f6b313"),
    ])}
    <div class="divider"></div>
    <div class="card-desc">외화계좌는 환율 정보가 없으므로 비중 계산에서 제외했습니다.</div>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# 14. 투자 화면
# =============================================================================
elif page == "투자":
    st.markdown('<div class="section">투자</div>', unsafe_allow_html=True)

    ret_cls = "delta-up" if np.isfinite(stock_return) and stock_return >= 0 else "delta-down"
    ret_arrow = "▲" if np.isfinite(stock_return) and stock_return >= 0 else "▼"

    st.markdown(
        f"""
<div class="card">
    <div class="card-title">투자수익률</div>
    <div class="big-number">{pct(stock_return)}</div>
    <div class="{ret_cls}" style="font-size:1rem;">{ret_arrow} 보유주식 평가손익 기준</div>
    <div class="card-desc" style="margin-top:.45rem;">매수기준가 × 수량 대비 현재 평가액으로 계산합니다.</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="card">
    <div class="card-title">다각도 분석</div>
    {radar_svg([diversification, growth_score, liquidity_score], ["분산도", "성장성", "유동성"])}
    <div class="card-desc">
        분산도는 보유비중 집중도, 성장성은 6개월 모멘텀,
        유동성은 현금성자산과 지출규모를 이용한 교육용 점수입니다.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section">투자자산구성</div>', unsafe_allow_html=True)

    if stocks.empty:
        st.info("보유 주식이 없습니다.")
    else:
        html = ['<div class="card">']
        total_for_weight = max(stock_value, 1)
        for _, r in stocks.head(8).iterrows():
            val = safe_num(r.get("current_value"), 0)
            weight = val / total_for_weight
            ret = safe_num(r.get("unrealized_return_rate"), np.nan)
            html.append(
                f'<div class="asset-line">'
                f'<div><div class="asset-name">{escape(str(r.get("company_name", r.get("stock_code", ""))))}</div>'
                f'<div class="card-desc">{escape(str(r.get("industry", "")))} · 비중 {weight*100:.1f}%</div></div>'
                f'<div class="asset-value">{won(val)}<div style="font-size:.78rem;color:#677381;margin-top:.2rem;">수익률 {pct(ret)}</div></div>'
                f'</div>'
            )
        html.append("</div>")
        st.markdown("".join(html), unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="card-blue">
    <div class="card-title">AI가 제안하는 맞춤형 자산진단</div>
    <div class="card-desc" style="margin-top:.35rem;">
        보유 종목 집중도와 금융건강 모델 결과를 함께 보고,
        리밸런싱 필요 여부를 점검합니다.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# =============================================================================
# 15. 소비 화면
# =============================================================================
elif page == "소비":
    st.markdown('<div class="section">계좌 지출 성향</div>', unsafe_allow_html=True)

    if account_spend_90.empty:
        st.info(
            "최근 거래에서 출금·송금·결제성 거래를 식별하지 못했습니다. "
            "거래 유형명(transaction_type)을 기반으로 지출성 거래를 구분합니다."
        )
    else:
        acct_total = safe_num(account_spend_90["spend_amount"].sum(), 0)
        acct_avg = safe_num(account_spend_90.groupby("month")["spend_amount"].sum().mean(), 0)
        acct_count = len(account_spend_90)
        acct_avg_ticket = safe_num(account_spend_90["spend_amount"].mean(), 0)
        acct_weekend = safe_num(account_spend_90["is_weekend"].mean(), 0)
        acct_by_category = account_spend_90.groupby("spend_category")["spend_amount"].sum().sort_values(ascending=False)
        acct_by_channel = account_spend_90.groupby("channel_clean")["spend_amount"].sum().sort_values(ascending=False)
        main_channel = escape(str(acct_by_channel.index[0])) if len(acct_by_channel) else "-"

        st.markdown(
            f"""
<div class="card">
    <div class="card-title">최근 90일 계좌 지출</div>
    <div class="big-number">{won(acct_total)}</div>
    <div class="hero-row">{tendency_chips_account(account_spend_90)}</div>
    <div class="card-desc" style="margin-top:.65rem;">
        거래 유형명에서 출금·송금·결제성 거래를 식별하여 분석합니다.
    </div>
</div>
<div class="grid2">
    <div class="mini"><div class="mini-label">월평균 지출</div><div class="mini-value">{won(acct_avg, short=True)}</div><div class="mini-note">최근 90일 월별 합계 평균</div></div>
    <div class="mini"><div class="mini-label">지출 거래</div><div class="mini-value">{acct_count:,}건</div><div class="mini-note">건당 평균 {won(acct_avg_ticket, short=True)}</div></div>
    <div class="mini"><div class="mini-label">주말 지출</div><div class="mini-value">{acct_weekend*100:.0f}%</div><div class="mini-note">지출 건수 기준</div></div>
    <div class="mini"><div class="mini-label">주요 채널</div><div class="mini-value">{main_channel}</div><div class="mini-note">지출금액 기준</div></div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""<div class="card"><div class="card-title">어디로 지출했나요?</div>
            <div class="card-desc">거래유형별 지출 비중</div>
            {category_bars_html(acct_by_category)}</div>""",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""<div class="card"><div class="card-title">어떤 채널을 많이 썼나요?</div>
            <div class="card-desc">채널별 지출금액</div>
            {category_bars_html(acct_by_channel)}</div>""",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section">카드 소비 성향</div>', unsafe_allow_html=True)

    if card_spend_90.empty:
        st.info("최근 90일 승인된 정상 카드결제 데이터가 없습니다.")
    else:
        card_total = safe_num(card_spend_90["amount"].sum(), 0)
        card_avg = safe_num(card_spend_90.groupby("month")["amount"].sum().mean(), 0)
        card_count_90 = len(card_spend_90)
        avg_ticket = safe_num(card_spend_90["amount"].mean(), 0)
        online_ratio = safe_num(card_spend_90["is_online"].mean(), 0)
        overseas_ratio = safe_num(card_spend_90["is_overseas"].mean(), 0)
        installment_ratio = safe_num((card_spend_90["installment_months"] > 1).mean(), 0)
        weekend_ratio = safe_num(card_spend_90["is_weekend"].mean(), 0)
        card_by_category = card_spend_90.groupby("spend_category")["amount"].sum().sort_values(ascending=False)

        st.markdown(
            f"""
<div class="card">
    <div class="card-title">최근 90일 카드 소비</div>
    <div class="big-number">{won(card_total)}</div>
    <div class="hero-row">{tendency_chips_card(card_spend_90)}</div>
    <div class="card-desc" style="margin-top:.65rem;">
        승인된 정상 결제만 포함하며, 소비 카테고리는 expense_category를 우선 사용합니다.
    </div>
</div>
<div class="grid2">
    <div class="mini"><div class="mini-label">월평균 카드소비</div><div class="mini-value">{won(card_avg, short=True)}</div><div class="mini-note">최근 90일 월별 합계 평균</div></div>
    <div class="mini"><div class="mini-label">평균 결제금액</div><div class="mini-value">{won(avg_ticket, short=True)}</div><div class="mini-note">총 {card_count_90:,}건</div></div>
    <div class="mini"><div class="mini-label">온라인 소비</div><div class="mini-value">{online_ratio*100:.0f}%</div><div class="mini-note">결제 건수 기준</div></div>
    <div class="mini"><div class="mini-label">해외 소비</div><div class="mini-value">{overseas_ratio*100:.0f}%</div><div class="mini-note">결제 건수 기준</div></div>
    <div class="mini"><div class="mini-label">할부 이용</div><div class="mini-value">{installment_ratio*100:.0f}%</div><div class="mini-note">2개월 이상 할부</div></div>
    <div class="mini"><div class="mini-label">주말 소비</div><div class="mini-value">{weekend_ratio*100:.0f}%</div><div class="mini-note">결제 건수 기준</div></div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""<div class="card"><div class="card-title">무엇에 가장 많이 썼나요?</div>
            <div class="card-desc">카테고리별 카드 소비금액</div>
            {category_bars_html(card_by_category, max_items=7)}</div>""",
            unsafe_allow_html=True,
        )

        if "merchant_name" in card_spend_90.columns:
            merchants_top = (
                card_spend_90.dropna(subset=["merchant_name"])
                .groupby("merchant_name")["amount"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )
            if not merchants_top.empty:
                st.markdown(
                    f"""<div class="card"><div class="card-title">자주 돈을 쓴 곳</div>
                    <div class="card-desc">가맹점별 결제금액 Top5</div>
                    {category_bars_html(merchants_top, max_items=5)}</div>""",
                    unsafe_allow_html=True,
                )

        if "card_id" in card_spend_90.columns:
            card_amount = card_spend_90.groupby("card_id")["amount"].sum().sort_values(ascending=False)
            if not card_amount.empty:
                card_name_map = {}
                if not cards.empty:
                    for _, r in cards.iterrows():
                        card_key = r.get("card_id")
                        brand = str(r.get("card_brand", "카드") or "카드")
                        ctype = str(r.get("card_type", "") or "")
                        card_name_map[card_key] = f"{brand} {ctype}".strip()
                card_amount.index = [card_name_map.get(idx, f"카드 {idx}") for idx in card_amount.index]
                st.markdown(
                    f"""<div class="card"><div class="card-title">카드별 소비 비중</div>
                    {category_bars_html(card_amount, max_items=5)}</div>""",
                    unsafe_allow_html=True,
                )


# =============================================================================
# 16. 금융건강 화면
# =============================================================================
elif page == "금융건강":
    st.markdown('<div class="section">금융건강</div>', unsafe_allow_html=True)

    if np.isfinite(health_score):
        st.markdown(
            f"""
<div class="card">
    <div class="score-row">
        <div>
            <div class="card-desc">금융건강점수</div>
            <div class="score">{health_score:.0f}<small> / 100</small></div>
        </div>
        <div class="grade">{escape(health_grade or "-")}등급</div>
    </div>
    <div class="track"><div class="fill" style="width:{clamp(health_score):.1f}%"></div></div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.info(
            "금융건강 결과 CSV가 없거나 해당 고객의 모델 결과가 없습니다. "
            "DB 자산현황은 정상 표시되며, 모델 노트북 결과 파일이 있으면 자동 결합됩니다."
        )

    dsr = safe_num(debt_summary.get("dsr_income"), np.nan) if len(debt_summary) else np.nan
    fixed_burden = safe_num(debt_summary.get("housing_education_burden_ratio"), np.nan) if len(debt_summary) else np.nan
    debt_asset = safe_num(debt_summary.get("debt_to_asset"), np.nan) if len(debt_summary) else np.nan
    credit_score = safe_num(profile.get("credit_score"), np.nan) if len(profile) else np.nan

    st.markdown(
        f"""
<div class="grid2">
    <div class="mini">
        <div class="mini-label">다음 달 금융스트레스</div>
        <div class="mini-value">{pct(stress_prob)}</div>
        <div class="mini-note">{escape(stress_level or "모델 결과 없음")}</div>
    </div>
    <div class="mini">
        <div class="mini-label">DSR 성격 지표</div>
        <div class="mini-value">{pct(dsr)}</div>
        <div class="mini-note">소득 대비 연간 채무상환</div>
    </div>
    <div class="mini">
        <div class="mini-label">주거·교육 부담</div>
        <div class="mini-value">{pct(fixed_burden)}</div>
        <div class="mini-note">주거+교육 고정부담</div>
    </div>
    <div class="mini">
        <div class="mini-label">부채 / 자산</div>
        <div class="mini-value">{pct(debt_asset)}</div>
        <div class="mini-note">DB 부채요약 기준</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if len(ai_row):
        score_cols = {
            "현금흐름": "score_cashflow",
            "유동성": "score_liquidity",
            "부채": "score_debt",
            "소비": "score_spending",
            "저축": "score_saving",
            "투자": "score_investment",
            "가족부담": "score_family_burden",
            "회복탄력성": "score_resilience",
        }
        available = []
        for label, col in score_cols.items():
            val = safe_num(ai_row.get(col), np.nan)
            if np.isfinite(val):
                available.append((label, clamp(val)))

        if available:
            st.markdown('<div class="section">영역별 점수</div>', unsafe_allow_html=True)
            html = ['<div class="card">']
            for label, val in available:
                html.append(
                    f'<div style="margin:.78rem 0;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:.86rem;font-weight:850;">'
                    f'<span>{escape(label)}</span><span>{val:.0f}</span></div>'
                    f'<div class="track" style="height:8px;margin-top:.3rem;"><div class="fill" style="width:{val:.1f}%"></div></div>'
                    f'</div>'
                )
            html.append("</div>")
            st.markdown("".join(html), unsafe_allow_html=True)

    st.markdown('<div class="section">고객 프로필</div>', unsafe_allow_html=True)
    profile_html = ['<div class="card">']
    if len(profile):
        profile_html.append(feature_row("나이", f"{int(safe_num(profile.get('age'), 0))}세"))
        profile_html.append(feature_row("고용형태", str(profile.get("employment_type", "-"))))
        profile_html.append(feature_row("가구 연소득", won(safe_num(profile.get("household_annual_income"), np.nan), short=True)))
        profile_html.append(feature_row("신용점수", f"{credit_score:.0f}" if np.isfinite(credit_score) else "-"))
        profile_html.append(feature_row("투자위험성향", str(profile.get("investment_risk_profile", "-"))))
    profile_html.append("</div>")
    st.markdown("".join(profile_html), unsafe_allow_html=True)


# =============================================================================
# 17. AI 진단 화면
# =============================================================================
else:
    st.markdown('<div class="section">AI 맞춤형 자산진단</div>', unsafe_allow_html=True)

    actions = [
        x.strip()
        for x in ai_recommendation.split("|")
        if x.strip() and x.strip().lower() != "nan"
    ]

    if not actions:
        # 모델 결과가 없어도 DB 지표로 "사실 기반 점검 문구"만 제시
        if np.isfinite(liquidity_months_db) and liquidity_months_db < 3:
            actions.append("현금성자산이 최근 지출 3개월치보다 적어 유동성 버퍼를 우선 점검하세요.")
        if np.isfinite(dsr) and dsr >= 0.4:
            actions.append("소득 대비 채무상환 부담이 높아 추가 대출보다 부채 축소를 먼저 검토하세요.")
        if diversification < 45 and stock_count >= 2:
            actions.append("주식 보유 비중이 일부 종목에 집중되어 있어 분산도를 점검하세요.")
        if np.isfinite(latest_net_cashflow) and latest_net_cashflow < 0:
            actions.append("최근 월 순현금흐름이 음수이므로 지출과 고정비를 우선 점검하세요.")
        if not actions:
            actions.append("현재 DB 지표에서는 우선 경고할 만한 주요 신호가 확인되지 않았습니다.")

    html = ['<div class="card"><div class="card-title">이번 달 우선 점검</div>']
    for i, action in enumerate(actions, 1):
        html.append(
            f'<div class="action"><div class="action-no">{i}</div>'
            f'<div class="action-text">{escape(action)}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

    st.markdown('<div class="section">핵심 위험 신호</div>', unsafe_allow_html=True)

    dsr = safe_num(debt_summary.get("dsr_income"), np.nan) if len(debt_summary) else np.nan
    fixed_burden = safe_num(debt_summary.get("housing_education_burden_ratio"), np.nan) if len(debt_summary) else np.nan
    overdue = max_overdue_days

    risk_html = ['<div class="card">']
    risk_html.append(feature_row("순자산", won(net_worth)))
    risk_html.append(feature_row("유동성", f"{liquidity_months_db:.1f}개월" if np.isfinite(liquidity_months_db) else "-"))
    risk_html.append(feature_row("DSR 성격 지표", pct(dsr)))
    risk_html.append(feature_row("주거·교육 부담", pct(fixed_burden)))
    risk_html.append(feature_row("투자 분산도", f"{diversification:.0f} / 100"))
    risk_html.append(feature_row("최대 연체일", f"{int(overdue)}일"))
    if np.isfinite(stress_prob):
        risk_html.append(feature_row("다음 달 금융스트레스", pct(stress_prob)))
    risk_html.append("</div>")
    st.markdown("".join(risk_html), unsafe_allow_html=True)

    if diagnosis_summary and diagnosis_summary.lower() != "nan":
        st.markdown('<div class="section">AI 진단 요약</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="card"><div class="card-desc" style="font-size:.94rem;color:#28313a;">'
            f'{escape(diagnosis_summary)}</div></div>',
            unsafe_allow_html=True,
        )


# =============================================================================
# 18. 하단 안내
# =============================================================================
st.markdown(
    """
<div class="footer">
교육용 MyData MVP입니다. 자산·대출·투자·현금흐름은 fintech_realistic_class DB를 사용하며,
AI 금융건강 점수는 별도 모델 결과 CSV가 있을 때 결합합니다.
외화자산은 환율 데이터가 없어 원화 총자산 합계에서 제외합니다.
</div>
""",
    unsafe_allow_html=True,
)
