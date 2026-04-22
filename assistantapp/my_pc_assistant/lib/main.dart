import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:firebase_core/firebase_core.dart';
import 'core/app_theme.dart';
import 'core/app_routes.dart';
import 'services/auth_service.dart';
import 'services/notification_service.dart';
import 'services/bluetooth_service.dart';
import 'services/database_service.dart';
import 'services/theme_service.dart';
import 'services/biometric_service.dart';
import 'services/nfc_service.dart';
import 'services/connectivity_service.dart';
import 'services/local_storage_service.dart';
import 'services/file_service.dart';
import 'services/vector_db_service.dart';
import 'core/objectbox.dart';

late ObjectBox objectbox;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Khởi tạo Local Storage (SharedPreferences)
  await LocalStorageService.init();

  // Khởi tạo ObjectBox (Vector Database)
  objectbox = await ObjectBox.create();
  
  // Khởi tạo Firebase (Yêu cầu file cấu hình google-services.json / GoogleService-Info.plist)
  try {
    await Firebase.initializeApp();
  } catch (e) {
    debugPrint('Firebase initialization failed: $e');
    debugPrint('Vui lòng thêm file cấu hình Firebase để sử dụng đầy đủ tính năng.');
  }

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => LocalStorageService()),
        ChangeNotifierProxyProvider<LocalStorageService, ThemeService>(
          create: (context) => ThemeService(context.read<LocalStorageService>()),
          update: (context, storage, theme) => theme ?? ThemeService(storage),
        ),
        ChangeNotifierProvider(create: (_) => AuthService()),
        ChangeNotifierProvider(create: (_) => NotificationService()),
        ChangeNotifierProvider(create: (_) => BluetoothService()),
        ChangeNotifierProvider(create: (_) => DatabaseService()),
        ChangeNotifierProvider(create: (_) => BiometricService()),
        ChangeNotifierProvider(create: (_) => NfcService()),
        ChangeNotifierProvider(create: (_) => ConnectivityService()),
        ChangeNotifierProvider(create: (_) => FileService()),
        ChangeNotifierProvider(create: (_) => VectorDbService(objectbox)),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeService = context.watch<ThemeService>();

    return MaterialApp(
      title: 'My PC Assistant',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeService.themeMode,
      initialRoute: AppRoutes.initialRoute,
      routes: AppRoutes.routes,
    );
  }
}
