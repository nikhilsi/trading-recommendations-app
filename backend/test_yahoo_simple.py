# backend/test_yahoo_simple.py
"""Simple Yahoo Finance test to debug issues"""
import yfinance as yf
import time

def test_single_symbol():
    print("🧪 Testing Yahoo Finance - Simple Version")
    print("=" * 50)
    
    # Test 1: Single symbol
    print("\n1️⃣ Testing ticker on single symbol (AAPL):")
    try:
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        if info:
            print(f"✅ Got data for AAPL")
            print(f"   Price: ${info.get('regularMarketPrice', 'N/A')}")
            print(f"   Volume: {info.get('regularMarketVolume', 'N/A')}")
            print('ALL Data:', info)
        else:
            print("❌ No info returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 50)
    print("Waiting 60 seconds before next test...") 
    time.sleep(60)  # Add 2 second delay between requests
    print("=" * 50)
    
    # Test 2: Download method (more reliable)
    print("\n2️⃣ Testing download method:")
    try:
        data = yf.download("AAPL", period="2d", group_by='ticker', progress=False)
        if not data.empty:
            print(f"✅ Download successful")
            print('ALL Data:', data)
            latest = data.iloc[-1]
            print(f"   Close: ${latest['Close']:.2f}")
            print(f"   Volume: {latest['Volume']:,}")
        else:
            print("❌ No data downloaded")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 50)
    print("Waiting 60 seconds before next test...") 
    time.sleep(60)  # Add 2 second delay between requests
    print("=" * 50)

    # Test 3: Multiple symbols with error handling
    print("\n3️⃣ Testing multiple symbols:")
    symbols = ["AAPL", "MSFT", "GOOGL"]
    try:
        data = yf.download(symbols, period="1d", group_by='ticker', progress=False)
        print(f"✅ Downloaded data for {len(symbols)} symbols")
        print('ALL Data:', data)
        for symbol in symbols:
            if symbol in data:
                latest = data[symbol].iloc[-1]
                print(f"   {symbol}: Close ${latest['Close']:.2f}, Volume {latest['Volume']:,}")
            else:
                print(f"❌ No data for {symbol}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_single_symbol()