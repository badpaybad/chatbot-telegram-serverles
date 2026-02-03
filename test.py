

from PIL import Image
from PIL.ExifTags import TAGS

image = Image.open('1.jpg')
exifdata = image.getexif()

for tag_id in exifdata:
    tag = TAGS.get(tag_id, tag_id)
    data = exifdata.get(tag_id)
    print(f"{tag:25}: {data}")