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

Type "/tmp/openapi-demo-venv/bin/python demo/render_hello_openapi_spec.py > /tmp/openapi.yaml"
Enter
Sleep 1800ms

Type "ls -lh /tmp/openapi.yaml"
Enter
Sleep 1200ms

Type "sed -n '/paths:/,/responses:/p' /tmp/openapi.yaml | sed -n '1,18p'"
Enter
Sleep 2500ms
