with open("lib/main.dart", encoding="utf-8") as f:
    code = f.read()

# Add import
code = code.replace(
    "import 'features/settings/settings_screen.dart';",
    "import 'features/settings/settings_screen.dart';\nimport 'features/history/history_screen.dart';"
)

# Add route
code = code.replace(
    "'/settings': (_) => const SettingsScreen(),",
    "'/settings': (_) => const SettingsScreen(),\n        '/history': (_) => const HistoryScreen(),"
)

with open("lib/main.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
