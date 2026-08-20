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
