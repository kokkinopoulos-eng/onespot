with open("lib/core/services/vision_api_service.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "    debugPrint('SIMILAR_CLAUDE: raw=${content[0]['text']} parsed=$result');",
    "    final rawText = content[0]['text'] as String;\n    debugPrint('SIMILAR_RAW: ${rawText.substring(0, rawText.length.clamp(0, 200))}');\n    debugPrint('SIMILAR_PARSED: $result');"
)

with open("lib/core/services/vision_api_service.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
