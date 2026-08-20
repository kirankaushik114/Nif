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
