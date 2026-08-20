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
