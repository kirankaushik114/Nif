from pathlib import Path


# ============================================================
# BANK NIFTY MOBILE PROJECT CREATOR
# ============================================================

ROOT = Path(r"D:\Nif\BankiftyMobile")


# ============================================================
# FOLDERS
# ============================================================

folders = [

    ROOT,

    ROOT / "lib",

    ROOT / "lib" / "api",

    ROOT / "lib" / "models",

    ROOT / "lib" / "screens",

    ROOT / "lib" / "widgets",

    ROOT / "lib" / "utils",

    ROOT / "assets",

    ROOT / "test",
]


# ============================================================
# FILE CONTENT
# ============================================================

files = {

    ROOT / "lib" / "main.dart": r'''
import 'package:flutter/material.dart';

import 'screens/dashboard.dart';


void main() {

  runApp(
    const BankNiftyApp(),
  );
}


class BankNiftyApp extends StatelessWidget {

  const BankNiftyApp({
    super.key,
  });


  @override
  Widget build(
    BuildContext context,
  ) {

    return MaterialApp(

      debugShowCheckedModeBanner: false,

      title:
          'Bank Nifty Paper Trading',

      theme:
          ThemeData(
            useMaterial3: true,
            brightness: Brightness.dark,
          ),

      home:
          const DashboardScreen(),
    );
  }
}
''',


    ROOT / "lib" / "api" / "api_service.dart": r'''
import 'dart:convert';

import 'package:http/http.dart' as http;


class ApiService {

  // ----------------------------------------------------------
  // IMPORTANT
  //
  // For Android phone testing on the same Wi-Fi:
  //
  // http://192.168.1.100:8000
  //
  // Do NOT use localhost from the phone.
  // ----------------------------------------------------------

  static const String baseUrl =
      'http://192.168.1.100:8000';


  // ----------------------------------------------------------
  // GET
  // ----------------------------------------------------------

  Future<dynamic> get(
    String endpoint,
  ) async {

    final response = await http.get(
      Uri.parse(
        '$baseUrl$endpoint',
      ),
    );


    if (response.statusCode >= 200 &&
        response.statusCode < 300) {

      return jsonDecode(
        response.body,
      );
    }


    throw Exception(
      'API Error ${response.statusCode}: '
      '${response.body}',
    );
  }


  // ----------------------------------------------------------
  // STATUS
  // ----------------------------------------------------------

  Future<dynamic> getStatus() {

    return get(
      '/api/status',
    );
  }


  // ----------------------------------------------------------
  // MARKET
  // ----------------------------------------------------------

  Future<dynamic> getMarket() {

    return get(
      '/api/market',
    );
  }


  // ----------------------------------------------------------
  // CONDITIONS
  // ----------------------------------------------------------

  Future<dynamic> getConditions() {

    return get(
      '/api/conditions',
    );
  }


  // ----------------------------------------------------------
  // TRADES
  // ----------------------------------------------------------

  Future<dynamic> getTrades() {

    return get(
      '/api/trades',
    );
  }


  // ----------------------------------------------------------
  // OPEN TRADES
  // ----------------------------------------------------------

  Future<dynamic> getOpenTrades() {

    return get(
      '/api/open-trades',
    );
  }


  // ----------------------------------------------------------
  // P&L
  // ----------------------------------------------------------

  Future<dynamic> getPnl() {

    return get(
      '/api/pnl',
    );
  }


  // ----------------------------------------------------------
  // MANUAL EXIT
  // ----------------------------------------------------------

  Future<dynamic> manualExit({

    required int tradeId,

    required double exitPrice,

  }) async {

    final response = await http.post(

      Uri.parse(
        '$baseUrl/api/manual-exit',
      ),

      headers: {

        'Content-Type':
            'application/json',
      },

      body: jsonEncode({

        'trade_id':
            tradeId,

        'exit_price':
            exitPrice,
      }),
    );


    if (response.statusCode >= 200 &&
        response.statusCode < 300) {

      return jsonDecode(
        response.body,
      );
    }


    throw Exception(
      'Manual exit failed: '
      '${response.body}',
    );
  }
}
''',


    ROOT / "lib" / "models" / "market.dart": r'''
class MarketData {

  final double bankNifty;

  final double rsi1m;

  final double rsi15m;

  final String candleTime;

  final String currentTime;


  MarketData({

    required this.bankNifty,

    required this.rsi1m,

    required this.rsi15m,

    required this.candleTime,

    required this.currentTime,
  });


  factory MarketData.fromJson(
    Map<String, dynamic> json,
  ) {

    return MarketData(

      bankNifty:
          (json['bank_nifty'] ?? 0)
              .toDouble(),

      rsi1m:
          (json['rsi_1m'] ?? 0)
              .toDouble(),

      rsi15m:
          (json['rsi_15m'] ?? 0)
              .toDouble(),

      candleTime:
          json['candle_time']
              ?.toString()
              ?? '',

      currentTime:
          json['current_time']
              ?.toString()
              ?? '',
    );
  }
}
''',


    ROOT / "lib" / "models" / "trade.dart": r'''
class PaperTrade {

  final int id;

  final String strategy;

  final String signal;

  final String optionType;

  final double strike;

  final String tradingSymbol;

  final double entryPrice;

  final double targetPrice;

  final double? exitPrice;

  final double? currentPrice;

  final double? pnlPoints;

  final double? pnlValue;

  final String status;

  final String? exitReason;


  PaperTrade({

    required this.id,

    required this.strategy,

    required this.signal,

    required this.optionType,

    required this.strike,

    required this.tradingSymbol,

    required this.entryPrice,

    required this.targetPrice,

    required this.exitPrice,

    required this.currentPrice,

    required this.pnlPoints,

    required this.pnlValue,

    required this.status,

    required this.exitReason,
  });


  factory PaperTrade.fromJson(
    Map<String, dynamic> json,
  ) {

    return PaperTrade(

      id:
          json['id'] ?? 0,

      strategy:
          json['strategy']
              ?.toString()
              ?? '',

      signal:
          json['signal']
              ?.toString()
              ?? '',

      optionType:
          json['option_type']
              ?.toString()
              ?? '',

      strike:
          (json['strike'] ?? 0)
              .toDouble(),

      tradingSymbol:
          json['trading_symbol']
              ?.toString()
              ?? '',

      entryPrice:
          (json['entry_price'] ?? 0)
              .toDouble(),

      targetPrice:
          (json['target_price'] ?? 0)
              .toDouble(),

      exitPrice:
          json['exit_price']
              ?.toDouble(),

      currentPrice:
          json['current_price']
              ?.toDouble(),

      pnlPoints:
          json['current_pnl_points']
              ?.toDouble()
          ??
          json['pnl_points']
              ?.toDouble(),

      pnlValue:
          json['current_pnl_value']
              ?.toDouble()
          ??
          json['pnl_value']
              ?.toDouble(),

      status:
          json['status']
              ?.toString()
              ?? '',

      exitReason:
          json['exit_reason']
              ?.toString(),
    );
  }
}
''',


    ROOT / "lib" / "models" / "pnl.dart": r'''
class PnlData {

  final int totalTrades;

  final int closedTrades;

  final int openTrades;

  final int winningTrades;

  final int losingTrades;

  final int breakevenTrades;

  final double grossProfit;

  final double grossLoss;

  final double closedPnl;

  final double openPnl;

  final double totalPnl;

  final double winRate;

  final double? profitFactor;


  PnlData({

    required this.totalTrades,

    required this.closedTrades,

    required this.openTrades,

    required this.winningTrades,

    required this.losingTrades,

    required this.breakevenTrades,

    required this.grossProfit,

    required this.grossLoss,

    required this.closedPnl,

    required this.openPnl,

    required this.totalPnl,

    required this.winRate,

    required this.profitFactor,
  });


  factory PnlData.fromJson(
    Map<String, dynamic> json,
  ) {

    return PnlData(

      totalTrades:
          json['total_trades'] ?? 0,

      closedTrades:
          json['closed_trades'] ?? 0,

      openTrades:
          json['open_trades'] ?? 0,

      winningTrades:
          json['winning_trades'] ?? 0,

      losingTrades:
          json['losing_trades'] ?? 0,

      breakevenTrades:
          json['breakeven_trades'] ?? 0,

      grossProfit:
          (json['gross_profit'] ?? 0)
              .toDouble(),

      grossLoss:
          (json['gross_loss'] ?? 0)
              .toDouble(),

      closedPnl:
          (json['closed_pnl'] ?? 0)
              .toDouble(),

      openPnl:
          (json['open_pnl'] ?? 0)
              .toDouble(),

      totalPnl:
          (json['total_pnl'] ?? 0)
              .toDouble(),

      winRate:
          (json['win_rate'] ?? 0)
              .toDouble(),

      profitFactor:
          json['profit_factor']
              ?.toDouble(),
    );
  }
}
''',


    ROOT / "lib" / "screens" / "dashboard.dart": r'''
import 'package:flutter/material.dart';

import '../api/api_service.dart';


class DashboardScreen
    extends StatefulWidget {

  const DashboardScreen({
    super.key,
  });


  @override
  State<DashboardScreen> createState() =>
      _DashboardScreenState();
}


class _DashboardScreenState
    extends State<DashboardScreen> {

  final ApiService api =
      ApiService();


  bool loading = true;

  String? error;

  Map<String, dynamic>? market;

  Map<String, dynamic>? conditions;

  Map<String, dynamic>? pnl;

  List<dynamic> openTrades = [];


  @override
  void initState() {

    super.initState();

    loadDashboard();
  }


  Future<void> loadDashboard() async {

    try {

      setState(() {

        loading = true;

        error = null;
      });


      final marketData =
          await api.getMarket();

      final conditionsData =
          await api.getConditions();

      final pnlData =
          await api.getPnl();

      final tradesData =
          await api.getOpenTrades();


      if (!mounted) {
        return;
      }


      setState(() {

        market =
            marketData;

        conditions =
            conditionsData;

        pnl =
            pnlData;

        openTrades =
            tradesData['trades']
                ?? [];

        loading = false;
      });

    } catch (e) {

      if (!mounted) {
        return;
      }

      setState(() {

        error =
            e.toString();

        loading = false;
      });
    }
  }


  @override
  Widget build(
    BuildContext context,
  ) {

    return Scaffold(

      appBar: AppBar(

        title: const Text(
          'Bank Nifty Paper Trading',
        ),

        actions: [

          IconButton(

            onPressed:
                loadDashboard,

            icon:
                const Icon(
                  Icons.refresh,
                ),
          ),
        ],
      ),


      body:

          loading

              ? const Center(
                  child:
                      CircularProgressIndicator(),
                )

              : error != null

                  ? Center(
                      child: Padding(
                        padding:
                            const EdgeInsets.all(
                              20,
                            ),

                        child: Text(
                          error!,
                        ),
                      ),
                    )

                  : RefreshIndicator(

                      onRefresh:
                          loadDashboard,

                      child:
                          ListView(

                            padding:
                                const EdgeInsets.all(
                                  16,
                                ),

                            children: [

                              buildMarket(),

                              const SizedBox(
                                height: 20,
                              ),

                              buildConditions(),

                              const SizedBox(
                                height: 20,
                              ),

                              buildOpenTrades(),

                              const SizedBox(
                                height: 20,
                              ),

                              buildPnl(),
                            ],
                          ),
                    ),
    );
  }


  // ==========================================================
  // MARKET
  // ==========================================================

  Widget buildMarket() {

    return Card(

      child: Padding(

        padding:
            const EdgeInsets.all(
              16,
            ),

        child: Column(

          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [

            const Text(
              'MARKET',
              style:
                  TextStyle(
                    fontSize: 20,
                    fontWeight:
                        FontWeight.bold,
                  ),
            ),

            const SizedBox(
              height: 15,
            ),

            Row(

              mainAxisAlignment:
                  MainAxisAlignment.spaceAround,

              children: [

                metric(
                  'Bank Nifty',
                  '${market?['bank_nifty']?.toStringAsFixed(2) ?? '-'}',
                ),

                metric(
                  '1M RSI',
                  '${market?['rsi_1m']?.toStringAsFixed(2) ?? '-'}',
                ),

                metric(
                  '15M RSI',
                  '${market?['rsi_15m']?.toStringAsFixed(2) ?? '-'}',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }


  // ==========================================================
  // CONDITIONS
  // ==========================================================

  Widget buildConditions() {

    final list =
        conditions?['conditions']
            as List<dynamic>?;

    return Card(

      child: Padding(

        padding:
            const EdgeInsets.all(
              16,
            ),

        child: Column(

          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [

            const Text(
              'RSI CONDITIONS',
              style:
                  TextStyle(
                    fontSize: 20,
                    fontWeight:
                        FontWeight.bold,
                  ),
            ),

            const SizedBox(
              height: 10,
            ),

            if (list != null)

              ...list.map(
                (item) {

                  final met =
                      item['met'] == true;

                  return ListTile(

                    dense: true,

                    leading:

                        Icon(
                          met
                              ? Icons.check_circle
                              : Icons.circle_outlined,

                          color:
                              met
                                  ? Colors.green
                                  : Colors.grey,
                        ),

                    title:
                        Text(
                          item['rule']
                              .toString(),
                        ),

                    subtitle:
                        Text(
                          '${item['strategy']} • '
                          '${item['option']} • '
                          '+${item['target_points']}',
                        ),
                  );
                },
              ),
          ],
        ),
      ),
    );
  }


  // ==========================================================
  // OPEN TRADES
  // ==========================================================

  Widget buildOpenTrades() {

    return Card(

      child: Padding(

        padding:
            const EdgeInsets.all(
              16,
            ),

        child: Column(

          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [

            const Text(
              'OPEN PAPER TRADES',
              style:
                  TextStyle(
                    fontSize: 20,
                    fontWeight:
                        FontWeight.bold,
                  ),
            ),

            const SizedBox(
              height: 10,
            ),

            if (openTrades.isEmpty)

              const Text(
                'No open paper trades.',
              )

            else

              ...openTrades.map(
                (trade) {

                  return ListTile(

                    title:
                        Text(
                          trade['strategy']
                              .toString(),
                        ),

                    subtitle:
                        Text(
                          trade[
                            'trading_symbol'
                          ].toString(),
                        ),

                    trailing:
                        Column(

                          mainAxisAlignment:
                              MainAxisAlignment.center,

                          crossAxisAlignment:
                              CrossAxisAlignment.end,

                          children: [

                            Text(
                              'BUY '
                              '${trade['entry_price']}',
                            ),

                            Text(
                              'CURRENT '
                              '${trade['current_price']}',
                            ),
                          ],
                        ),
                  );
                },
              ),
          ],
        ),
      ),
    );
  }


  // ==========================================================
  // P&L
  // ==========================================================

  Widget buildPnl() {

    return Card(

      child: Padding(

        padding:
            const EdgeInsets.all(
              16,
            ),

        child: Column(

          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [

            const Text(
              'PROFIT & LOSS',
              style:
                  TextStyle(
                    fontSize: 20,
                    fontWeight:
                        FontWeight.bold,
                  ),
            ),

            const SizedBox(
              height: 15,
            ),

            metric(
              'Closed P&L',
              '${pnl?['closed_pnl'] ?? 0}',
            ),

            metric(
              'Open P&L',
              '${pnl?['open_pnl'] ?? 0}',
            ),

            metric(
              'Total P&L',
              '${pnl?['total_pnl'] ?? 0}',
            ),

            metric(
              'Win Rate',
              '${pnl?['win_rate'] ?? 0}%',
            ),
          ],
        ),
      ),
    );
  }


  // ==========================================================
  // METRIC
  // ==========================================================

  Widget metric(
    String title,
    String value,
  ) {

    return Column(

      children: [

        Text(
          title,
          style:
              const TextStyle(
                color:
                    Colors.grey,
              ),
        ),

        const SizedBox(
          height: 4,
        ),

        Text(
          value,
          style:
              const TextStyle(
                fontSize: 20,
                fontWeight:
                    FontWeight.bold,
              ),
        ),
      ],
    );
  }
}
''',


    ROOT / "lib" / "widgets" / "README.txt": r'''
Reusable mobile dashboard widgets will be added here.
''',


    ROOT / "lib" / "utils" / "README.txt": r'''
Mobile application utility functions will be added here.
''',


    ROOT / "test" / "widget_test.dart": r'''
import 'package:flutter_test/flutter_test.dart';

import 'package:bank_nifty_mobile/main.dart';


void main() {

  testWidgets(
    'Bank Nifty app loads',
    (
      WidgetTester tester,
    ) async {

      await tester.pumpWidget(
        const BankNiftyApp(),
      );

      expect(
        find.text(
          'Bank Nifty Paper Trading',
        ),
        findsOneWidget,
      );
    },
  );
}
''',


    ROOT / "README.md": r'''
# Bank Nifty Mobile

Mobile dashboard for the Bank Nifty paper-trading system.

## Backend

FastAPI:

http://192.168.1.100:8000

## API

GET /api/status

GET /api/market

GET /api/conditions

GET /api/trades

GET /api/open-trades

GET /api/pnl

POST /api/manual-exit

## Important

This mobile application is for paper trading only.

No real broker orders are placed.

## Android testing

The phone and Bank Nifty PC should be connected to
the same Wi-Fi network.

The API address is currently:

http://192.168.1.100:8000
''',
}


# ============================================================
# CREATE DIRECTORIES
# ============================================================

print()
print("=" * 70)
print("BANK NIFTY MOBILE PROJECT CREATOR")
print("=" * 70)
print()

for folder in folders:

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"[FOLDER] {folder}"
    )


# ============================================================
# CREATE FILES
# ============================================================

print()

for path, content in files.items():

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content.strip()
        + "\n",
        encoding="utf-8",
    )

    print(
        f"[FILE]   {path}"
    )


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("PROJECT STRUCTURE CREATED")
print("=" * 70)
print()
print(ROOT)
print()

print(
    "IMPORTANT:"
)

print(
    "This script creates the lib/api/models/screens "
    "structure."
)

print(
    "Flutter itself must still be initialized with "
    "`flutter create .`."
)

print()
print(
    "Next steps:"
)

print(
    f"  cd {ROOT}"
)

print(
    "  flutter create ."
)

print(
    "  flutter pub add http"
)

print(
    "  flutter run"
)

print()
print("=" * 70)