import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_pc_assistant/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Login Flow Test', () {
    testWidgets('login with mock account and navigate to home', (tester) async {
      app.main();
      
      // Chờ app khởi tạo và màn hình Sign In xuất hiện
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Kiểm tra xem có đang ở trang Sign In không
      expect(find.text('Welcome Back'), findsOneWidget);

      // Tìm các trường nhập liệu
      final textFields = find.byType(TextFormField);
      expect(textFields, findsNWidgets(2));

      // Nhập Email (Trường đầu tiên)
      await tester.enterText(textFields.at(0), 'test@gmail.com');
      await tester.pump();

      // Nhập Password (Trường thứ hai)
      await tester.enterText(textFields.at(1), '12345678');
      await tester.pump();

      // Nhấn nút Sign in
      final signInButton = find.widgetWithText(ElevatedButton, 'Sign in');
      await tester.tap(signInButton);
      
      // Chờ chuyển cảnh và kết quả API
      for (int i = 0; i < 10; i++) {
        await tester.pump(const Duration(milliseconds: 500));
        if (find.text('Hi, John Smith').evaluate().isNotEmpty) break;
      }

      // Kiểm tra xem có chuyển sang trang Home không
      expect(find.text('Hi, John Smith'), findsOneWidget);
    });
  });
}
