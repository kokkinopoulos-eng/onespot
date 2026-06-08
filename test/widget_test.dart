import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:onespot/main.dart';

void main() {
  testWidgets('OneSpot smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const OneShotApp(termsAccepted: true));
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
