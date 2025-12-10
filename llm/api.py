import lmstudio as lms
from lmstudio import ToolFunctionDef
from watermark.watermark import watermark_image

tool_def = ToolFunctionDef(
  name="watermark_image",
  description="Given a base64 encoded image string and a unique hash or identifier, returns a watermarked image in base64 string format",
  parameters={
    "base64_image": str,
    "watermark_hash": str,
  },
  implementation=watermark_image,
)

model = lms.llm("qwen/qwen3-vl-4b")
model.act(tool_def)
