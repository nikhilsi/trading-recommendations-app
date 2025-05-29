# backend/test_polygon.py
import sys
import os
sys.path.append('/app/app')

from services.polygon_service import PolygonService

def test_polygon():
    print("🧪 Testing Polygon.io Integration")
    print("=" * 50)
    
    api_key = os.getenv('POLYGON_API_KEY')
    if not api_key:
        print("❌ No API key found!")
        return
        
    polygon = PolygonService(api_key)
    
    # Test market snapshot
    print("\n📊 Getting market snapshot...")
    snapshot = polygon.get_market_snapshot()
    
    print(f"\n📈 Top Gainers:")
    for stock in snapshot['gainers'][:5]:
        print(f"   {stock['symbol']}: ${stock['price']:.2f} ({stock['change_percent']:+.1f}%)")
    
    print(f"\n📉 Top Losers:")
    for stock in snapshot['losers'][:5]:
        print(f"   {stock['symbol']}: ${stock['price']:.2f} ({stock['change_percent']:.1f}%)")
    
    print("\n✅ Polygon.io integration successful!")

if __name__ == "__main__":
    test_polygon()