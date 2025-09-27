### IQ Option API Overview

IQ Option, a prominent online trading platform for binary options, digital options, forex, CFDs, and more, does not offer an official public API for automated trading or direct integration. Like Pocket Option, it relies on WebSocket-based communication, which the community has reverse-engineered into unofficial libraries. These enable programmatic access for tasks like login, balance checks, placing trades, fetching candles, and monitoring positions. **Warning:** Unofficial APIs violate IQ Option's terms of service, risking account bans, security issues, or financial losses. Use only on demo accounts, and seek professional advice for any real trading.

#### Recommended Unofficial Library: `iqoptionapi`
The most active and feature-rich unofficial API is the community-maintained `iqoptionapi` Python library (Python 3.7+), available on GitHub. It supports binary/turbo options, digital options, forex, crypto, and CFDs, with stable WebSocket handling for real-time data.

- **Installation**:  
  Requires `websocket-client==0.56`. Then:  
  ```
  pip install -U git+https://github.com/iqoptionapi/iqoptionapi.git
  ```

- **Key Features**:
  - Email/password authentication (handles 2FA via SMS/app).
  - Balance and profile retrieval.
  - Buying/selling options (binary, digital, turbo) with parameters like asset (e.g., "EURUSD"), amount, direction ("call"/"put"), and duration (e.g., 1 minute).
  - Candle data fetching for technical analysis.
  - Asset open/close status, payouts, and order history.
  - Reconnection logic for stable sessions.
  - Subscriptions for live updates (e.g., top assets, commissions).

- **Basic Usage Example** (adapted from documentation):  
  This authenticates, checks balance, places a demo binary trade, and verifies the outcome.

  ```python
  from iqoptionapi.stable_api import IQ_Option
  import time
  import logging

  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

  # Replace with your credentials
  email = "your_email@example.com"
  password = "your_password"

  Iq = IQ_Option(email, password)
  check, reason = Iq.connect()  # Connect and handle 2FA if prompted

  if check:
      print("Connected! Balance:", Iq.get_balance())  # Switch to "REAL" or "PRACTICE" via change_balance()

      asset = "EURUSD"
      amount = 1  # USD
      action = "call"  # Or "put"
      duration = 1  # Minutes

      print("Placing trade...")
      check, trade_id = Iq.buy(amount, asset, action, duration)
      if check:
          print("Trade placed with ID:", trade_id)
          while Iq.get_async_order(trade_id) is None:
              time.sleep(0.1)
          result = Iq.get_async_order(trade_id)
          print("Trade result:", result)
          print("Updated balance:", Iq.get_balance())
      else:
          print("Trade failed:", reason)

  Iq.close()  # Close WebSocket
  ```

  - **2FA Handling**: If enabled, the library prompts for SMS code during login. For automation, extend with app-based token fetching.
  - **Demo Mode**: Call `Iq.change_balance("PRACTICE")` after login.
  - **Candle Fetching Example**:  
    ```python
    candles = Iq.get_candles(asset, 60, 100, int(time.time()))  # 60s intervals, last 100 candles
    print(candles)
    ```

- **Limitations**:
  - Sessions expire; implement auto-reconnect (e.g., `Iq.set_max_reconnect(-1)`).
  - Platform updates can break compatibility—check GitHub issues for fixes.
  - No built-in risk management; add your own (e.g., stop-loss via sell_option).
  - Heavy calls like `get_all_open_time()` may strain connections.

#### Other Community Resources
- **Alternative Repos**:
  - [Lu-Yi-Hsun/iqoptionapi](https://github.com/Lu-Yi-Hsun/iqoptionapi): Original fork with pro docs; supports advanced features like digital spot buys.
  - [ejtraderLabs/ejtraderIQ](https://github.com/ejtraderLabs/ejtraderIQ): Simplified for digital/turbo trades and live powerbar streaming.
  - [deibsoncarvalho/py-iqoption-api](https://github.com/deibsoncarvalho/py-iqoption-api): Lightweight wrapper for basics.
- **Docs & Tutorials**: Full English docs at [iqoptionapi.github.io](https://iqoptionapi.github.io/iqoptionapi/). Covers multi-language support (e.g., Portuguese, Spanish). Tutorials include bots for EMA strategies or Telegram integrations.
- **Non-Python Options**: Node.js wrappers like [@hemes/iqoption](https://www.npmjs.com/package/@hemes/iqoption) or TypeScript via JSR for web apps.
- **Freelance/Custom**: Developers on platforms like Freelancer offer IQ Option bots, often using these libs for signals or auto-trading.

#### Alternatives
For official APIs in similar trading:
- MetaTrader 4/5 (MT4/MT5) integrations via brokers like XM or IC Markets.
- Platforms like OANDA or Interactive Brokers provide documented REST/WebSocket APIs for forex/CFDs.
- Note: Searches for "IQ Option API" sometimes mix with unrelated tools (e.g., intelligence quotient apps).

