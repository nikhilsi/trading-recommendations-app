# backend/test_yahoo.py
"""Test Yahoo Finance integration"""
import sys
import time
sys.path.append('/app/app')

from services.yahoo_data_service import YahooDataService

def test_yahoo():
    print("🧪 Testing Yahoo Finance Integration")
    print("=" * 50)
    
    # Create service
    yahoo = YahooDataService()
    
    # Test 1: Get market movers
    print("\n1️⃣ Testing Market Movers (Top Gainers):")
    gainers = yahoo.get_market_movers('gainers')
    if gainers:
        print(f"✅ Found {len(gainers)} gainers")
        for stock in gainers[:3]:  # Show top 3
            print(f"   {stock['symbol']}: ${stock['price']} ({stock['change_percent']:+.1f}%)")
    else:
        print("❌ No gainers found")
    
    # Add delay to avoid rate limits
    print("=" * 50)
    print("Waiting 60 seconds before next test...") 
    time.sleep(60)  # Add 60 second delay between requests
    print("=" * 50)
    
    # Test 2: Get quick quote
    print("\n2️⃣ Testing Quick Quote (AAPL):")
    quote = yahoo.get_quick_quote('AAPL')
    if quote:
        print(f"✅ AAPL: ${quote['price']} ({quote['change_percent']:+.1f}%)")
        print(f"   Volume: {quote['volume']:,}")
    else:
        print("❌ Quote failed")
    
    print("=" * 50)
    print("Waiting 60 seconds before next test...") 
    time.sleep(60)  # Add 2 second delay between requests
    print("=" * 50)
    
    # Test 3: Scan for opportunities
    print("\n3️⃣ Testing Opportunity Scanner:")
    opportunities = yahoo.scan_for_opportunities('momentum')
    if opportunities:
        print(f"✅ Found {len(opportunities)} opportunities")
        for opp in opportunities[:3]:
            print(f"   {opp['symbol']}: Score {opp['score']} - {opp['signals'][0]}")
    else:
        print("❌ No opportunities found")
    
    print("\n✅ Yahoo Finance integration test complete!")

if __name__ == "__main__":
    test_yahoo()