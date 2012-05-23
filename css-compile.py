import sys, os, hashlib, logging, json
import cssutils

FILENAME_POSTFIX = ".css"
OUT_PREFIX = '_'

cssutils.log.setLevel(logging.ERROR)
cssutils.ser.prefs.useMinified()

def process_file(source):
    sheet = cssutils.resolveImports(cssutils.parseFile(source))
    hash = hashlib.md5()
    hash.update(sheet.cssText)
    filename = OUT_PREFIX + hash.hexdigest() + FILENAME_POSTFIX
    with open(filename, "w") as out:
        out.write(sheet.cssText)
    return {source : filename}

def process_dir(dir):
    os.chdir(dir)
    file_map = {}
    for filename in [f for f in os.listdir(".") if f.endswith(FILENAME_POSTFIX) and not f.startswith(OUT_PREFIX)]:
        file_map.update(process_file(filename))
    with open("file_map.json", "w") as out:
        out.write(json.dumps(file_map))

if __name__ == "__main__":
    try:
        process_dir(sys.argv[1])
    except IndexError:
        sys.exit('Usage: {0} DIRNAME'.format(sys.argv[0]))