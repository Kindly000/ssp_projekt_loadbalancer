FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1\
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Narzędzia systemowe potrzebne przy budowaniu części pakietów/zależności 

RUN apt-get update && apt-get install -y --no-install-recommends \
gcc \
libc6-dev \ 
libffi-dev \
iproute2 \
iputils-ping \
&& rm -rf /var/lib/apt/lists/*

# Starszy Ryu to starszy setuptool :_
RUN pip install --upgrade "pip<24.1" "setuptools<60" "wheel<0.41" && \
    pip install "eventlet==0.33.3" "dnspython==2.2.1" "ryu==4.34"

# Zabezpieczenie importu ALREADY_HANDLED w wsgi.py pod nowszym Werkzeug/eventlet
# Bezpieczne dodanie fallbacku ALREADY_HANDLED z zachowaniem oryginalnego wcięcia
RUN python - <<'EOF'
from pathlib import Path
import ryu

wsgi_path = Path(ryu.__file__).parent / "app" / "wsgi.py"
lines = wsgi_path.read_text(encoding="utf-8").splitlines(keepends=True)

target = "from eventlet.wsgi import ALREADY_HANDLED"
out = []
patched = False

for i, line in enumerate(lines):
    if target in line and not patched:
        indent = line[: len(line) - len(line.lstrip(" \t"))]
        prev_has_try = i > 0 and lines[i - 1].lstrip(" \t").startswith("try:")
        if not prev_has_try:
            stripped = line.lstrip(" \t")
            out.append(f"{indent}try:\n")
            out.append(f"{indent}    {stripped}")
            out.append(f"{indent}except ImportError:\n")
            out.append(f"{indent}    ALREADY_HANDLED = object()\n")
            patched = True
            continue
    out.append(line)

wsgi_path.write_text("".join(out), encoding="utf-8")
print("Patched:", patched)
EOF

EXPOSE 6633 6653 8080

ENTRYPOINT ["ryu-manager"]
CMD ["--verbose", "ryu.app.simple_switch_stp_13"]