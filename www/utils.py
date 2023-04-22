from qrcode import *
from django.conf import settings

# Function to generate QR code
def generate_qr(item_type,data,id):
    img = make(data)
    img_name = 'qr_'+item_type+"_"+str(id)+ '.png'
    img_url = settings.MEDIA_ROOT + 'qrcode/' + img_name
    img.save(img_url)
    return img_name


# Function to generate Unique code for every item
def generate_code(campus, department, category, ID):
    return "{}-{:04d}-{:04d}-{:04d}".format(campus, int(department.dep_code), int(category.cat_code),int(ID))


# Saving new Items
