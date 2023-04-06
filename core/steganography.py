import cv2
import binascii
import numpy as np
import sys
from PIL import Image
from secrets import choice
from random import sample

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
    if state in ("0", "1"):
        return (v & 0b11111110) | int(state)
    else:
        print(f"invalid state: {state}")
        return v


# Function > Write Data Using LPS
def write(data, pixel, nextP, img):
    pix = img.load()
    x, y = pixelNumberToCoordinate(nextP, img)
    l = len(data)
    col, lin = bin(x)[2:].zfill(l), bin(y)[2:].zfill(l)

    for i in range(pixel, pixel + l):
        coord = pixelNumberToCoordinate(i, img)
        p = pix[coord]
        new_pixel = (
            setLSB(p[0], data[i - pixel]),
            setLSB(p[1], col[i - pixel]),
            setLSB(p[2], lin[i - pixel]),
        )
        if len(p) == 4:
            new_pixel += (p[3],)
        pix[coord] = new_pixel


# Function > Binary Formating String
def toBin(string):
    return ''.join(format(x, 'b').zfill(8) for x in string)


# Function > Convert Strings In Chunks Of Length
def chunkstring(string, length):
    return [string[0+i:length+i].ljust(length, "0") for i in range(0, len(string), length)]


# Function > Encode Using LSB-LPS Technique
def LPS_Encode(src, secret_message, dst, startingPixel=(0,0)):
    img = Image.open(src)
    BLOCKLEN = len(bin(max(img.size))[2:])
    total_pixels = img.size[0] * img.size[1]
    AVAILABLE = [x for x in range(1, total_pixels - 1, BLOCKLEN)]
    if AVAILABLE[-1] + BLOCKLEN >= total_pixels:
        AVAILABLE.pop()

    d = chunkstring(toBin(secret_message.encode("utf8")), BLOCKLEN)
    n = len(d)
    pixel = coordinateToPixelNumber(*startingPixel, img)
    
    if pixel == 0:
        pixel = choice(AVAILABLE)
        AVAILABLE.remove(pixel)
        startingPixel = pixelNumberToCoordinate(pixel, img)

    # Shuffle AVAILABLE list once and iterate through it
    shuffled_AVAILABLE = sample(AVAILABLE, len(AVAILABLE))

    for nextP in shuffled_AVAILABLE[:n - 1]:
        write(d.pop(0), pixel, nextP, img)
        AVAILABLE.remove(nextP)
        pixel = nextP

    write(d.pop(), pixel, 0, img)
    img.save(dst)
    img.close()

    return [str(startingPixel[0]), str(startingPixel[1])]


# Function > Binary To String Conversion
def binToString(i):
    # Pad i to be a multiple of 8
    padding = (-len(i)) % 8
    i += "0" * padding
    # Convert padded binary string to bytes
    b = bytearray()
    for idx in range(0, len(i), 8):
        b.append(int(i[idx:idx + 8], 2))
    # Remove last null byte
    return bytes(b[:-1])


# Function > Get Data From Encoded Image
def getData(img, startX, startY):
    n = coordinateToPixelNumber(startX, startY, img)
    pix = img.load()
    BLOCKLEN = len(bin(max(img.size))[2:])
    nx = ""
    ny = ""
    s = ""
    for i in range(BLOCKLEN):
        c = pixelNumberToCoordinate(n+i, img)
        s += str(pix[c][0] & 1)
        nx += str(pix[c][1] & 1)
        ny += str(pix[c][2] & 1)
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
        msg_status("ERROR", "Need Larger File Size")
        exit()
    else:
        index=0
        for p in range(total_pixels):
            for q in range(m, n):
                if index < req_pixels:
                    array[p][q] = int(bin(array[p][q])[2:9] + b_message[index], 2)
                    index += 1
        array=array.reshape(height, width, n)
        enc_img = Image.fromarray(array.astype('uint8'), img.mode)
        enc_img.save(dest)
        msg_status("INFO", "LSB Steganography Successful")


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
        msg_status("ERROR", "No hidden message found using")
