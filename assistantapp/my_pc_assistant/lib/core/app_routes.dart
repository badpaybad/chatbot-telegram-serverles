import 'package:flutter/material.dart';
import '../pages/sign_in_page.dart';
import '../pages/sign_up_page.dart';
import '../pages/home_page.dart';

class AppRoutes {
  static const String signIn = '/sign-in';
  static const String signUp = '/sign-up';
  static const String home = '/home';

  static Map<String, WidgetBuilder> get routes => {
    signIn: (context) => const SignInPage(),
    signUp: (context) => const SignUpPage(),
    home: (context) => const HomePage(),
  };

  static String get initialRoute => signIn;
}
