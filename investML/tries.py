result = [{'type': 'text', 'text': '## Investment Brief: MSFT - Microsoft Corporation\n**Date:** 2024-05-15\n**Recommendation:** BUY\n**Conviction:** HIGH\n### The Bull Case\nMicrosoft demonstrates strong fundamentals with a 0.183 YoY revenue growth and a healthy profit margin of 0.3934. The company\'s forward P/E of 21.45 is considered attractive by analysts, who also highlight a significant implied upside of 35.36% from the current price, with a mean price target of $562.07. Continued innovation in AI and cloud services positions Microsoft for future growth.\n### The Bear Case\nDespite strong fundamentals, the technical picture shows some bearish signals, including a Death Cross (SMA50 below SMA200) and MACD below its signal line. Recent news sentiment is neutral, with mixed signals, indicating some uncertainty in the near term. The current volume is also below average, suggesting a lack of strong buying interest.\n### Fundamental Snapshot\n* **P/E Ratio (TTM):** 24.73, **Forward P/E:** 21.45\n* **Revenue Growth (YoY):** 0.183, **Earnings Growth (YoY):** 0.234\n* **Profit Margin:** 0.3934, **Operating Margin:** 0.46326\n* **Debt-to-Equity Ratio:** 30.271 (relatively low)\n### Technical Picture\n* **RSI (14-day):** 53.97 (Neutral)\n* **MACD:** 5.9002, **Signal Line:** 6.9785 (Bearish - MACD below signal line)\n* **Moving Averages:** SMA50 ($398.15) is below SMA200 ($464.37), indicating a Death Cross (bearish).\n* **Volume:** Today\'s volume (7,390,184) is significantly below the 30-day average (33,404,206), suggesting below-average trading activity.\n### News Sentiment\nOverall news sentiment is NEUTRAL, driven by mixed signals (23 bullish, 19 bearish). Some headlines suggest the current valuation offers a rare entry point and that Microsoft is perfectly poised for 2026 after underperforming in 2025. Other articles provide various price forecasts for 2026 and beyond.\n### Analyst Consensus\nOut of 54 analysts, 44 recommend "Buy" and 10 recommend "Strong Buy", with only 3 "Hold" ratings. The consensus recommendation is "STRONG BUY". The mean price target is $562.07, implying an upside of 35.36% from the current price of $415.24.\n### Final Verdict\nDespite some bearish technical signals and neutral near-term news sentiment, Microsoft\'s strong fundamentals, including robust revenue and earnings growth, healthy profit margins, and a manageable debt-to-equity ratio, make it an attractive long-term investment. The overwhelming "STRONG BUY" consensus from Wall Street analysts, coupled with a significant implied upside to the mean price target, reinforces a positive outlook. The current forward P/E also suggests a reasonable valuation. Therefore, a **BUY** recommendation with **HIGH** conviction is warranted for MSFT.', 'extras': {'signature': 'CpsBAQw51sdq9t0PBmLJ8EPcXye20IVISVRqae4ZVN779QTIM1vlGGGBH34HeuMBFcoxaKLlQ7G1XrGbQSxfPdlpN05/p2gYqYxO80vH7QUHAD65qO00AUSSaW+nwMD6lvUhpbJyhNreXKemNsaPImd/R4pThBkDI6AYQiZHF+udtoYOzSmONpqYwB5zFbQXEFhvKC/BQwTYPv/Tbvs='}}]


import re

text = result[0]['text']
import re
import json

# The raw text from result[0]['text']

def extract_stock_data(text):
    # Mapping keys to specific Regex patterns
    patterns = {
        "ticker": r"Brief:\s*(\w+)",
        "recommendation": r"Recommendation:\s*(\w+)",
        "conviction": r"Conviction:\s*(\w+)",
        "pe_ttm": r"P/E Ratio \(TTM\):\s*([\d.]+)",
        "profit_margin": r"Profit Margin:\s*([\d.]+)",
        "revenue_growth": r"Revenue Growth \(YoY\):\s*([\d.]+)",
        "rsi": r"RSI \(14-day\):\s*([\d.]+)",
        "sma50": r"SMA50 \(\$([\d.]+)\)",
        "sma200": r"SMA200 \(\$([\d.]+)\)",
        "price_target": r"mean price target is \$([\d.]+)",
        "upside": r"upside of ([\d.]+)%",
        "consensus": r"recommendation is \"([^\"]+)\""
    }
    
    extracted_info = {}
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        extracted_info[key] = match.group(1) if match else None

    # Logic for Verdict (usually the last sentence/paragraph)
    verdict_match = re.search(r"### Final Verdict\n(.*)", text, re.DOTALL)
    extracted_info["final_verdict"] = verdict_match.group(1).strip() if verdict_match else None
    
    return extracted_info

# Execute and Print
data = extract_stock_data(text)

# Print as a clean JSON object
print(data.keys())
['ticker', 'recommendation', 'conviction', 'pe_ttm', 'profit_margin', 'revenue_growth', 'rsi', 'sma50', 'sma200', 'price_target', 'upside', 'consensus', 'final_verdict']