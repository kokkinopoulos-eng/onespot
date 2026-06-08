with open("pubspec.yaml", encoding="utf-8") as f:
    code = f.read()

if "assets/icon/icon.png" not in code:
    code = code.replace(
        "  assets:",
        "  assets:\n    - assets/icon/icon.png"
    )
    # If no assets section exists
    if "  assets:" not in code:
        code = code.replace(
            "flutter:",
            "flutter:\n  assets:\n    - assets/icon/icon.png"
        )

with open("pubspec.yaml", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
