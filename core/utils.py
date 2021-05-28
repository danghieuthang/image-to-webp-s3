from PIL import Image
import json
dataReponseFalse = json.dumps({
    "error": "True",
    "message": "Upload Failed!"
})

dataResponseTrue = json.dumps({
    "error": "False",
    "url": "https://example.s3.amazonaws.com/example.webp"
})


def convertToWebp(imageSource, imageName="Undefined.webp"):
    """Convert image to webp image

    Args:
        imageSource (ImageSource): The image source
        imageName (str, optional): The image name. Defaults to "Undefined.webp".

    Returns:
        str: The webp image name
    """
    extension = imageName.split(".")[-1]
    imageName = imageName.replace(extension, "webp")
    image = Image.open(imageSource)
    image = image.convert("RGB")
    image.save(imageName, "webp")
    return imageName

