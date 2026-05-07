from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from tavily import TavilyClient

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# agent.py
from langchain_core.messages import SystemMessage
import json
from datetime import datetime, timedelta
import pandas_ta as ta
import yfinance as yf
from langchain_core.tools import tool
from tavily import TavilyClient





loaded = load_dotenv()

if not loaded:
    load_dotenv("venv/.env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 

API_KEY = os.getenv("THE_KEY")  
tavily_client = TavilyClient(api_key=API_KEY)



class AgentState(TypedDict):
    # The full message history - drives the ReAct loop
    # add_messages is a reducer: appends new messages rather than overwriting
    messages: Annotated[list[BaseMessage], add_messages]
    
    # The ticker being researched
    ticker: str
    
    # Structured research outputs (populated by tools)
    financials: dict
    news_sentiment: dict
    technical_indicators: dict
    analyst_ratings: dict
    
    # Final output
    investment_brief: str



@tool
def get_stock_financials(ticker: str) -> str:
    """
    Fetch key fundamental financial metrics for a stock ticker.
    Returns P/E ratio, forward P/E, revenue growth (YoY), EPS (TTM),
    profit margin, debt-to-equity ratio, and free cash flow yield.
    Use this tool first to understand whether a company's fundamentals
    are strong before diving into price-based analysis.
    Works for both NSE tickers (e.g. RELIANCE.NS) and US tickers (e.g. AAPL).
    """
    try:
        stock = yf.Ticker(ticker)  # [4]
        info = stock.info
        fundamentals = {
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "market_cap_b": round(info.get("marketCap", 0) / 1e9, 2),
            "pe_ratio_ttm": info.get("trailingPE"),
            "pe_ratio_forward": info.get("forwardPE"),
            "eps_ttm": info.get("trailingEps"),
            "revenue_growth_yoy": info.get("revenueGrowth"),
            "earnings_growth_yoy": info.get("earningsGrowth"),
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "return_on_equity": info.get("returnOnEquity"),
            "free_cashflow_b": round(info.get("freeCashflow", 0) / 1e9, 2),
            "dividend_yield": info.get("dividendYield"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "current_price": info.get("currentPrice"),
        }
        # Flag key concerns automatically
        concerns = []
        if fundamentals["debt_to_equity"] and fundamentals["debt_to_equity"] > 200:
            concerns.append("High debt-to-equity ratio - leverage risk")
        if fundamentals["profit_margin"] and fundamentals["profit_margin"] < 0:
            concerns.append("Negative profit margin - company is unprofitable")
        if fundamentals["revenue_growth_yoy"] and fundamentals["revenue_growth_yoy"] < -0.05:
            concerns.append("Revenue declining year-over-year")
        fundamentals["flagged_concerns"] = concerns
        return json.dumps(fundamentals, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})

@tool
def get_news_sentiment(ticker: str) -> str:
    """
    Search for recent news about a stock ticker and analyse overall sentiment.
    Returns the top 5 recent headlines with publication dates and URLs,
    a sentiment classification (BULLISH / BEARISH / NEUTRAL), and
    a brief reasoning for the sentiment call.
    Use this tool to understand current market narrative and any recent
    events (earnings, regulatory issues, product launches, macro exposure)
    that could affect the stock's near-term trajectory.
    """
    try:
        stock = yf.Ticker(ticker)
        company_name = stock.info.get("longName", ticker)
        # Search for recent news via Tavily [6]
        results = tavily_client.search(
            query=f"{company_name} {ticker} stock news analysis 2025 2026",
            max_results=5,
            search_depth="advanced",
        )
        headlines = []
        content_for_sentiment = []
        for r in results.get("results", []):
            headlines.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "published_date": r.get("published_date", ""),
                "snippet": r.get("content", "")[:300],
            })
            content_for_sentiment.append(r.get("content", ""))
        # Simple keyword-based sentiment scoring
        combined_text = " ".join(content_for_sentiment).lower()
        bullish_keywords = [
            "beat", "exceeded", "strong", "growth", "upgrade", "buy",
            "outperform", "record", "surge", "rally", "positive", "robust"
        ]
        bearish_keywords = [
            "miss", "disappointed", "weak", "decline", "downgrade", "sell",
            "underperform", "concern", "risk", "drop", "fell", "negative",
            "lawsuit", "investigation", "layoff"
        ]
        bullish_score = sum(combined_text.count(kw) for kw in bullish_keywords)
        bearish_score = sum(combined_text.count(kw) for kw in bearish_keywords)
        if bullish_score > bearish_score * 1.5:
            sentiment = "BULLISH"
            sentiment_reasoning = f"News skews positive ({bullish_score} bullish signals vs {bearish_score} bearish)"
        elif bearish_score > bullish_score * 1.5:
            sentiment = "BEARISH"
            sentiment_reasoning = f"News skews negative ({bearish_score} bearish signals vs {bullish_score} bullish)"
        else:
            sentiment = "NEUTRAL"
            sentiment_reasoning = f"Mixed signals ({bullish_score} bullish, {bearish_score} bearish)"
        output = {
            "ticker": ticker,
            "company": company_name,
            "headlines": headlines,
            "overall_sentiment": sentiment,
            "sentiment_reasoning": sentiment_reasoning,
            "bullish_signal_count": bullish_score,
            "bearish_signal_count": bearish_score,
        }
        return json.dumps(output, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})

