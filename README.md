### Setup
- Create a new virtual environment
```bash
python -m venv .env
source .venv/bin/activate
# Install trustmark library
pip install trustmark

# Optional (LLM deps)
pip install openai lmstudio
```

- Download Trustmark models
https://cc-assets.netlify.app/watermarking/trustmark-models/trustmark_Q.yaml
https://cc-assets.netlify.app/watermarking/trustmark-models/decoder_Q.ckpt
https://cc-assets.netlify.app/watermarking/trustmark-models/encoder_Q.ckpt
https://cc-assets.netlify.app/watermarking/trustmark-models/trustmark_rm_Q.yaml
https://cc-assets.netlify.app/watermarking/trustmark-models/trustmark_rm_Q.ckpt
https://cc-assets.netlify.app/watermarking/trustmark-models/trustmark_bbox_Q.yaml
https://cc-assets.netlify.app/watermarking/trustmark-models/trustmark_bbox_Q.ckpt

- Copy models
```bash
# Assuming python version 3.10 is installed
cp {model-filename} .venv/lib/python3.10/site-packages/trustmark/models/
# Alternatively, assuming model files are downloaded into "models/" directory:
cp -R ./models/* .venv/lib/python3.10/site-packages/trustmark/models/
```

- Run watermarking script
```bash
python watermark.py
```