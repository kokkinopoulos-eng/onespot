with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Fix identify popup - constrain width and make scrollable
code = code.replace(
    "width: 220,",
    "width: MediaQuery.of(context).size.width - 32,"
)

# Fix counter panel - add maxHeight constraint and scrollable
code = code.replace(
    "constraints: const BoxConstraints(minWidth: 160, maxWidth: 200, maxHeight: 300),",
    "constraints: BoxConstraints(minWidth: 160, maxWidth: MediaQuery.of(context).size.width * 0.55, maxHeight: MediaQuery.of(context).size.height * 0.4),"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