@tool
def get_technical_indicators(ticker: str) -> str:
    """
    Calculate technical analysis indicators for a stock using the last
    200 days of price data. Returns RSI (14-day), MACD and signal line,
    50-day and 200-day SMAs, Golden/Death Cross status, and volume analysis.
    Use this tool to assess whether the stock is in a technically
    favourable or unfavourable position for entry.
    RSI above 70 = overbought. RSI below 30 = oversold.
    Golden cross (SMA50 > SMA200) is bullish; death cross is bearish.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="200d")  # [4]
        if df.empty or len(df) < 50:
            return json.dumps({"error": "Insufficient price history", "ticker": ticker})
        # RSI [5]
        df.ta.rsi(length=14, append=True)
        rsi = round(df["RSI_14"].iloc[-1], 2)
        # MACD [5]
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        macd_val = round(df["MACD_12_26_9"].iloc[-1], 4)
        macd_signal = round(df["MACDs_12_26_9"].iloc[-1], 4)
        macd_histogram = round(df["MACDh_12_26_9"].iloc[-1], 4)
        # SMAs [5]
        df.ta.sma(length=50, append=True)
        df.ta.sma(length=200, append=True)
        sma_50 = round(df["SMA_50"].iloc[-1], 2)
        sma_200 = round(df["SMA_200"].iloc[-1], 2) if len(df) >= 200 else None
        current_price = round(df["Close"].iloc[-1], 2)
        # Golden/Death Cross
        if sma_200:
            cross_status = (
                "GOLDEN CROSS (bullish - SMA50 above SMA200)"
                if sma_50 > sma_200
                else "DEATH CROSS (bearish - SMA50 below SMA200)"
            )
        else:
            cross_status = "N/A (insufficient data for SMA200)"
        # Volume
        avg_volume_30d = int(df["Volume"].tail(30).mean())
        current_volume = int(df["Volume"].iloc[-1])
        volume_ratio = round(current_volume / avg_volume_30d, 2)
        rsi_signal = (
            "OVERBOUGHT - potential reversal ahead" if rsi > 70
            else "OVERSOLD - potential buying opportunity" if rsi < 30
            else f"NEUTRAL ({rsi})"
        )
        macd_signal_str = (
            "BULLISH - MACD above signal line"
            if macd_val > macd_signal
            else "BEARISH - MACD below signal line"
        )
        technicals = {
            "ticker": ticker,
            "current_price": current_price,
            "rsi_14": rsi,
            "rsi_signal": rsi_signal,
            "macd": macd_val,
            "macd_signal_line": macd_signal,
            "macd_histogram": macd_histogram,
            "macd_interpretation": macd_signal_str,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "cross_status": cross_status,
            "price_vs_sma50_pct": round((current_price - sma_50) / sma_50 * 100, 2),
            "volume_30d_avg": avg_volume_30d,
            "volume_today": current_volume,
            "volume_ratio_vs_avg": volume_ratio,
            "volume_note": (
                "Above average" if volume_ratio > 1.2
                else "Below average" if volume_ratio < 0.8
                else "In line with average"
            ),
        }
        return json.dumps(technicals, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})

@tool
def get_analyst_ratings(ticker: str) -> str:
    """
    Fetch current Wall Street / institutional analyst consensus ratings for a stock.
    Returns the distribution of Strong Buy / Buy / Hold / Sell / Strong Sell
    recommendations, the consensus, and the mean price target with implied
    upside or downside from the current price.
    Use this tool to understand what professional analysts collectively
    think about the stock's near-term potential.
    """
    try:
        stock = yf.Ticker(ticker)  # [4]
        info = stock.info
        current_price = info.get("currentPrice", 0)
        target_mean = info.get("targetMeanPrice")
        target_high = info.get("targetHighPrice")
        target_low = info.get("targetLowPrice")
        recommendation = info.get("recommendationKey", "N/A").upper()
        num_analysts = info.get("numberOfAnalystOpinions", 0)
        implied_upside = None
        if target_mean and current_price:
            implied_upside = round((target_mean - current_price) / current_price * 100, 2)
        rec_df = stock.recommendations
        rec_summary = {}
        if rec_df is not None and not rec_df.empty:
            latest = rec_df.tail(1)
            for col in ["strongBuy", "buy", "hold", "sell", "strongSell"]:
                if col in latest.columns:
                    rec_summary[col] = int(latest[col].values[0])
        output = {
            "ticker": ticker,
            "current_price": current_price,
            "consensus_recommendation": recommendation,
            "number_of_analysts": num_analysts,
            "price_target_mean": target_mean,
            "price_target_high": target_high,
            "price_target_low": target_low,
            "implied_upside_pct": implied_upside,
            "ratings_distribution": rec_summary,
        }
        return json.dumps(output, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})

# Register all tools for the agent
TOOLS = [
    get_stock_financials,
    get_news_sentiment,
    get_technical_indicators,
    get_analyst_ratings,
]

# agent.py
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI


SYSTEM_PROMPT = """You are an expert financial research analyst with deep experience
in fundamental analysis, technical analysis, and market sentiment.
Your task is to produce a comprehensive investment brief for a given stock ticker.
RESEARCH APPROACH:
1. Start with fundamentals - understand the business quality first
2. Then check news sentiment - what is the current market narrative?
3. Run technical analysis - is the price action favourable for entry?
4. Finally check analyst consensus - how does Wall Street see it?
You have access to four research tools. Use ALL of them before writing your brief.
Do not skip any tool - each provides a different dimension of analysis.
INVESTMENT BRIEF FORMAT (use this exact structure in your final response):
## Investment Brief: [TICKER] - [COMPANY NAME]
**Date:** [today's date]
**Recommendation:** [STRONG BUY / BUY / HOLD / SELL / STRONG SELL]
**Conviction:** [HIGH / MEDIUM / LOW]
### The Bull Case
[2-3 sentences on why someone would buy this stock]
### The Bear Case
[2-3 sentences on the key risks and why someone would avoid it]
### Fundamental Snapshot
[Key metrics: P/E, growth, margins, debt. 3-4 bullet points]
### Technical Picture
[RSI, MACD, moving averages, volume. 2-3 bullet points]
### News Sentiment
[Current sentiment and what is driving it. 2-3 bullet points]
### Analyst Consensus
[What analysts think. Price target. 1-2 bullet points]
### Final Verdict
[3-4 sentences synthesising everything into a clear recommendation with reasoning]
---
Be direct. Be specific. Use actual numbers from your research.
Avoid generic statements - every claim must be backed by data you retrieved.
"""

def create_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # Use the latest and most capable model
        temperature=0.1,  # Low temperature for consistent analytical output
    )
    # Bind tools - this injects tool schemas into every LLM call
    return llm.bind_tools(TOOLS)


# graph.py
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition



def agent_node(state: AgentState) -> dict:
    """
    Core reasoning node. Calls the LLM with the full message history.
    The LLM either:
    - Returns a tool call → routes to tools node
    - Returns a final text response → routes to END
    """
    llm_with_tools = create_agent()
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def build_graph() -> StateGraph:
    """
    Construct and compile the ReAct agent graph.
    Flow:
    START → agent_node → (tool call?) → tools_node → agent_node → ... → END
    """
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("agent", agent_node)
    graph_builder.add_node("tools", ToolNode(TOOLS))
    graph_builder.add_edge(START, "agent")
    # tools_condition checks if the last message has a tool_call.
    # If yes → "tools". If no → END.
    graph_builder.add_conditional_edges("agent", tools_condition)
    # After tools execute, always return to the agent for the next reasoning step
    graph_builder.add_edge("tools", "agent")
    return graph_builder.compile()


import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

def research_stock(ticker: str, stream: bool = True) -> str:
    """
    Run the financial research agent on a given ticker.
    Args:
        ticker: Stock symbol - e.g. "AAPL", "RELIANCE.NS", "VEDL.NS"
        stream: If True, prints the ReAct loop steps in real-time
    Returns:
        Final investment brief as a string
    """
    graph = build_graph()
    initial_state = {
        "messages": [
            HumanMessage(
                content=f"Please research {ticker.upper()} and produce a comprehensive "
                        f"investment brief using all available research tools."
            )
        ],
        "ticker": ticker.upper(),
        "financials": {},
        "news_sentiment": {},
        "technical_indicators": {},
        "analyst_ratings": {},
        "investment_brief": "",
    }
    final_brief = ""
    if stream:
        print(f"\n{'='*60}")
        print(f"  Financial Research Agent - {ticker.upper()}")
        print(f"{'='*60}\n")
        for event in graph.stream(initial_state, stream_mode="values"):
            messages = event.get("messages", [])
            if messages:
                last_msg = messages[-1]
                msg_type = type(last_msg).__name__
                if msg_type == "AIMessage":
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        for tc in last_msg.tool_calls:
                            print(f"🔧 Calling tool: {tc['name']}")
                            print(f"   Args: {tc['args']}\n")
                    elif last_msg.content:
                        print("📋 INVESTMENT BRIEF\n")
                        print(last_msg.content)
                        final_brief = last_msg.content
                elif msg_type == "ToolMessage":
                    print(f"✅ Tool result received: {last_msg.name}")
                    content_preview = last_msg.content[:200].replace('\n', ' ')
                    print(f"   Preview: {content_preview}...\n")
    else:
        result = graph.invoke(initial_state)
        final_brief = result["messages"][-1].content
    return final_brief

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "RELIANCE.NS"
    research_stock(ticker, stream=True)



