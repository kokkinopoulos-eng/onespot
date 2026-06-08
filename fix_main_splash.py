with open("lib/main.dart", encoding="utf-8") as f:
    code = f.read()

# Add import
code = code.replace(
    "import 'features/history/history_screen.dart';",
    "import 'features/history/history_screen.dart';\nimport 'features/splash/splash_screen.dart';"
)

# Change initial route to splash
code = code.replace(
    "initialRoute: '/',",
    "initialRoute: '/splash',"
)

# Add routes
code = code.replace(
    "'/': (_) => const CameraScreen(),",
    "'/splash': (_) => const SplashScreen(),\n        '/camera': (_) => const CameraScreen(),\n        '/': (_) => const CameraScreen(),"
)

with open("lib/main.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
