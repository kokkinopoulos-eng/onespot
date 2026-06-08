with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Add import
code = code.replace(
    "import '../../core/services/settings_service.dart';",
    "import '../../core/services/settings_service.dart';\nimport '../../core/models/history_entry.dart';"
)

# Add HistoryService instance
code = code.replace(
    "  final SettingsService _settings = SettingsService();",
    "  final SettingsService _settings = SettingsService();\n  final HistoryService _historyService = HistoryService();"
)

# Save to history after result
code = code.replace(
    "      _identifyResult = result;\n        _isIdentifying = false;",
    "      _identifyResult = result;\n        _isIdentifying = false;\n        await _historyService.add(_mode.name, result);"
)

# Add history button in top bar
code = code.replace(
    "_iconBtn('⚙️', () => Navigator.pushNamed(context, '/settings')),",
    "_iconBtn('📋', () => Navigator.pushNamed(context, '/history')),\n              const SizedBox(width: 8),\n              _iconBtn('⚙️', () => Navigator.pushNamed(context, '/settings')),"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
