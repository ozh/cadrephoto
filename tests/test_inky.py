import io
from contextlib import redirect_stdout
from inky.auto import auto

try:
    f = io.StringIO()
    with redirect_stdout(f):
        inky_display = auto(ask_user=True, verbose=True)
    out = f.getvalue()
    print(out)

except Exception as e:
    print(f"Could not initialize Inky display: {e}")

print("End")