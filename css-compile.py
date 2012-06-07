import sys, os, hashlib, logging, xml.dom.minidom
import cssutils

FILENAME_POSTFIX = ".css"
OUT_PREFIX = '_'

cssutils.log.setLevel(logging.WARNING)
cssutils.ser.prefs.useMinified()

def process_file(source):
    sheet = cssutils.resolveImports(cssutils.parseFile(source))
    hash = hashlib.md5()
    hash.update(sheet.cssText)
    filename = OUT_PREFIX + hash.hexdigest() + FILENAME_POSTFIX
    with open(filename, "w") as out:
        out.write(sheet.cssText)
    return source, filename

def process_dir(dir, orig_dir):
    os.chdir(dir)

    doc = xml.dom.minidom.Document()
    root_node = doc.createElement('static_urls')
    doc.appendChild(root_node)

    for filename in [f for f in os.listdir(".") if f.endswith(FILENAME_POSTFIX) and not f.startswith(OUT_PREFIX)]:
        item = process_file(filename)
        node = doc.createElement('url')
        node.setAttribute('source', item[0])
        node.setAttribute('target', item[1])
        root_node.appendChild(node)

    with open("mapping.xml", "w") as out:
        doc.writexml(out)

    os.chdir(orig_dir)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit('Usage: {0} DIRNAME [DIRNAME...]'.format(sys.argv[0]))
    orig_dir = os.getcwd()
    for dir in sys.argv[1:]:
        process_dir(dir, orig_dir)
