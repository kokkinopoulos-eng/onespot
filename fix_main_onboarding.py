with open("lib/main.dart", encoding="utf-8") as f:
    code = f.read()

# Add import
code = code.replace(
    "import 'features/splash/splash_screen.dart';",
    "import 'features/splash/splash_screen.dart';\nimport 'features/onboarding/onboarding_screen.dart';\nimport 'package:shared_preferences/shared_preferences.dart';"
)

# Change app to StatefulWidget to check terms
old_app = """class OneShotApp extends StatelessWidget {
  const OneShotApp({super.key});

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
      initialRoute: '/splash',
      routes: {
        '/splash': (_) => const SplashScreen(),
        '/camera': (_) => const CameraScreen(),
        '/': (_) => const CameraScreen(),
        '/settings': (_) => const SettingsScreen(),
        '/history': (_) => const HistoryScreen(),
      },
    );
  }
}"""

new_app = """class OneShotApp extends StatelessWidget {
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
      },
    );
  }
}"""

code = code.replace(old_app, new_app)

# Change main to async
code = code.replace(
    "void main() {\n  WidgetsFlutterBinding.ensureInitialized();\n  runApp(const OneShotApp());\n}",
    "void main() async {\n  WidgetsFlutterBinding.ensureInitialized();\n  final prefs = await SharedPreferences.getInstance();\n  final termsAccepted = prefs.getBool('terms_accepted') ?? false;\n  runApp(OneShotApp(termsAccepted: termsAccepted));\n}"
)

with open("lib/main.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
