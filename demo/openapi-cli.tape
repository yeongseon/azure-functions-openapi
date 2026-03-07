Output "docs/assets/openapi-cli-demo.gif"

Set Shell "bash"
Set FontSize 22
Set Width 1200
Set Height 900
Set Theme "Builtin Solarized Dark"
Set TypingSpeed 55ms
Set Padding 24

Hide
Type "python3 -m venv /tmp/openapi-demo-venv"
Enter
Type "/tmp/openapi-demo-venv/bin/pip install -q --upgrade pip"
Enter
Type "/tmp/openapi-demo-venv/bin/pip install -q -e /vhs"
Enter
Type "clear"
Enter
Show

Type "cd /vhs"
Enter
Sleep 700ms

Type "/tmp/openapi-demo-venv/bin/python -m azure_functions_openapi.cli --help"
Enter
Sleep 2s

Type "/tmp/openapi-demo-venv/bin/python -m azure_functions_openapi.cli generate --format yaml --title DemoAPI --version 1.2.0 --output /tmp/openapi.yaml"
Enter
Sleep 1600ms

Type "sed -n '1,12p' /tmp/openapi.yaml"
Enter
Sleep 2500ms
