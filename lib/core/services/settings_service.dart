import 'package:shared_preferences/shared_preferences.dart';

class SettingsService {
  static const _keyProvider = 'api_provider';
  static const _keyClaude = 'key_claude';
  static const _keyChatgpt = 'key_chatgpt';
  static const _keyGemini = 'key_gemini';
  static const _keyLanguage = 'response_language';

  Future<void> saveProvider(String provider) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyProvider, provider);
  }

  Future<String> getProvider() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyProvider) ?? 'claude';
  }

  Future<void> saveApiKey(String provider, String key) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('key_$provider', key);
  }

  Future<String?> getApiKey(String provider) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('key_$provider');
  }

  Future<void> saveLanguage(String language) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyLanguage, language);
  }

  Future<String> getLanguage() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyLanguage) ?? 'English';
  }

  Future<Map<String, String?>> getAllKeys() async {
    final prefs = await SharedPreferences.getInstance();
    return {
      'claude': prefs.getString(_keyClaude),
      'chatgpt': prefs.getString(_keyChatgpt),
      'gemini': prefs.getString(_keyGemini),
    };
  }
}
