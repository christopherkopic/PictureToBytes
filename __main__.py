from PIL import Image
from pathlib import Path
from itertools import zip_longest
from random import randint
import os
import textwrap

data_folder = "testdata"
file_format = ".bmp"
output_folder = "testoutput"
output_file = "Icons.h"

def writeImg(file, pixels, sizeX, sizeY, name):
    """Writes picture byte array into output file"""
    #Image Dimensions
    file.write("const unsigned int {0}_X = {1};\n".format(name, sizeX))
    file.write("const unsigned int {0}_Y = {1};\n".format(name, sizeY))

    #Array Header
    file.write("const unsigned char {0}[] PROGMEM =\n".format(name))
    file.write("{\n")

    #Array
    file.write("\t0X{:02X}".format(pixels.pop(0)))
    for pixel in pixels:
        file.write(", 0X{:02X}".format(pixel))
    file.write("\n")

    #Array Footer
    file.write("};\n")
    file.write("\n")

def writeFileHead(file, filename):
    """Header for output file"""
    name = Path(filename).stem
    file.write("#ifndef _{0}_H_\n".format(name))
    file.write("#define _{0}_H_\n".format(name))
    file.write("\n")
    file.write("#if defined(ESP8266) || defined(ESP32)\n")
    file.write("#include <pgmspace.h>\n")
    file.write("#else\n")
    file.write("#include <avr/pgmspace.h>\n")
    file.write("#endif\n")
    file.write("\n")

def writeFileFoot(file):
    """Footer for output file"""
    file.write("#endif\n")

def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return list(zip_longest(*[iter(iterable)]*n, fillvalue=padvalue))

def encodeBinary(pixels, sizeX):
    """Encodes a bitmap as a string of binary values inte an array of bytes for arduino image processing"""
    rows = grouper(sizeX, pixels, '0');
    data = []
    for row in rows:
        data.append(grouper(8, row, '0'))

    data_encoded = []
    for row in data:
        for byte in row:
            bytestring = "".join(byte)
            data_encoded.append(int(bytestring, 2))

    return data_encoded

def convertToBinary(pixels):
    """Converts an array of pixel values into a string of binary values through dithering"""
    binstring = ""
    i = 0
    for pixel in pixels:
        binstring += dither_random(pixel, 255)
    return binstring

def dither_random(value, maxdepth):
    """Dithers pixels by comparing their value with a random value within their color range"""
    if(value < randint(0, maxdepth)):
        return "0"
    else:
        return "1"

def main():
    #Load Textfile
    out_path = Path(output_folder)
    txt = open(out_path / output_file, "w+")
    writeFileHead(txt, output_file)

    #All bmp files as list
    import_files = os.listdir(data_folder)
    pictures = [i for i in import_files if i.endswith(file_format)]
    picture_path = Path(data_folder)

    for picture in pictures:
        #Load Image
        img = Image.open(picture_path / picture)
        img = img.convert('L')
        pixels = list(img.getdata())
        sizeX = img.size[0];
        sizeY = img.size[1];
        name = Path(picture).stem

        #Encode into bytearray
        binpixels = convertToBinary(pixels)
        bytearray = encodeBinary(binpixels, sizeX)

        #Write data into output file
        writeImg(txt, bytearray, sizeX, sizeY, name)

    writeFileFoot(txt)
    txt.close()

if __name__ == '__main__':
    main()
