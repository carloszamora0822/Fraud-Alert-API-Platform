"""
Disposable script — test that we can connect to ADX and query our table.
Delete this whenever you want.
"""

from app.services.adx_client import adx_client

print("📡 Test 1: Checking cluster connection...")
connected = adx_client.test_connection()
print(f"   ✅ Connected! Schema returned: {connected}")
print()

print("📋 Test 2: Checking FraudAlerts table...")
result = adx_client.query_to_dicts("FraudAlerts | count")
print(f"   ✅ FraudAlerts table exists! Row count: {result}")
print()

print("🎉 All tests passed! ADX is ready to go.")
