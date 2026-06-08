code = open("lib/features/camera/camera_screen.dart", encoding="utf-8").read()
# Fix all broken interpolations
code = code.replace("'\\${", "'${")
code = code.replace("\"\\${", "\"${")
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
