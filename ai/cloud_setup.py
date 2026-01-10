# Flaw Engine Cloud Trainer (Colab Template)
# Paste this into a Google Colab notebook

"""
# 1. Install Dependencies
!pip install requests flask
!apt-get install cmake g++

# 2. Clone/Upload your 'flaw' directory
# (Assuming you uploaded it as flaw.zip)
!unzip flaw.zip
%cd flaw

# 3. Build C++ Core (Linux version for Colab)
!mkdir build
%cd build
!cmake ..
!make -j4
%cd ..

# 4. Start Training Worker
# Replace MASTER_URL with your local server's public URL (e.g., from ngrok)
MASTER_URL = "http://your-ngrok-url.ngrok.io"

!python -m ai.selfplay_worker --master {MASTER_URL}
"""

import sys

def generate_colab_sh():
    script = """
#!/bin/bash
# High-speed setup for Colab Workers
pip install requests flask --quiet
git clone https://github.com/your-username/flaw-engine.git flaw
cd flaw
mkdir build && cd build && cmake .. && make -j$(nproc)
cd ..
python -m ai.selfplay_worker --master $1
"""
    with open("setup_colab.sh", "w") as f:
        f.write(script)
    print("Cloud setup script 'setup_colab.sh' generated.")

if __name__ == "__main__":
    generate_colab_sh()
