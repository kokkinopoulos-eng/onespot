import 'package:flutter/material.dart';
import 'features/camera/camera_screen.dart';
import 'features/settings/settings_screen.dart';
import 'features/history/history_screen.dart';
import 'features/about/about_screen.dart';
import 'features/splash/splash_screen.dart';
import 'features/onboarding/onboarding_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final termsAccepted = prefs.getBool('terms_accepted') ?? false;
  runApp(OneShotApp(termsAccepted: termsAccepted));
}

class OneShotApp extends StatelessWidget {
  final bool termsAccepted;
  const OneShotApp({super.key, required this.termsAccepted});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OneSpot',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF080810),
        colorScheme: const ColorScheme.dark(primary: Color(0xFF00FF88)),
        fontFamily: 'SpaceMono',
      ),
      initialRoute: termsAccepted ? '/splash' : '/onboarding',
      routes: {
        '/onboarding': (_) => const OnboardingScreen(),
        '/splash': (_) => const SplashScreen(),
        '/camera': (_) => const CameraScreen(),
        '/': (_) => const CameraScreen(),
        '/settings': (_) => const SettingsScreen(),
        '/history': (_) => const HistoryScreen(),
        '/about': (_) => const AboutScreen(),
      },
    );
  }
}
