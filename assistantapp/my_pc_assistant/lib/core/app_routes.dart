import 'package:flutter/material.dart';
import '../pages/sign_in_page.dart';
import '../pages/sign_up_page.dart';
import '../pages/home_page.dart';
import '../pages/hardware_page.dart';
import '../pages/vector_search_page.dart';

class AppRoutes {
  static const String signIn = '/sign-in';
  static const String signUp = '/sign-up';
  static const String home = '/home';
  static const String hardware = '/hardware';
  static const String vectorSearch = '/vector-search';

  static Map<String, WidgetBuilder> get routes => {
    signIn: (context) => const SignInPage(),
    signUp: (context) => const SignUpPage(),
    home: (context) => const HomePage(),
    hardware: (context) => const HardwarePage(),
    vectorSearch: (context) => const VectorSearchPage(),
  };

  static String get initialRoute => signIn;
}
