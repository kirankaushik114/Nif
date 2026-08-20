# Bank Nifty Paper Trading System

A local Bank Nifty paper-trading platform with a Python/FastAPI backend,
SQLite paper-trading database, and Flutter Android mobile dashboard.

> **Current mode: Paper Trading. Real orders are disabled.**

## 1. Overview

The system monitors Bank Nifty market data, calculates RSI values,
manages paper trades, calculates profit/loss, and exposes the data
through a REST API.

The Flutter Android app provides:

-   Bank Nifty price
-   1-minute RSI
-   15-minute RSI
-   Open P&L
-   Closed P&L
-   Total P&L
-   Win rate
-   Open paper trades
-   Manual paper-trade exit
-   API connection status
-   Automatic refresh every 3 seconds

The trading engine remains on the Windows PC. The Android app is a
mobile client for the backend.

## 2. Architecture

``` text
Windows PC
│
├── Bank Nifty Trading Engine
│   ├── Market data
│   ├── RSI calculations
│   ├── Paper-trading logic
│   ├── Trade management
│   └── SQLite database
│
└── FastAPI / Uvicorn
        │
        │ HTTP :8000
        │
        ▼
   Android Phone
   └── Flutter APK
       └── Mobile Dashboard
```

## 3. Project Locations

### Backend

``` text
D:\Nif\Bankifty
```

Important backend files/components include:

``` text
D:\Nif\Bankifty\api\app.py
D:\Nif\Bankifty\data\paper_trading.db
```

### Mobile

``` text
D:\Nif\BankiftyMobile
```

Important Flutter files:

``` text
D:\Nif\BankiftyMobile\lib\main.dart
D:\Nif\BankiftyMobile\lib\api\api_service.dart
D:\Nif\BankiftyMobile\lib\screens\dashboard.dart
D:\Nif\BankiftyMobile\android\app\src\main\AndroidManifest.xml
```

## 4. Trading Mode

The current system is configured as:

``` text
Paper Trading: ON
Real Orders: OFF
```

Example status:

``` json
{
  "status": "running",
  "paper_trading": true,
  "real_orders": false
}
```

## 5. RSI Strategy

The backend currently uses these RSI conditions:

``` text
1M RSI <= 30
    → CE +15

1M RSI >= 70
    → PE +15

15M RSI < 30
    → CE +45

15M RSI > 70
    → PE +45

1M RSI < 20 AND 15M RSI < 25
    → Combined CE +75

1M RSI > 80 AND 15M RSI > 75
    → Combined PE +75
```

These conditions remain part of the backend trading logic.

The mobile application intentionally does **not** display the RSI
condition rules. It displays only the current 1M and 15M RSI values.

## 6. API Endpoints

The mobile application uses:

``` text
GET  /api/market
GET  /api/pnl
GET  /api/open-trades
POST /api/manual-exit
```

Other backend endpoints include:

``` text
GET /api/status
GET /api/conditions
GET /api/trades
```

## 7. Market API

Example:

``` json
{
  "bank_nifty": 57495.9,
  "rsi_1m": 57.62052510513876,
  "rsi_15m": 59.746579506554006,
  "candle_time": "2026-08-20T15:29:00",
  "current_time": "2026-08-20T18:42:08.044405"
}
```

The mobile dashboard displays:

``` text
BANK NIFTY     1M RSI     15M RSI
57495.90       57.62      59.75
```

## 8. P&L API

Example:

``` json
{
  "total_trades": 0,
  "closed_trades": 0,
  "open_trades": 0,
  "winning_trades": 0,
  "losing_trades": 0,
  "breakeven_trades": 0,
  "gross_profit": 0,
  "gross_loss": 0,
  "closed_pnl": 0,
  "open_pnl": 0,
  "total_pnl": 0,
  "win_rate": 0.0,
  "profit_factor": null
}
```

The mobile app displays Open P&L, Closed P&L, Total P&L, Win Rate, and
Open Trades.

