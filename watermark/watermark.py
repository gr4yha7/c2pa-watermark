# import lmstudio as lms
# from lmstudio import ToolFunctionDef
import base64
import io
import random
import hashlib
from PIL import Image
from trustmark import TrustMark


TM_SCHEMA_CODE=TrustMark.Encoding.BCH_4

def uuidgen(bitlen):
    id = ''.join(random.choice('01') for _ in range(bitlen))
    return id

def string_to_binary(watermark_id: str, bitlen: int) -> str:
    """
    Convert an alphanumeric string to a binary string of the specified length.
    
    Args:
        watermark_id: The alphanumeric string to convert
        bitlen: The required length of the binary string
    
    Returns:
        A binary string (e.g., "01010101") of length bitlen
    """
    # Convert string to bytes using UTF-8 encoding
    string_bytes = watermark_id.encode('utf-8')
    
    # Use hash to get consistent binary representation
    # Hash the string to get a fixed-size output, then convert to binary
    hash_obj = hashlib.sha256(string_bytes)
    hash_bytes = hash_obj.digest()
    
    # Convert hash bytes to binary string
    binary_str = ''.join(format(byte, '08b') for byte in hash_bytes)
    
    # If we need more bits, repeat the hash or extend
    if len(binary_str) < bitlen:
        # Extend by hashing again with a counter
        extended = binary_str
        counter = 0
        while len(extended) < bitlen:
            counter_bytes = counter.to_bytes(4, 'big')
            additional_hash = hashlib.sha256(string_bytes + counter_bytes).digest()
            extended += ''.join(format(byte, '08b') for byte in additional_hash)
            counter += 1
        binary_str = extended
    
    # Truncate to the required length
    return binary_str[:bitlen]


def embed_watermark(base64_image: str, watermarkID, tm):
    decoded_image_bytes = base64.b64decode(base64_image)
    print(f"Decoded image bytes: {len(decoded_image_bytes)}")
    image_stream = io.BytesIO(decoded_image_bytes)
    try:
        cover = Image.open(image_stream)
        print(f"Image information: {cover.format}, {cover.size}, {cover.mode}")
        rgb=cover.convert('RGB')  
        has_alpha=cover.mode== 'RGBA'
        if (has_alpha):
            alpha=cover.split()[-1]
        encoded=tm.encode(rgb, watermarkID, MODE='binary')
        params={
            "exif":cover.info.get('exif'),
            "icc_profile":cover.info.get('icc_profile'),
            "dpi":cover.info.get('dpi')
        }
        not_none_params = {k:v for k, v in params.items() if v is not None}
        output_stream = io.BytesIO()
        # Determine format from original image or default to JPG
        image_format = cover.format or 'JPG'
        encoded.save(output_stream, format=image_format, **not_none_params)
        base64_encoded_image = base64.b64encode(output_stream.getvalue()).decode('utf-8')
        # print(f"Base64 encoded image bytes: {output_stream.getvalue()}")
        print(f"Base64 encoded image: {len(base64_encoded_image)}")
        return base64_encoded_image
    except Exception as e:
        print(f"Error opening image: {e}")
        return None
    finally:
        image_stream.close()

# watermark_image is a tool function that watermarks an image
# image is a base64 encoded string of the image
def watermark_image(base64_image: str, watermark_id: str = None):
    """
    Watermark an image with a user-provided or randomly generated watermark ID.
    
    Args:
        base64_image: Base64 encoded string of the image to watermark
        watermark_id: Optional alphanumeric string to use as watermark ID.
                     If None, a random binary ID will be generated.
    
    Returns:
        Base64 encoded string of the watermarked image, or None if watermarking failed
    """
    tm = TrustMark(verbose=True, model_type='Q', encoding_type=TM_SCHEMA_CODE)
    bitlen = tm.schemaCapacity()
    
    # Use user-provided watermark ID or generate a random one
    if watermark_id:
        print(f"Converting watermark ID '{watermark_id}' to binary format...")
        id = string_to_binary(watermark_id, bitlen)
        print(f"Using user-provided watermark ID (binary length: {len(id)} bits)")
    else:
        id = uuidgen(bitlen)  # Generate a proper binary string
        print(f"Generated random watermark ID (binary length: {len(id)} bits)")
    
    # watermark the image using embed_watermark
    wm_base64_img = embed_watermark(base64_image, id, tm)
    if wm_base64_img is None:
        print(f"Failed to watermark image: embed_watermark returned None")
        return None
    # if verify_watermark(wm_base64_img, watermark_id):
    #   return wm_base64_img
    # else:
    #   print(f"Failed to verify watermark")
    #   return None

def verify_watermark(wm_base64_img_str: str, wm_hash: str):
  if wm_base64_img_str is None:
      print('Error: Cannot verify watermark - image is None')
      return False
  try:
    tm = TrustMark(verbose=True, model_type='Q', encoding_type=TM_SCHEMA_CODE)
    bitlen = tm.schemaCapacity()
    id = string_to_binary(wm_hash, bitlen)
    decoded_image_bytes = base64.b64decode(wm_base64_img_str)
    # print(f"Decoded image bytes: {len(decoded_image_bytes)}")
    image_stream = io.BytesIO(decoded_image_bytes)
    img = Image.open(image_stream)
    stego = img.convert('RGB')
    wm_id, wm_present, wm_schema = tm.decode(stego, 'binary')
    if wm_present:
      print('Watermark detected in image')
      if wm_id==id:
          print('Watermark is correct')
          print(f'Watermark ID: {id}')
      else:
          print('Watermark does not match!')
          print(f'Expected ID: {id}')
          print(f'Found ID: {wm_id}')
    else:
        print('No watermark detected!') 
    return (wm_present and wm_id==id)
  except Exception as e:
    print(f'Error verifying watermark: {e}')
    return False


# def main():
  # api_host = lms.Client.find_default_local_api_host()
  # if api_host is not None:
  #     print(f"An LM Studio API server instance is available at {api_host}")
  # else:
  #     print("No LM Studio API server instance found on any of the default local ports")

  # model = lms.llm("qwen/qwen3-vl-4b")

  # # Functions without type hints can be used without wrapping them
  # # at runtime by defining a tool function directly.
  # tool_def = ToolFunctionDef(
  #   name="watermark_image",
  #   description="Watermarks an image with a random watermark ID.",
  #   parameters={
  #     "base64_image": str,
  #   },
  #   implementation=watermark_image,
  # )
  

#   base64_image_str="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"
  
#   # Example: Use a user-provided watermark ID
#   user_watermark_id = "r4nd0ma55"  # You can change this to any alphanumeric string
#   print(f"Watermarking with user-provided ID: '{user_watermark_id}'")
#   watermarked_image_base64 = watermark_image(base64_image_str, watermark_id=user_watermark_id)
  
#   # Example: Use random watermark ID (if watermark_id is None)
#   # watermarked_image_base64 = watermark_image(base64_image_str)

# if __name__ == "__main__":
#     main()


