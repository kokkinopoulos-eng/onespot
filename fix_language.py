# 1. Add language to SettingsService
with open("lib/core/services/settings_service.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "  static const _keyGemini = 'key_gemini';",
    "  static const _keyGemini = 'key_gemini';\n  static const _keyLanguage = 'response_language';"
)

code = code.replace(
    "  Future<Map<String, String?>> getAllKeys",
    """  Future<void> saveLanguage(String language) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyLanguage, language);
  }

  Future<String> getLanguage() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyLanguage) ?? 'English';
  }

  Future<Map<String, String?>> getAllKeys"""
)

with open("lib/core/services/settings_service.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Settings done")
