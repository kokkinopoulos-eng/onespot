with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "    debugPrint('ONESPOT: pointer up \${e.pointer} moved=\$_moved wasTap-pending');",
    "    debugPrint('ONESPOT: pointer up \${e.pointer} moved=\$_moved wasTap-pending rect=\$_selectionRect');"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
