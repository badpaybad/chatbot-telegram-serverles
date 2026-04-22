import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_pc_assistant/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('End-to-end test', () {
    testWidgets('verify login page and navigate to signup', (tester) async {
      app.main();
      
      // Wait for the app to initialize and render the first frame
      // We use a loop to pump until the text appears or we timeout
      bool found = false;
      for (int i = 0; i < 10; i++) {
        await tester.pump(const Duration(seconds: 1));
        if (find.text('Welcome Back').evaluate().isNotEmpty) {
          found = true;
          break;
        }
      }

      // Verify that the login page is shown
      expect(find.text('Welcome Back'), findsOneWidget);
      expect(find.text('Sign in'), findsWidgets);

      // Tap on the Sign Up button
      final signUpButton = find.text('Sign Up');
      await tester.tap(signUpButton);
      await tester.pumpAndSettle();

      // Verify that the signup page is shown
      expect(find.text('Create Account'), findsOneWidget);
    });
  });
}
