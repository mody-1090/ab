
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import timedelta

st.set_page_config(page_title="تحليل العلاقة بين الأسهم", layout="centered")

st.title("📊 منصة تحليل العلاقة بين شركتين")

# إدخالات المستخدم
stock_main = st.text_input("رمز السهم المؤثر (مثلاً: AMD)", value="AMD")
stock_secondary = st.text_input("رمز السهم المتأثر (مثلاً: NVDA)", value="NVDA")
analysis_type = st.selectbox("تحليل التفاعل في:", ["نفس اليوم", "اليوم التالي"])

earnings_dates_input = st.text_area(
    "أدخل تواريخ إعلان الأرباح (واحدة في كل سطر، بصيغة YYYY-MM-DD):",
    "2023-10-31\n2023-08-01\n2023-05-02\n2023-01-31"
)

if st.button("🔍 تحليل العلاقة"):
    earnings_dates = earnings_dates_input.strip().split("\n")
    earnings_dates = [pd.to_datetime(date.strip()) for date in earnings_dates if date.strip()]

    # تحميل بيانات الأسعار
    with st.spinner("جاري تحميل البيانات..."):
        main_df = yf.download(stock_main, start=min(earnings_dates) - timedelta(days=2), end=max(earnings_dates) + timedelta(days=2))
        secondary_df = yf.download(stock_secondary, start=min(earnings_dates) - timedelta(days=2), end=max(earnings_dates) + timedelta(days=2))

    results = []
    for date in earnings_dates:
        try:
            day_before = date - timedelta(days=1)
            day_after = date + timedelta(days=1)

            main_change = (main_df.loc[str(date)]['Close'] - main_df.loc[str(day_before)]['Close']) / main_df.loc[str(day_before)]['Close']

            if analysis_type == "نفس اليوم":
                sec_change = (secondary_df.loc[str(date)]['Close'] - secondary_df.loc[str(day_before)]['Close']) / secondary_df.loc[str(day_before)]['Close']
            else:
                sec_change = (secondary_df.loc[str(day_after)]['Close'] - secondary_df.loc[str(date)]['Close']) / secondary_df.loc[str(date)]['Close']

            results.append({
                "📅 التاريخ": date.date(),
                f"🔺 تغير {stock_main}": round(main_change * 100, 2),
                f"📈 تغير {stock_secondary}": round(sec_change * 100, 2),
                "✅ نفس الاتجاه؟": (
                    "نعم" if (main_change > 0 and sec_change > 0) or (main_change < 0 and sec_change < 0) else "لا"
                )
            })
        except Exception as e:
            st.warning(f"تخطي تاريخ {date.date()} بسبب خطأ: {e}")
            continue

    df = pd.DataFrame(results)
    st.subheader("📋 نتائج التحليل:")
    st.dataframe(df)

    same_direction = df["✅ نفس الاتجاه؟"].value_counts().get("نعم", 0)
    total = len(df)
    success_rate = round((same_direction / total) * 100, 2) if total > 0 else 0

    st.markdown(f"### ✅ نسبة النجاح: {success_rate}% ({same_direction} من {total})")
