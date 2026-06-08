# Add language field and save to settings_screen.dart
with open("lib/features/settings/settings_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Add controller
code = code.replace(
    "  final Map<String, TextEditingController> _controllers = {",
    "  final TextEditingController _languageController = TextEditingController();\n  final Map<String, TextEditingController> _controllers = {"
)

# Load language
code = code.replace(
    "    _provider = await _settings.getProvider();",
    "    _provider = await _settings.getProvider();\n    _languageController.text = await _settings.getLanguage();"
)

# Save language
code = code.replace(
    "    await _settings.saveProvider(_provider);",
    "    await _settings.saveProvider(_provider);\n    await _settings.saveLanguage(_languageController.text.trim().isEmpty ? 'English' : _languageController.text.trim());"
)

# Dispose controller
code = code.replace(
    "    _controllers.values.forEach((c) => c.dispose());",
    "    _languageController.dispose();\n    _controllers.values.forEach((c) => c.dispose());"
)

# Add language field in UI before save button
code = code.replace(
    "          const SizedBox(height: 32),\n          ElevatedButton(",
    """          const SizedBox(height: 24),
          _sectionLabel('RESPONSE LANGUAGE'),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF0F0F1A),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFF1E1E32)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('AI will reply in this language', style: TextStyle(color: Colors.white54, fontSize: 11)),
                const SizedBox(height: 8),
                TextField(
                  controller: _languageController,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  decoration: const InputDecoration(
                    hintText: 'e.g. English, Greek, French...',
                    hintStyle: TextStyle(color: Colors.white24, fontSize: 13),
                    border: InputBorder.none,
                    isDense: true,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),
          ElevatedButton("""
)

with open("lib/features/settings/settings_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Settings screen done")
