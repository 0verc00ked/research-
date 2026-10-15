# SEBI Retail Algo Trading Framework — captured 2026-05-21

Primary: https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html  (T3)
Extension: https://www.sebi.gov.in/legal/circulars/sep-2025/extension-of-timeline-for-implementation-of-sebi-circular-dated-february-04-2025-on-safer-participation-of-retail-investors-in-algorithmic-trading-_96979.html  (T3)

## Key points
- Broker = principal; algo vendor/fintech = agent. Broker is liable for all API orders.
- "White-box" (execution, transparent logic, replicable by user) vs "black-box" (opaque, vendor-provided) algos.
- Every algo strategy — in-house or vendor — must be registered with the exchange BEFORE going live.
- API access only via unique vendor-client API key + static IP whitelist + 2FA. Logs kept 5 yrs.
- All retail algos must be hosted on Indian servers.
- Brokers ready can go live Oct 1, 2025. Mock session by Jan 3, 2026. Full framework binding on ALL brokers from **Apr 1, 2026**.

## Implication for solo retail algo trader (as of May 2026)
- Self-developed strategy via own broker API key = "white-box, self-use" — broadly permitted but the broker must have completed exchange registration of the product. Threshold for mandatory per-strategy exchange registration applies when orders/sec crosses limits (the circular requires registration above a per-second threshold — confirm with broker; commonly cited as orders/sec > X where X = exchange-set).
- Selling/sharing the algo or making it available to third parties = needs vendor onboarding via the broker.
- Static IP requirement materially affects cloud deployment (need Elastic IP on AWS, etc.).
- Indian-server requirement effectively rules out US/EU cloud regions for the order-routing component.

STALENESS RISK: HIGH. Operational modalities are still being finalised exchange-side as of May 2026. Re-verify before live trading.