## 9. Open Trades API

When there are no open trades:

``` json
{
  "count": 0,
  "trades": []
}
```

This is a valid response, not an error.

## 10. Manual Exit

The mobile app supports manual paper-trade exits.

Endpoint:

``` text
POST /api/manual-exit
```

Example:

``` json
{
  "trade_id": 1,
  "exit_price": 225.50
}
```

The entered price is used as the paper-trade exit price.

## 11. Mobile Auto Refresh

The mobile dashboard refreshes every:

``` text
3 seconds
```

It refreshes market data, P&L, open trades, and connection state.

## 12. Flutter API Configuration

The API service is:

``` text
D:\Nif\BankiftyMobile\lib\api\api_service.dart
```

Current API URL:

``` dart
static const String baseUrl =
    'http://192.168.1.100:8000';
```

Do not use `localhost` from the physical Android phone. The phone must
use the Windows PC's LAN IP.

## 13. Android Network Configuration

The Android manifest contains:

``` xml
<uses-permission android:name="android.permission.INTERNET" />
```

and:

``` xml
android:usesCleartextTraffic="true"
```

These allow the release APK to communicate with the local HTTP API:

``` text
http://192.168.1.100:8000
```

## 14. Start the Backend

Open PowerShell:

``` powershell
cd D:\Nif\Bankifty
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

Expected:

``` text
Uvicorn running on http://0.0.0.0:8000
```

## 15. Test the API

From a browser on the PC or phone:

``` text
http://192.168.1.100:8000/
http://192.168.1.100:8000/api/market
http://192.168.1.100:8000/api/pnl
http://192.168.1.100:8000/api/open-trades
```

## 16. Flutter Environment

Current versions:

``` text
Flutter 3.47.1
Dart 3.13.1
```

Flutter SDK:

``` text
C:\src\flutter
```

## 17. Run the Emulator

``` powershell
cd D:\Nif\BankiftyMobile
flutter devices
flutter emulators
flutter run -d emulator-5554
```

Stop Flutter debug mode with:

``` text
Ctrl + C
```

## 18. Build the Release APK

``` powershell
cd D:\Nif\BankiftyMobile
flutter clean
flutter pub get
flutter build apk --release
```

APK output:

``` text
D:\Nif\BankiftyMobile\build\app\outputs\flutter-apk\app-release.apk
```

The APK can be installed directly on a compatible Android phone. Flutter
and Python do not need to be installed on the phone.

## 19. Current Runtime

``` text
Windows PC
│
├── Bank Nifty trading engine
├── SQLite paper-trading database
└── FastAPI :8000
        │
        │ Wi-Fi / LAN
        ▼
Android phone
└── Bank Nifty Paper Trading APK
```

The PC backend must remain running for the current mobile app to receive
live data.

## 20. Network Requirements

Current PC address:

``` text
192.168.1.100
```

API port:

``` text
8000
```

The phone and PC must be reachable over the same network.

If the PC IP changes, update `baseUrl` in:

``` text
lib/api/api_service.dart
```

and rebuild the APK.

Windows Firewall must allow inbound TCP traffic on port 8000 if
required.

## 21. Mobile Dashboard

Current dashboard:

``` text
BANK NIFTY PAPER TRADING

API CONNECTION STATUS

MARKET
 ├── Bank Nifty
 ├── 1M RSI
 └── 15M RSI

PROFIT & LOSS
 ├── Open P&L
 ├── Closed P&L
 ├── Total P&L
 ├── Win Rate
 └── Open Trades

OPEN PAPER TRADES
 ├── Trade details
 ├── Buy price
 ├── Current price
 ├── Target
 ├── P&L
 └── Manual Exit

