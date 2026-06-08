with open("lib/core/services/vision_api_service.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "  Future<List<Map<String, dynamic>>> findSimilar(",
    "  Future<List<Map<String, dynamic>>> findSimilar("
)

# Add debug after findSimilar return
code = code.replace(
    "    return _extractJsonList(content[0]['text'] as String);",
    "    final result = _extractJsonList(content[0]['text'] as String);\n    debugPrint('SIMILAR_CLAUDE: raw=${content[0]['text']} parsed=$result');\n    return result;"
)

with open("lib/core/services/vision_api_service.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
