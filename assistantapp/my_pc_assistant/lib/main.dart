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
import 'services/device_service.dart';
import 'services/media_service.dart';
import 'core/objectbox.dart';

late ObjectBox objectbox;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  debugPrint('App starting initialization...');

  try {
    // Khởi tạo Local Storage (SharedPreferences)
    debugPrint('Initializing SharedPreferences...');
    await LocalStorageService.init();
    debugPrint('SharedPreferences initialized.');

    // Khởi tạo ObjectBox (Vector Database)
    debugPrint('Initializing ObjectBox...');
    objectbox = await ObjectBox.create();
    debugPrint('ObjectBox initialized.');
    
    // Khởi tạo Firebase
    debugPrint('Initializing Firebase...');
    await Firebase.initializeApp().timeout(const Duration(seconds: 5), onTimeout: () {
      debugPrint('Firebase initialization timed out.');
      return Firebase.app(); // Return default app if already exists or just continue
    });
    debugPrint('Firebase initialized.');
  } catch (e) {
    debugPrint('Initialization error: $e');
    // Tiếp tục chạy app ngay cả khi có lỗi khởi tạo (để hiển thị UI thông báo lỗi sau)
  }

  debugPrint('Running app...');
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
        ChangeNotifierProvider(create: (_) => DeviceService()),
        ChangeNotifierProvider(create: (_) => MediaService()),
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
