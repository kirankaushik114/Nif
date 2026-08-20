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