Auto-refresh: 3 seconds
```

The RSI Conditions panel is intentionally hidden from the mobile UI.

## 22. Database

Paper-trading database:

``` text
D:\Nif\Bankifty\data\paper_trading.db
```

The database remains on the Windows backend and is not stored inside the
APK.

## 23. Troubleshooting

### Flutter not found

Check:

``` powershell
flutter --version
```

Flutter SDK path:

``` text
C:\src\flutter\bin
```

### Android API connection error

Check:

1.  FastAPI is running.
2.  Phone and PC are on the same network.
3.  `baseUrl` is `http://192.168.1.100:8000`.
4.  Android has the INTERNET permission.
5.  `android:usesCleartextTraffic="true"` is present.
6.  Windows Firewall allows port 8000.
7.  The phone can open `http://192.168.1.100:8000/`.

### No open trades

If the API returns:

``` json
{
  "count": 0,
  "trades": []
}
```

there are simply no open paper trades.

### Rebuild after Android manifest changes

``` powershell
cd D:\Nif\BankiftyMobile
flutter clean
flutter pub get
flutter build apk --release
```

## 24. Current Completion Status

-   [x] Bank Nifty paper-trading backend
-   [x] FastAPI REST API
-   [x] Market API
-   [x] P&L API
-   [x] Open trades API
-   [x] Manual paper-trade exit API
-   [x] SQLite paper-trading database
-   [x] Flutter Android application
-   [x] Android emulator
-   [x] Physical Android APK
-   [x] LAN API communication
-   [x] Android HTTP permissions
-   [x] 3-second auto refresh
-   [x] Mobile P&L
-   [x] Mobile open-trade display
-   [x] Mobile manual exit
-   [x] RSI condition display removed
-   [x] Paper trading confirmed
-   [x] Real orders disabled

## 25. Future Enhancements

Possible future improvements:

### Mobile

-   Push notifications
-   Trade entry alerts
-   Target/stop-loss alerts
-   Trade history
-   Daily/weekly/monthly P&L
-   P&L charts
-   Strategy performance
-   Better connection diagnostics

### Backend

-   WebSocket live updates
-   Background service
-   Automatic startup
-   Risk controls
-   Daily loss limits
-   Maximum trade limits
-   Trading-session controls
-   Market-hours validation

### Deployment

Current:

``` text
Windows PC → FastAPI → Android
```

Future:

``` text
Cloud/VPS
   ├── Trading Engine
   ├── FastAPI
   ├── Database
   └── HTTPS API
          │
          ▼
       Android APK
```

This would allow the phone to connect without being on the same Wi-Fi
network as the Windows PC.

## 26. Security

The current system uses HTTP and a private LAN address, which is
appropriate for local testing.

Before exposing the API to the internet, add:

-   HTTPS
-   Authentication
-   API tokens
-   Access control
-   Rate limiting
-   Secure secret management
-   Firewall rules
-   Audit logging
-   Database backups

Do not expose the current unauthenticated API directly to the public
internet.

## 27. Quick Start

### Terminal 1 --- Backend

``` powershell
cd D:\Nif\Bankifty
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

### Terminal 2 --- Flutter development

``` powershell
cd D:\Nif\BankiftyMobile
flutter run -d emulator-5554
```

### Release APK

``` powershell
cd D:\Nif\BankiftyMobile
flutter clean
flutter pub get
flutter build apk --release
```

APK:

``` text
D:\Nif\BankiftyMobile\build\app\outputs\flutter-apk\app-release.apk
```

## 28. Design Principle

The project is separated into:

``` text
TRADING ENGINE
      ↓
   FASTAPI
      ↓
 MOBILE APP
```

The backend owns trading logic and paper-trade state.

The Flutter application is the mobile monitoring and control interface.

This separation allows the mobile application to evolve independently
while keeping the Bank Nifty trading engine on the backend.

## Disclaimer

This project is currently configured for paper trading. It does not
guarantee trading performance or profitability. Real-money trading
should not be enabled without comprehensive testing, validation, risk
controls, authentication, monitoring, and appropriate safeguards.
