import cv2, binascii
from PIL import Image
from random import choice
import numpy as np
import sys
from itertools import repeat
import itertools
import struct
import binascii
import math

from core.colors import *
from core.utils import status

# set numpy threashold
np.set_printoptions(threshold=sys.maxsize)

# Function > Convert Image Pixel Number To Coordinate Value
def pixelNumberToCoordinate(n, img):
    return (n%img.size[0], n//img.size[0])


# Function > Convert Image Coordinate Number To Pixel Value
def coordinateToPixelNumber(x, y, img):
    return y*img.size[0]+x


# Function > Set the Least-Significant-Bit Value
def setLSB(v, state):
    if state == "0":
        return v & 0b11111110
    elif state == "1":
        return v | 0b00000001
    else:
        print(f"invalid state: {state}")
        return v


# Function > Write Data Using LPS
def write(data, pixel, nextP, img):
    pix = img.load()
    x, y = pixelNumberToCoordinate(nextP, img)
    l = len(data)
    # binari representation of next pixel x
    col = bin(x)[2:].zfill(l)
    # binari representation of next pixel y
    lin = bin(y)[2:].zfill(l)

    for i in range(pixel, pixel+l):
        p = pix[pixelNumberToCoordinate(i, img)]
        if len(p) == 4:
            # With alpha channel
            pix[pixelNumberToCoordinate(i, img)] = (
            setLSB(p[0], data[i-pixel]),
            setLSB(p[1], col[i-pixel]),
            setLSB(p[2], lin[i-pixel]),
            p[3])
        else:
            # no alpha channel
            pix[pixelNumberToCoordinate(i, img)] = (
            setLSB(p[0], data[i-pixel]),
            setLSB(p[1], col[i-pixel]),
            setLSB(p[2], lin[i-pixel]))


# Function > Binary Formating String
def toBin(string: str) -> bytes:
    # use struct module to convert string to bytes object
    b = struct.pack("s", string)
    # use bin function to convert bytes object to binary string
    h = "{:x}".format(int.from_bytes(b, "big"))
    # use binascii.unhexlify to convert hexadecimal string to bytes object
    return binascii.unhexlify(h)


# Function > Convert Strings In Chunks Of Length
def chunkstring(string, length):
    return [string[0+i:length+i].ljust(length, "0") for i in range(0, len(string), length)]


# Function > Encode Using LSB-LPS Technique
def LPS_Encode(src, secret_message, dst, startingPixel=(0,0)):
    coordinate_vals_array = []
    img = Image.open(src)
    BLOCKLEN = len(bin(max(img.size))[2:])
    # The number of pixels in the image
    total = img.size[0] * img.size[1]
    # list of available block positions
    AVAILABLE = [x for x in range(1, total-1, BLOCKLEN)]
    # Check if the last position is big enough
    if AVAILABLE[-1] + BLOCKLEN >= total:
        AVAILABLE.pop()

    d = chunkstring(toBin(secret_message.encode('utf8')),BLOCKLEN)
    n = len(d)
    # choose the first pixel
    pixel = coordinateToPixelNumber(startingPixel[0], startingPixel[1], img)
    if pixel == 0:
        # Choose a random location because (0, 0) is not authorized
        pixel = choice(AVAILABLE)
        AVAILABLE.remove(pixel)
        startingPixel = pixelNumberToCoordinate(pixel, img)
    for i in range(n-1):
        # pointer to the next pixel
        nextP = choice(AVAILABLE)
        AVAILABLE.remove(nextP)
        write(d[i], pixel, nextP, img)
        # switch to next pixel
        pixel = nextP
    # last pointer towards NULL (0, 0)
    write(d[-1], pixel, 0, img)
    img.save(dst)
    img.close()

    # startingPixel format = (x, y)
    pixel_range = str(startingPixel)
    pixel_range = pixel_range[1:-1] # x, y
    pixel_coordinate_values = pixel_range.split(",")

    # save lps coordinate values to array
    coordinate_vals_array.append(pixel_coordinate_values[0])
    coordinate_vals_array.append(pixel_coordinate_values[1])

    # return the coordinates
    return coordinate_vals_array


# Function > Binary To String Conversion
def binToString(i: str) -> bytes:
    # pad i to be a multiple of 8
    padding = 8 - len(i) % 8
    i = i.rjust(len(i) + padding, "0")
    # use format method to build hexadecimal string
    h = "{:x}".format(int(i, 2))
    # use binascii.unhexlify to convert hexadecimal string to bytes object
    return binascii.unhexlify(h)


# Function > Get Data From Encoded Image
def getData(img, startX, startY):
    # use struct.pack and struct.unpack to convert between pixel coordinates and pixel numbers
    n = struct.pack("<HH", startX, startY)
    n = struct.unpack("<I", n)[0]
    pix = img.load()
    # use bit_length method to compute length of binary representation of maximum pixel value
    BLOCKLEN = max(img.size).bit_length()
    # use generator expression to build nx, ny, and s strings
    nx = "".join(str((pix[n+i][1] >> 1) & 1) for i in repeat(BLOCKLEN))
    ny = "".join(str((pix[n+i][2] >> 1) & 1) for i in repeat(BLOCKLEN))
    s = "".join(str((pix[n+i][0] >> 1) & 1) for i in repeat(BLOCKLEN))
    # use int function to convert binary strings to integers
    nx = int(nx, 2)
    ny = int(ny, 2)
    return (s,(nx, ny))


# Function > Decode Using LSB-LPS Technique
def LPS_Decode(dst, x_coordinate, y_coordinate):
    # load pixel coordinate values from config file
    img = Image.open(dst)
    data, p = getData(img, x_coordinate, y_coordinate)
    while p != (0, 0):
        d, p = getData(img, p[0], p[1])
        data += d
    secret_message = binToString(data)
    return secret_message


# Function > LSB Encode Image
def LSB_Encode(src, message, dest):
    img = Image.open(src, 'r')
    width, height = img.size
    array = np.array(list(img.getdata()))
    if img.mode == 'RGB':
        n = 3
        m = 0
    elif img.mode == 'RGBA':
        n = 4
        m = 1
    total_pixels = array.size//n
    message += "$t3g0"
    b_message = ''.join([format(ord(i), "08b") for i in message])
    req_pixels = len(b_message)
    if req_pixels > total_pixels:
        status(3, "Need Larger File Size")
        exit()
    else:
        index=0
        for p, q in itertools.product(range(total_pixels), range(m, n)):
            if index < req_pixels:
                array[p][q] = int(bin(array[p][q])[2:9] + b_message[index], 2)
                index += 1
        array=array.reshape(height, width, n)
        enc_img = Image.fromarray(array.astype('uint8'), img.mode)
        enc_img.save(dest)
        status(2, "LSB Steganography Successful")


# Function > LSB Decode Image
def LSB_Decode(src):
    img = Image.open(src, 'r')
    array = np.array(list(img.getdata()))
    if img.mode == 'RGB':
        n = 3
        m = 0
    elif img.mode == 'RGBA':
        n = 4
        m = 1
    total_pixels = array.size//n
    hidden_bits = ""
    for p in range(total_pixels):
        for q in range(m, n):
            hidden_bits += (bin(array[p][q])[2:][-1])
    hidden_bits = [hidden_bits[i:i+8] for i in range(0, len(hidden_bits), 8)]
    message = ""
    for i in range(len(hidden_bits)):
        if message[-5:] == "$t3g0":
            break
        else:
            message += chr(int(hidden_bits[i], 2))
    if "$t3g0" in message:
        secret_message = message[:-5]
        return secret_message
    else:
        status(3, "No hidden message found using")
