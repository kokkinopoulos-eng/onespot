# Fix onboarding
with open("lib/features/onboarding/onboarding_screen.dart", encoding="utf-8") as f:
    code = f.read()
code = code.replace("const SizedBox(height, 32),", "const SizedBox(height: 32),")
with open("lib/features/onboarding/onboarding_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)

# Fix widget_test
with open("test/widget_test.dart", encoding="utf-8") as f:
    code = f.read()
code = code.replace(
    "await tester.pumpWidget(const OneShotApp());",
    "await tester.pumpWidget(const OneShotApp(termsAccepted: true));"
)
with open("test/widget_test.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
