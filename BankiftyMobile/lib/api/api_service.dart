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
