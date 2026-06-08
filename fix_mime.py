with open("lib/core/services/vision_api_service.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "'media_type': 'image/png'",
    "'media_type': 'image/jpeg'"
)

with open("lib/core/services/vision_api_service.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
