from PIL import Image
import xml.etree.ElementTree as ET

ALTO_NS = {"alto": "http://www.loc.gov/standards/alto/ns-v4#"}
PAGE_NS = {
    "page": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
}

def text_normalize(s: str) -> str:
    return " ".join(s.strip().split())

def crop(img: Image.Image, x, y, w, h, margin=2) -> Image.Image:

    x0 = max(x - margin, 0)
    y0 = max(y - margin, 0)
    x1 = min(x + w + margin, img.width)
    y1 = min(y + h + margin, img.height)
    return img.crop((x0, y0, x1, y1))

def parse_alto(xml_str: str):
    """get (x, y, w, h, text) from ALTO TextLine. Prefer TextLine box; fallback to union of Strings."""
    root = ET.fromstring(xml_str)
    for tl in root.findall(".//alto:TextLine", ALTO_NS):

        strings = tl.findall(".//alto:String", ALTO_NS)
        words = [s.attrib.get("CONTENT", "") for s in strings]
        text = text_normalize(" ".join(w for w in words if w))

        if not text:
            continue

        # Prefer line-level bbox if present
        attrs = tl.attrib
        def _num(a):
            return int(float(a))  # ALTO uses floats; cast safely
        if all(k in attrs for k in ("HPOS", "VPOS", "WIDTH", "HEIGHT")):
            x, y = _num(attrs["HPOS"]), _num(attrs["VPOS"])
            w, h = _num(attrs["WIDTH"]), _num(attrs["HEIGHT"])
        else:
            # Fallback: union over word boxes
            xs, ys, xe, ye = [], [], [], []
            for s in strings:
                a = s.attrib
                if all(k in a for k in ("HPOS", "VPOS", "WIDTH", "HEIGHT")):
                    x0, y0 = _num(a["HPOS"]), _num(a["VPOS"])
                    w0, h0 = _num(a["WIDTH"]), _num(a["HEIGHT"])
                    xs.append(x0); ys.append(y0)
                    xe.append(x0 + w0); ye.append(y0 + h0)
            if not xs:
                continue
            x, y, w, h = min(xs), min(ys), max(xe) - min(xs), max(ye) - min(ys)

        yield x, y, w, h, text


def parse_page(xml_str: str):
    """Get bounding boxes and text from PAGE XML text lines."""
    root = ET.fromstring(xml_str)

    for text_line in root.findall(".//page:TextLine", PAGE_NS):
        coords = text_line.find("./page:Coords", PAGE_NS)
        points = [
            tuple(map(int, point.split(",")))
            for point in coords.attrib["points"].split()
        ]
        xs, ys = zip(*points)

        x = min(xs)
        y = min(ys)
        width = max(xs) - x
        height = max(ys) - y
        text = text_line.find("./page:TextEquiv/page:Unicode", PAGE_NS).text

        yield x, y, width, height, text
