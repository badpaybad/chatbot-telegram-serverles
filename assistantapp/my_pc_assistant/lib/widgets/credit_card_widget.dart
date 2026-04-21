import 'package:flutter/material.dart';
import '../core/app_colors.dart';

class CreditCardWidget extends StatelessWidget {
  final String name;
  final String cardNumber;
  final String balance;
  final String cardType;

  const CreditCardWidget({
    super.key,
    required this.name,
    required this.cardNumber,
    required this.balance,
    required this.cardType,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 200,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppColors.primary, AppColors.primaryLight, AppColors.secondary],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                name,
                style: const TextStyle(
                  color: AppColors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Icon(Icons.circle, color: AppColors.white, size: 40), // Placeholder for logo
            ],
          ),
          const SizedBox(height: 10),
          Text(
            cardType,
            style: TextStyle(
              color: AppColors.white.withOpacity(0.8),
              fontSize: 16,
            ),
          ),
          const Spacer(),
          Text(
            cardNumber,
            style: const TextStyle(
              color: AppColors.white,
              fontSize: 18,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            balance,
            style: const TextStyle(
              color: AppColors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
