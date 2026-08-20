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
