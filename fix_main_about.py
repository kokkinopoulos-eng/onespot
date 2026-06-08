with open("lib/main.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "import 'features/history/history_screen.dart';",
    "import 'features/history/history_screen.dart';\nimport 'features/about/about_screen.dart';"
)

code = code.replace(
    "'/history': (_) => const HistoryScreen(),",
    "'/history': (_) => const HistoryScreen(),\n        '/about': (_) => const AboutScreen(),"
)

with open("lib/main.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
