brew update
brew install python@3.10

python -m venv .venv
source .venv/bin/activate


pip install --upgrade pip
pip install numpy==1.26.4 onnxruntime-silicon==1.16.3 insightface==0.7.3 opencv-python==4.10.0.84

python cam_age_gender.py
