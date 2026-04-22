import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_colors.dart';
import '../widgets/credit_card_widget.dart';
import '../widgets/feature_item.dart';
import '../services/auth_service.dart';
import '../services/theme_service.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthService>().currentUser;

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.primary,
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 25,
                    backgroundImage: NetworkImage(user?.profileImageUrl ?? 'https://i.pravatar.cc/150'),
                  ),
                  const SizedBox(width: 15),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Hi, ${user?.name ?? 'Guest'}',
                        style: const TextStyle(
                          color: AppColors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Text(
                        'Welcome back',
                        style: TextStyle(color: Colors.white70, fontSize: 14),
                      ),
                    ],
                  ),
                  const Spacer(),
                  IconButton(
                    icon: Icon(
                      context.watch<ThemeService>().isDarkMode 
                        ? Icons.light_mode 
                        : Icons.dark_mode,
                      color: AppColors.white,
                    ),
                    onPressed: () => context.read<ThemeService>().toggleTheme(),
                  ),
                  Stack(
                    children: [
                      const Icon(Icons.notifications_none, color: AppColors.white, size: 30),
                      Positioned(
                        right: 0,
                        top: 0,
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: const BoxDecoration(
                            color: Colors.red,
                            shape: BoxShape.circle,
                          ),
                          child: const Text(
                            '3',
                            style: TextStyle(color: Colors.white, fontSize: 10),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.background,
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(40),
                    topRight: Radius.circular(40),
                  ),
                ),
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      const CreditCardWidget(
                        name: 'John Smith',
                        cardNumber: '4756 •••• •••• 9018',
                        balance: '\$3,469.52',
                        cardType: 'Amazon Platinum',
                      ),
                      const SizedBox(height: 30),
                      GridView.count(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        crossAxisCount: 3,
                        mainAxisSpacing: 20,
                        crossAxisSpacing: 20,
                        children: const [
                          FeatureItem(title: 'Account and Card', icon: Icons.account_balance_wallet, color: Colors.blue),
                          FeatureItem(title: 'Transfer', icon: Icons.swap_horiz, color: Colors.red),
                          FeatureItem(title: 'Withdraw', icon: Icons.account_balance, color: Colors.blueAccent),
                          FeatureItem(title: 'Mobile prepaid', icon: Icons.phone_android, color: Colors.orange),
                          FeatureItem(title: 'Pay the bill', icon: Icons.receipt_long, color: Colors.teal),
                          FeatureItem(title: 'Save online', icon: Icons.savings, color: Colors.indigo),
                          FeatureItem(title: 'Credit card', icon: Icons.credit_card, color: Colors.orange),
                          FeatureItem(title: 'Transaction report', icon: Icons.assessment, color: Colors.blue),
                          FeatureItem(title: 'Beneficiary', icon: Icons.person_pin, color: Colors.pink),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: AppColors.grey,
        showSelectedLabels: false,
        showUnselectedLabels: false,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.search), label: 'Search'),
          BottomNavigationBarItem(icon: Icon(Icons.mail_outline), label: 'Messages'),
          BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Settings'),
        ],
      ),
    );
  }
}
