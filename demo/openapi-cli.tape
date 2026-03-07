Output "docs/assets/openapi-cli-demo.gif"

Set Shell "bash"
Set FontSize 22
Set Width 1200
Set Height 900
Set Theme "Builtin Solarized Dark"
Set TypingSpeed 55ms
Set Padding 24

Type "cd /workspace"
Enter
Sleep 900ms
Type "python3 -m venv /tmp/openapi-demo-venv"
Enter
Sleep 1800ms
Type "source /tmp/openapi-demo-venv/bin/activate"
Enter
Sleep 700ms
Type "python -m pip install -q -e ."
Enter
Sleep 2200ms

Type "python demo/preview.py --output /tmp/openapi.yaml"
Enter
Sleep 1800ms

Type "ls -lh /tmp/openapi.yaml"
Enter
Sleep 1200ms

Sleep 2200ms
