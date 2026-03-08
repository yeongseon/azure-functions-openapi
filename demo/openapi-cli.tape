Output "docs/assets/openapi-cli-demo.gif"

Set Shell "bash"
Set FontSize 22
Set Width 1200
Set Height 900
Set Theme "Builtin Solarized Dark"
Set TypingSpeed 90ms
Set Padding 24

Type "cd /workspace"
Enter
Sleep 1400ms
Type "python3 -m venv /tmp/openapi-demo-venv"
Enter
Sleep 2600ms
Type "source /tmp/openapi-demo-venv/bin/activate"
Enter
Sleep 1200ms
Type "python -m pip install -q -e ."
Enter
Sleep 3200ms

Type "python demo/run_hello_openapi_example.py --output-dir /tmp/openapi-demo"
Enter
Sleep 2600ms

Type "sed -n '1,20p' /tmp/openapi-demo/openapi.yaml"
Enter
Sleep 1800ms

Type "ls -lh /tmp/openapi-demo/swagger-ui/index.html"
Enter
Sleep 1800ms

Sleep 3400ms
