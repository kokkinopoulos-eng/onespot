with open("lib/core/services/vision_api_service.dart", encoding="utf-8") as f:
    code = f.read()

# Add flutter import if not present
if "package:flutter/foundation.dart" not in code:
    code = code.replace(
        "import 'dart:convert';",
        "import 'dart:convert';\nimport 'package:flutter/foundation.dart';"
    )

with open("lib/core/services/vision_api_service.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
