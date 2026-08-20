import 'dart:async';

import 'package:flutter/material.dart';

import '../api/api_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService api = ApiService();

  Timer? _refreshTimer;

  bool loading = true;
  bool refreshing = false;

  String? error;

  Map<String, dynamic>? market;
  Map<String, dynamic>? pnl;

  List<dynamic> openTrades = [];

  DateTime? lastRefresh;

  // ==========================================================
  // INIT
  // ==========================================================

  @override
  void initState() {
    super.initState();

    loadDashboard();

    _refreshTimer = Timer.periodic(
      const Duration(seconds: 3),
      (_) {
        loadDashboard(silent: true);
      },
    );
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  // ==========================================================
  // LOAD DASHBOARD
  // ==========================================================

  Future<void> loadDashboard({
    bool silent = false,
  }) async {
    if (refreshing) {
      return;
    }

    refreshing = true;

    if (!silent && mounted) {
      setState(() {
        loading = true;
        error = null;
      });
    }

    String? marketError;
    String? pnlError;
    String? tradesError;

    // ----------------------------------------------------------
    // MARKET
    // ----------------------------------------------------------

    try {
      final result = await api.getMarket();

      if (result is Map) {
        market = Map<String, dynamic>.from(result);
      } else {
        marketError =
            'Invalid market response format.';
      }
    } catch (e) {
      marketError = e.toString();
    }

    // ----------------------------------------------------------
    // P&L
    // ----------------------------------------------------------

    try {
      final result = await api.getPnl();

      if (result is Map) {
        pnl = Map<String, dynamic>.from(result);
      } else {
        pnlError =
            'Invalid P&L response format.';
      }
    } catch (e) {
      pnlError = e.toString();
    }

    // ----------------------------------------------------------
    // OPEN TRADES
    // ----------------------------------------------------------

    try {
      final result = await api.getOpenTrades();

      if (result is Map) {
        final data =
            Map<String, dynamic>.from(result);

        final trades = data['trades'];

        if (trades is List) {
          openTrades = trades;
        } else {
          openTrades = [];
          tradesError =
              'Invalid open-trades list.';
        }
      } else {
        tradesError =
            'Invalid open-trades response.';
      }
    } catch (e) {
      tradesError = e.toString();
    }

    if (!mounted) {
      refreshing = false;
      return;
    }

    // ----------------------------------------------------------
    // DETERMINE CONNECTION STATUS
    // ----------------------------------------------------------

    final allFailed =
        market == null &&
        pnl == null &&
        marketError != null &&
        pnlError != null &&
        tradesError != null;

    String? finalError;

    if (allFailed) {
      finalError =
          marketError ??
          pnlError ??
          tradesError;
    }

    setState(() {
      loading = false;

      refreshing = false;

      error = finalError;

      lastRefresh = DateTime.now();
    });
  }

  // ==========================================================
  // BUILD
  // ==========================================================

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Bank Nifty Paper Trading',
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: refreshing
                ? null
                : () {
                    loadDashboard();
                  },
            icon: refreshing
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                    ),
                  )
                : const Icon(
                    Icons.refresh,
                  ),
          ),
        ],
      ),

      body: loading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : RefreshIndicator(
              onRefresh: () => loadDashboard(),

              child: ListView(
                physics:
                    const AlwaysScrollableScrollPhysics(),

                padding:
                    const EdgeInsets.fromLTRB(
                  12,
                  12,
                  12,
                  30,
                ),

                children: [
                  buildConnectionStatus(),

                  const SizedBox(
                    height: 12,
                  ),

                  buildMarketCard(),

                  const SizedBox(
                    height: 12,
                  ),

                  buildPnlCard(),

                  const SizedBox(
                    height: 12,
                  ),

                  buildOpenTradesCard(),

                  const SizedBox(
                    height: 12,
                  ),

                  buildRefreshInfo(),
                ],
              ),
            ),
    );
  }

  // ==========================================================
  // CONNECTION STATUS
  // ==========================================================

  Widget buildConnectionStatus() {
    final connected =
        error == null;

    return Container(
      padding:
          const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 9,
      ),

      decoration: BoxDecoration(
        borderRadius:
            BorderRadius.circular(10),

        color: connected
            ? Colors.green
                .withOpacity(0.12)
            : Colors.red
                .withOpacity(0.12),

        border: Border.all(
          color: connected
              ? Colors.green
              : Colors.red,
        ),
      ),

      child: Column(
        children: [
          Row(
            children: [
              Icon(
                connected
                    ? Icons.cloud_done
                    : Icons.cloud_off,

                size: 19,

                color: connected
                    ? Colors.green
                    : Colors.red,
              ),

              const SizedBox(
                width: 8,
              ),

              Expanded(
                child: Text(
                  connected
                      ? 'API CONNECTED • PAPER TRADING'
                      : 'API CONNECTION ERROR',

                  style: TextStyle(
                    fontWeight:
                        FontWeight.bold,

                    color: connected
                        ? Colors.green
                        : Colors.red,
                  ),
                ),
              ),
            ],
          ),

          if (!connected) ...[
            const SizedBox(
              height: 8,
            ),

            Text(
              error ?? '',
              style:
                  const TextStyle(
                fontSize: 11,
                color: Colors.red,
              ),
            ),
          ],
        ],
      ),
    );
  }

  // ==========================================================
  // MARKET
  // ==========================================================

  Widget buildMarketCard() {
    final bankNifty =
        number(
      market?['bank_nifty'],
    );

    final rsi1m =
        number(
      market?['rsi_1m'],
    );

    final rsi15m =
        number(
      market?['rsi_15m'],
    );

    return Card(
      child: Padding(
        padding:
            const EdgeInsets.all(16),

        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [
            Row(
              children: [
                const Icon(
                  Icons.show_chart,
                  size: 22,
                ),

                const SizedBox(
                  width: 8,
                ),

                const Text(
                  'MARKET',
                  style:
                      TextStyle(
                    fontSize: 19,
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),

                const Spacer(),

                Container(
                  padding:
                      const EdgeInsets
                          .symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),

                  decoration:
                      BoxDecoration(
                    borderRadius:
                        BorderRadius.circular(8),

                    color: Colors.green
                        .withOpacity(0.12),
                  ),

                  child:
                      const Text(
                    'LIVE',

                    style:
                        TextStyle(
                      fontSize: 11,
                      fontWeight:
                          FontWeight.bold,
                      color:
                          Colors.green,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(
              height: 18,
            ),

            Row(
              children: [
                Expanded(
                  child:
                      marketMetric(
                    'BANK NIFTY',
                    formatNumber(
                      bankNifty,
                    ),
                  ),
                ),

                Expanded(
                  child:
                      marketMetric(
                    '1M RSI',
                    formatNumber(
                      rsi1m,
                    ),
                    valueColor:
                        rsiColor(
                      rsi1m,
                    ),
                  ),
                ),

                Expanded(
                  child:
                      marketMetric(
                    '15M RSI',
                    formatNumber(
                      rsi15m,
                    ),
                    valueColor:
                        rsiColor(
                      rsi15m,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(
              height: 15,
            ),

            if (market?['candle_time'] != null)
              Text(
                'Candle: ${market!['candle_time']}',

                style:
                    const TextStyle(
                  fontSize: 11,
                  color:
                      Colors.grey,
                ),
              ),
          ],
        ),
      ),
    );
  }

  // ==========================================================
  // MARKET METRIC
  // ==========================================================

  Widget marketMetric(
    String title,
    String value, {
    Color? valueColor,
  }) {
    return Column(
      children: [
        Text(
          title,
          style:
              const TextStyle(
            fontSize: 10,
            color:
                Colors.grey,
            fontWeight:
                FontWeight.bold,
          ),
        ),

        const SizedBox(
          height: 5,
        ),

        FittedBox(
          child: Text(
            value,
            style:
                TextStyle(
              fontSize: 20,
              fontWeight:
                  FontWeight.bold,
              color:
                  valueColor,
            ),
          ),
        ),
      ],
    );
  }

  // ==========================================================
  // P&L
  // ==========================================================

  Widget buildPnlCard() {
    final openPnl =
        number(
      pnl?['open_pnl'],
    );

    final closedPnl =
        number(
      pnl?['closed_pnl'],
    );

    final totalPnl =
        number(
      pnl?['total_pnl'],
    );

    final winRate =
        number(
      pnl?['win_rate'],
    );

    return Card(
      child: Padding(
        padding:
            const EdgeInsets.all(16),

        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [
            sectionTitle(
              Icons
                  .account_balance_wallet,
              'PROFIT & LOSS',
            ),

            const SizedBox(
              height: 15,
            ),

            Row(
              children: [
                Expanded(
                  child:
                      pnlMetric(
                    'OPEN P&L',
                    openPnl,
                  ),
                ),

                Expanded(
                  child:
                      pnlMetric(
                    'CLOSED P&L',
                    closedPnl,
                  ),
                ),

                Expanded(
                  child:
                      pnlMetric(
                    'TOTAL P&L',
                    totalPnl,
                    large: true,
                  ),
                ),
              ],
            ),

            const SizedBox(
              height: 15,
            ),

            const Divider(),

            const SizedBox(
              height: 8,
            ),

            Row(
              mainAxisAlignment:
                  MainAxisAlignment
                      .spaceBetween,

              children: [
                const Text(
                  'Win Rate',

                  style:
                      TextStyle(
                    color:
                        Colors.grey,
                  ),
                ),

                Text(
                  '${formatNumber(winRate)}%',

                  style:
                      const TextStyle(
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),
              ],
            ),

            const SizedBox(
              height: 8,
            ),

            Row(
              mainAxisAlignment:
                  MainAxisAlignment
                      .spaceBetween,

              children: [
                const Text(
                  'Open Trades',

                  style:
                      TextStyle(
                    color:
                        Colors.grey,
                  ),
                ),

                Text(
                  '${openTrades.length}',

                  style:
                      const TextStyle(
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ==========================================================
  // P&L METRIC
  // ==========================================================

  Widget pnlMetric(
    String title,
    double value, {
    bool large = false,
  }) {
    final color =
        pnlColor(value);

    return Column(
      children: [
        Text(
          title,

          style:
              const TextStyle(
            fontSize: 10,
            color:
                Colors.grey,
            fontWeight:
                FontWeight.bold,
          ),
        ),

        const SizedBox(
          height: 5,
        ),

        FittedBox(
          child: Text(
            '${value >= 0 ? '+' : ''}'
            '${value.toStringAsFixed(2)}',

            style:
                TextStyle(
              fontSize:
                  large ? 19 : 15,
              fontWeight:
                  FontWeight.bold,
              color:
                  color,
            ),
          ),
        ),
      ],
    );
  }

  // ==========================================================
  // OPEN TRADES
  // ==========================================================

  Widget buildOpenTradesCard() {
    return Card(
      child: Padding(
        padding:
            const EdgeInsets.all(16),

        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [
            sectionTitle(
              Icons.shopping_cart,
              'OPEN PAPER TRADES',
            ),

            const SizedBox(
              height: 10,
            ),

            if (openTrades.isEmpty)

              Container(
                padding:
                    const EdgeInsets.all(15),

                child:
                    const Center(
                  child:
                      Text(
                    'No open paper trades.',
                    style:
                        TextStyle(
                      color:
                          Colors.grey,
                    ),
                  ),
                ),
              )

            else

              ...openTrades.map(
                (item) {
                  final trade =
                      item
                          as Map<String,
                              dynamic>;

                  return buildTradeCard(
                    trade,
                  );
                },
              ),
          ],
        ),
      ),
    );
  }

  // ==========================================================
  // TRADE CARD
  // ==========================================================

  Widget buildTradeCard(
    Map<String, dynamic> trade,
  ) {
    final id =
        intValue(
      trade['id'],
    );

    final strategy =
        trade['strategy']
            ?.toString() ??
            '';

    final optionType =
        trade['option_type']
            ?.toString() ??
            '';

    final symbol =
        trade['trading_symbol']
            ?.toString() ??
            '';

    final strike =
        number(
      trade['strike'],
    );

    final entry =
        number(
      trade['entry_price'],
    );

    final target =
        number(
      trade['target_price'],
    );

    final current =
        number(
      trade['current_price'],
    );

    final pnlPoints =
        trade['pnl_points'] != null
            ? number(
                trade['pnl_points'],
              )
            : current - entry;

    final pnlPercent =
        entry == 0
            ? 0
            : pnlPoints /
                entry *
                100;

    final positive =
        pnlPoints >= 0;

    return Container(
      margin:
          const EdgeInsets.only(
        bottom: 12,
      ),

      padding:
          const EdgeInsets.all(13),

      decoration:
          BoxDecoration(
        borderRadius:
            BorderRadius.circular(12),

        border:
            Border.all(
          color:
              positive
                  ? Colors.green
                      .withOpacity(
                          0.45)
                  : Colors.red
                      .withOpacity(
                          0.35),
        ),

        color: Theme.of(context)
            .colorScheme
            .surfaceContainerHighest
            .withOpacity(0.30),
      ),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,

                  children: [
                    Text(
                      strategy,

                      style:
                          const TextStyle(
                        fontSize: 17,
                        fontWeight:
                            FontWeight.bold,
                      ),
                    ),

                    const SizedBox(
                      height: 3,
                    ),

                    Text(
                      '$optionType '
                      '${strike.toStringAsFixed(0)}',

                      style:
                          const TextStyle(
                        fontSize: 12,
                        color:
                            Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),

              Container(
                padding:
                    const EdgeInsets
                        .symmetric(
                  horizontal: 9,
                  vertical: 5,
                ),

                decoration:
                    BoxDecoration(
                  borderRadius:
                      BorderRadius.circular(
                          7),

                  color:
                      optionType == 'CE'
                          ? Colors.blue
                              .withOpacity(
                                  0.15)
                          : Colors.orange
                              .withOpacity(
                                  0.15),
                ),

                child:
                    Text(
                  optionType,

                  style:
                      TextStyle(
                    fontWeight:
                        FontWeight.bold,

                    color:
                        optionType == 'CE'
                            ? Colors.blue
                            : Colors.orange,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(
            height: 8,
          ),

          Text(
            symbol,

            style:
                const TextStyle(
              fontSize: 11,
              color:
                  Colors.grey,
            ),
          ),

          const SizedBox(
            height: 13,
          ),

          Row(
            children: [
              Expanded(
                child:
                    tradeMetric(
                  'BUY',
                  entry,
                ),
              ),

              Expanded(
                child:
                    tradeMetric(
                  'CURRENT',
                  current,
                ),
              ),

              Expanded(
                child:
                    tradeMetric(
                  'TARGET',
                  target,
                ),
              ),
            ],
          ),

          const SizedBox(
            height: 12,
          ),

          Container(
            padding:
                const EdgeInsets
                    .symmetric(
              horizontal: 12,
              vertical: 10,
            ),

            decoration:
                BoxDecoration(
              borderRadius:
                  BorderRadius.circular(
                      9),

              color:
                  positive
                      ? Colors.green
                          .withOpacity(
                              0.10)
                      : Colors.red
                          .withOpacity(
                              0.10),
            ),

            child:
                Row(
              children: [
                const Text(
                  'P&L',

                  style:
                      TextStyle(
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),

                const Spacer(),

                Text(
                  '${positive ? '+' : ''}'
                  '${pnlPoints.toStringAsFixed(2)} pts',

                  style:
                      TextStyle(
                    fontWeight:
                        FontWeight.bold,

                    color:
                        positive
                            ? Colors.green
                            : Colors.red,
                  ),
                ),

                const SizedBox(
                  width: 8,
                ),

                Text(
                  '(${positive ? '+' : ''}'
                  '${pnlPercent.toStringAsFixed(2)}%)',

                  style:
                      TextStyle(
                    fontSize: 11,

                    color:
                        positive
                            ? Colors.green
                            : Colors.red,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(
            height: 12,
          ),

          SizedBox(
            width:
                double.infinity,

            child:
                OutlinedButton.icon(
              onPressed: () {
                showManualExitDialog(
                  tradeId: id,
                  strategy:
                      strategy,
                  currentPrice:
                      current,
                );
              },

              icon:
                  const Icon(
                Icons.exit_to_app,
              ),

              label:
                  const Text(
                'MANUAL EXIT',
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ==========================================================
  // TRADE METRIC
  // ==========================================================

  Widget tradeMetric(
    String title,
    double value,
  ) {
    return Column(
      children: [
        Text(
          title,

          style:
              const TextStyle(
            fontSize: 10,
            color:
                Colors.grey,
            fontWeight:
                FontWeight.bold,
          ),
        ),

        const SizedBox(
          height: 4,
        ),

        Text(
          value.toStringAsFixed(2),

          style:
              const TextStyle(
            fontSize: 16,
            fontWeight:
                FontWeight.bold,
          ),
        ),
      ],
    );
  }

  // ==========================================================
  // MANUAL EXIT
  // ==========================================================

  Future<void> showManualExitDialog({
    required int tradeId,
    required String strategy,
    required double currentPrice,
  }) async {
    final controller =
        TextEditingController(
      text:
          currentPrice
              .toStringAsFixed(2),
    );

    bool submitting = false;

    String? validationError;

    await showDialog(
      context: context,
      barrierDismissible: false,

      builder:
          (dialogContext) {
        return StatefulBuilder(
          builder:
              (
            context,
            setDialogState,
          ) {
            return AlertDialog(
              title:
                  const Text(
                'Manual Exit',
              ),

              content:
                  Column(
                mainAxisSize:
                    MainAxisSize.min,

                crossAxisAlignment:
                    CrossAxisAlignment
                        .start,

                children: [
                  Text(
                    strategy,

                    style:
                        const TextStyle(
                      fontWeight:
                          FontWeight.bold,
                    ),
                  ),

                  const SizedBox(
                    height: 6,
                  ),

                  const Text(
                    'Enter any exit price.',

                    style:
                        TextStyle(
                      color:
                          Colors.grey,
                      fontSize: 12,
                    ),
                  ),

                  const SizedBox(
                    height: 15,
                  ),

                  TextField(
                    controller:
                        controller,

                    keyboardType:
                        const TextInputType
                            .numberWithOptions(
                      decimal: true,
                    ),

                    autofocus: true,

                    decoration:
                        InputDecoration(
                      labelText:
                          'Exit Price',

                      prefixText:
                          '₹ ',

                      border:
                          const OutlineInputBorder(),

                      errorText:
                          validationError,
                    ),
                  ),
                ],
              ),

              actions: [
                TextButton(
                  onPressed:
                      submitting
                          ? null
                          : () {
                              Navigator.of(
                                dialogContext,
                              ).pop();
                            },

                  child:
                      const Text(
                    'CANCEL',
                  ),
                ),

                FilledButton.icon(
                  onPressed:
                      submitting
                          ? null
                          : () async {
                              final price =
                                  double.tryParse(
                                controller
                                    .text
                                    .trim(),
                              );

                              if (price ==
                                      null ||
                                  price <= 0) {
                                setDialogState(
                                  () {
                                    validationError =
                                        'Enter a valid price.';
                                  },
                                );

                                return;
                              }

                              setDialogState(
                                () {
                                  submitting =
                                      true;
                                  validationError =
                                      null;
                                },
                              );

                              try {
                                await api.manualExit(
                                  tradeId:
                                      tradeId,

                                  exitPrice:
                                      price,
                                );

                                if (!mounted) {
                                  return;
                                }

                                Navigator.of(
                                  dialogContext,
                                ).pop();

                                ScaffoldMessenger
                                    .of(
                                        context)
                                    .showSnackBar(
                                  SnackBar(
                                    content:
                                        Text(
                                      '$strategy exited at '
                                      '₹${price.toStringAsFixed(2)}',
                                    ),
                                  ),
                                );

                                await loadDashboard();
                              } catch (e) {
                                setDialogState(
                                  () {
                                    submitting =
                                        false;

                                    validationError =
                                        'Exit failed: $e';
                                  },
                                );
                              }
                            },

                  icon:
                      submitting
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child:
                                  CircularProgressIndicator(
                                strokeWidth:
                                    2,
                              ),
                            )
                          : const Icon(
                              Icons.check,
                            ),

                  label:
                      Text(
                    submitting
                        ? 'EXITING...'
                        : 'EXIT TRADE',
                  ),
                ),
              ],
            );
          },
        );
      },
    );

    controller.dispose();
  }

  // ==========================================================
  // REFRESH INFO
  // ==========================================================

  Widget buildRefreshInfo() {
    final time =
        lastRefresh;

    return Center(
      child: Text(
        time == null
            ? 'Auto-refresh: every 3 seconds'
            : 'Updated '
              '${time.hour.toString().padLeft(2, '0')}:'
              '${time.minute.toString().padLeft(2, '0')}:'
              '${time.second.toString().padLeft(2, '0')}'
              ' • Auto-refresh: 3 sec',

        style:
            const TextStyle(
          fontSize: 10,
          color:
              Colors.grey,
        ),
      ),
    );
  }

  // ==========================================================
  // SECTION TITLE
  // ==========================================================

  Widget sectionTitle(
    IconData icon,
    String title,
  ) {
    return Row(
      children: [
        Icon(
          icon,
          size: 21,
        ),

        const SizedBox(
          width: 8,
        ),

        Text(
          title,

          style:
              const TextStyle(
            fontSize: 19,
            fontWeight:
                FontWeight.bold,
          ),
        ),
      ],
    );
  }

  // ==========================================================
  // NUMBER
  // ==========================================================

  double number(
    dynamic value,
  ) {
    if (value == null) {
      return 0;
    }

    if (value is num) {
      return value.toDouble();
    }

    return double.tryParse(
          value.toString(),
        ) ??
        0;
  }

  // ==========================================================
  // INT
  // ==========================================================

  int intValue(
    dynamic value,
  ) {
    if (value is int) {
      return value;
    }

    if (value is num) {
      return value.toInt();
    }

    return int.tryParse(
          value.toString(),
        ) ??
        0;
  }

  // ==========================================================
  // FORMAT
  // ==========================================================

  String formatNumber(
    double value,
  ) {
    return value.toStringAsFixed(2);
  }

  // ==========================================================
  // RSI COLOR
  // ==========================================================

  Color? rsiColor(
    double value,
  ) {
    if (value <= 30) {
      return Colors.green;
    }

    if (value >= 70) {
      return Colors.red;
    }

    return null;
  }

  // ==========================================================
  // P&L COLOR
  // ==========================================================

  Color pnlColor(
    double value,
  ) {
    if (value > 0) {
      return Colors.green;
    }

    if (value < 0) {
      return Colors.red;
    }

    return Colors.grey;
  }
}