from PIL import Image
from pathlib import Path
from itertools import zip_longest
import os

file_txt = "Icons.h"

def writeImg(file, pixels, sizeX, sizeY, name):
    file.write("const unsigned int {0}_X = {1};\n".format(name, sizeX))
    file.write("const unsigned int {0}_Y = {1};\n".format(name, sizeY))

    file.write("const unsigned char {0}[] PROGMEM =\n".format(name))
    file.write("{\n")

    file.write("\t0X{:02X}".format(pixels.pop(0)))
    for pixel in pixels:
        file.write(", 0X{:02X}".format(pixel))
    file.write("\n")

    file.write("};\n")
    file.write("\n")

def writeFileHead(file, filename):
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
    file.write("#endif\n")

def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return list(zip_longest(*[iter(iterable)]*n, fillvalue=padvalue))

def encodePixels(pixels, sizeX):
    rows = grouper(sizeX, pixels, 0);
    data = []
    for row in rows:
        data.append(grouper(8, row, 0))

    data_encoded = []
    for row in data:
        for byte in row:
            binary = ""
            for value in byte:
                if value > 125:
                    binary += "1"
                else:
                    binary += "0"
            data_encoded.append(int(binary, 2))

    return data_encoded

def main():
    #Load Textfile
    txt = open(file_txt, "w+")
    writeFileHead(txt, file_txt)

    #All bmp files as list
    files = os.listdir()
    files_bmp = [i for i in files if i.endswith('.bmp')]

    for bmp in files_bmp:
        #Load Image
        img = Image.open(bmp)
        pixels = list(img.getdata())
        sizeX = img.size[0];
        sizeY = img.size[1];
        name = Path(bmp).stem

        pixels_encoded = encodePixels(pixels, sizeX)

        writeImg(txt, pixels_encoded, sizeX, sizeY, name)

    writeFileFoot(txt)
    txt.close()

if __name__ == '__main__':
    main()
