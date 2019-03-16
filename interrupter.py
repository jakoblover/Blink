import PIL.Image

def valid_media(path):
    img = PIL.Image.open(path)
    aspect_ratio = img.size[0] / img.size[1]
    print(aspect_ratio)
    if aspect_ratio >= 0.5 and aspect_ratio <= 2:
        return True
    else:
        return False

print(valid_media('/home/omegav/git/Blink/images/b0v2ly.gif'))