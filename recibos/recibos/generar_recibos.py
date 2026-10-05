# Genera un PDF de recibo por universidad/alumno leyendo la pestana 'datos' del Sheet.
# Incrusta el logo (prioriza vector SVG > PDF > PNG > JPG) desde la carpeta logos\.
# Exporta: pdfs\<Universidad> - <Nombre Apellido>.pdf
import os, re, sys, glob
sys.path.insert(0, r"C:\Users\mama\Desktop\google sheetse\metodo")
import sheets
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

SHEET_ID = "1pwgqz-dZZSrXj4_ndrUHk9iBzdkQhp7J1Dn37CBeB7E"
TAB      = "datos"
BASE     = os.path.dirname(os.path.abspath(__file__))
LOGOS    = os.path.join(BASE, "logos")
OUTDIR   = os.path.join(BASE, "pdfs")
os.makedirs(OUTDIR, exist_ok=True)

NAVY   = HexColor("#0b2a4a")
RULE   = HexColor("#9b9b9b")
LINK   = HexColor("#1a4f8b")
HEADG  = HexColor("#e9e9e9")
LIGHT  = HexColor("#eef0f2")
BLACK  = HexColor("#1a1a1a")
THEAD  = HexColor("#555f63")
PAGE_W, PAGE_H = letter
LM = 10; RM = PAGE_W - 10

COLX = {"crn":12,"course":44,"title":84,"campus":190,"credits":243,"level":280,
        "start":308,"end":350,"days":396,"time":430,"loc":483,"instr":560}
ORDER = ["crn","course","title","campus","credits","level","start","end","days","time","loc","instr"]
LABEL = {"crn":"CRN","course":"Course","title":"Title","campus":"Campus","credits":"Credits",
         "level":"Level","start":"Start\nDate","end":"End\nDate","days":"Days","time":"Time",
         "loc":"Location","instr":"Instructor"}

# -------- datos --------
CACHE = os.path.join(BASE, "datos_cache.tsv")
import csv as _csv
def _parse(v):
    groups = []; cur = None
    for r in v[1:]:
        if not any(c.strip() for c in r):
            continue
        code = r[18].strip()
        def cell(idx): return r[idx] if len(r) > idx else ""
        if code:  # nueva inscripcion (fila con datos de estudiante)
            cur = {"first":r[0],"last":r[1],"level":r[2],"college":r[3],"major":r[4],"minor":r[5],
                   "addr":r[6],"campus":r[10],"start":r[12],"end":r[13],"code":code,"season":r[19],
                   "class":r[20],"exp_y":r[21],"exp_m":r[22],"exp_d":r[23],"exp_h":r[24],
                   "rate":cell(25),"tuition":cell(26),"ssf":cell(27),"tech":cell(28),"health":cell(29),
                   "reg":cell(30),"total":cell(31),"method":cell(32),"receipt":cell(33),"courses":[]}
            groups.append(cur)
        if cur is None:
            continue
        cur["courses"].append({"crn":r[7],"course":r[8],"title":r[9],"credits":r[11],
                                "days":r[14],"time":r[15],"loc":r[16],"instr":r[17]})
    return groups

def leer():
    # intenta leer el Sheet en vivo; cachea; si falla, usa la cache local
    try:
        v = sheets.libro(SHEET_ID).worksheet(TAB).get_all_values()
        try:
            with open(CACHE, "w", encoding="utf-8", newline="") as f:
                _csv.writer(f, delimiter="\t").writerows(v)
        except Exception:
            pass
        return _parse(v)
    except Exception as e:
        if os.path.exists(CACHE):
            print(f"[aviso] no se pudo leer el Sheet en vivo ({type(e).__name__}); uso la cache local.")
            with open(CACHE, encoding="utf-8") as f:
                v = list(_csv.reader(f, delimiter="\t"))
            return _parse(v)
        raise SystemExit(
            "No se pudo leer el Google Sheet y no hay cache local.\n"
            "Causa tipica: el token de Google (authorized_user.json) expiro o no pudo refrescarse.\n"
            "Solucion: vuelve a copiar un authorized_user.json valido a %APPDATA%\\gspread\\ "
            "y corre de nuevo. Detalle: " + f"{type(e).__name__}: {e}")

# -------- logo --------
PRIO = {"svg":0,"pdf":1,"png":2,"jpg":3,"jpeg":3,"JPG":3,"webp":4}
def find_logo(univ):
    best = None; bestp = 99
    for f in glob.glob(os.path.join(LOGOS, "* - *.*")):
        b = os.path.basename(f)
        name, ext = b.rsplit(".", 1)
        # quita prefijo de pais "USA - " / "CANADA - "
        core = name.split(" - ", 1)[1] if " - " in name else name
        if core.strip().lower() == univ.strip().lower():
            p = PRIO.get(ext.lower(), 9)
            if p < bestp:
                best, bestp = f, p
    return best

# ---- color emblematico por universidad (de su logo) ----
import re as _re
from collections import Counter as _Counter
def _sat(r,g,b): return max(r,g,b)-min(r,g,b)
def _pick(cnt):
    if not cnt: return None
    top = cnt.most_common(12); best=None; bs=-1
    for col,n in top:
        s = _sat(*col) * (0.5 + n/top[0][1])
        if s > bs: bs=s; best=col
    return best
def _color_raster(path):
    from PIL import Image
    im = Image.open(path).convert("RGBA"); im.thumbnail((100,100))
    cnt=_Counter()
    for r,g,b,a in im.getdata():
        if a<128 or min(r,g,b)>235 or max(r,g,b)<20: continue
        cnt[(r//24*24,g//24*24,b//24*24)] += 1
    return _pick(cnt)
def _color_svg(path):
    txt=open(path,encoding="utf-8",errors="ignore").read()
    cols=[]
    for m in _re.findall(r'#([0-9a-fA-F]{6})',txt):
        cols.append((int(m[0:2],16),int(m[2:4],16),int(m[4:6],16)))
    for m in _re.findall(r'#([0-9a-fA-F]{3})\b',txt):
        cols.append((int(m[0]*2,16),int(m[1]*2,16),int(m[2]*2,16)))
    for r,g,b in _re.findall(r'rgb\((\d+)[, ]+(\d+)[, ]+(\d+)\)',txt):
        cols.append((int(r),int(g),int(b)))
    cnt=_Counter()
    for col in cols:
        if min(col)>235 or max(col)<20: continue
        cnt[col]+=1
    return _pick(cnt)
def univ_color(path):
    if not path: return NAVY
    try:
        c = _color_svg(path) if path.rsplit(".",1)[1].lower()=="svg" else _color_raster(path)
    except Exception:
        c=None
    return HexColor('#%02x%02x%02x'%c) if c else NAVY
def readable(col):
    r,g,b=int(col.red*255),int(col.green*255),int(col.blue*255)
    lum=0.299*r+0.587*g+0.114*b
    if lum>175:
        f=150/max(lum,1); r,g,b=int(r*f),int(g*f),int(b*f)
    return HexColor('#%02x%02x%02x'%(r,g,b))
def fit_size(c, text, maxw, font, maxs, mins):
    s=maxs
    while s>mins and c.stringWidth(str(text),font,s)>maxw: s-=0.5
    return s

def draw_logo(c, path, x, y, maxw, maxh):
    if not path: return False
    ext = path.rsplit(".",1)[1].lower()
    try:
        if ext == "svg":
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPDF
            d = svg2rlg(path)
            if not d or not d.width or not d.height: return False
            s = min(maxw/d.width, maxh/d.height)
            d.scale(s, s); d.width*=s; d.height*=s
            renderPDF.draw(d, c, x, y)
            return True
        else:
            img = ImageReader(path)
            iw, ih = img.getSize()
            s = min(maxw/iw, maxh/ih)
            w, h = iw*s, ih*s
            c.drawImage(img, x, y+(maxh-h)/2, w, h, mask='auto', preserveAspectRatio=True)
            return True
    except Exception as e:
        sys.stderr.write(f"logo fail {os.path.basename(path)}: {e}\n")
        return False

def lines(c, x, y, text, font, size, color, lead):
    c.setFont(font, size); c.setFillColor(color)
    for i, ln in enumerate(str(text).split("\n")):
        c.drawString(x, y - i*lead, ln)

def clip(c, text, maxw, font, size):
    text = str(text)
    if c.stringWidth(text, font, size) <= maxw:
        return text
    while text and c.stringWidth(text+"…", font, size) > maxw:
        text = text[:-1]
    return text + "…"

# ancho disponible por columna de la tabla
COLW = {}
for _i, _k in enumerate(ORDER):
    _nx = (RM if _i == len(ORDER)-1 else COLX[ORDER[_i+1]])
    COLW[_k] = _nx - COLX[_k] - 3

def safe(s):
    return re.sub(r'[\\/:*?"<>|]', "", s).strip()

def norm_md(s):
    return re.sub(r'^\s*([A-Za-z]{3})', lambda m: m.group(1).capitalize(), str(s).strip())

def money(x):
    return f"${x:,.2f}"

import hashlib
SIS_LIST = ["Ellucian Banner","Oracle PeopleSoft Campus Solutions","Workday Student",
            "Jenzabar One","Anthology Student","Ellucian Colleague"]
def sis_for(univ):
    return SIS_LIST[int(hashlib.md5(univ.encode()).hexdigest()[:6],16) % len(SIS_LIST)]
def set_meta(c, kind, g):
    univ = g["campus"]; name = f"{g['first']} {g['last']}"; sis = sis_for(univ)
    c.setTitle(f"{kind} - {univ} - {name} - {g['season']}")
    c.setAuthor(univ)
    c.setSubject(f"{kind} | {g['season']} | Student ID {g['code']} | Receipt {g.get('receipt','')}".strip(" |"))
    c.setKeywords(f"{name}; {g['code']}; {g['season']}; {univ}; {kind}")
    c.setCreator(sis)
    c.setProducer(f"{sis} Student Information System")

def tuition_plan(univ, credits):
    h = int(hashlib.md5(univ.encode()).hexdigest()[:8], 16)
    is_cc = ("Community" in univ or "Technical" in univ) or (" College" in univ and "University" not in univ)
    rate = (120 + h % 160) if is_cc else (360 + h % 840)
    rate = round(rate/5)*5
    items = [("Tuition  (%d cr @ %s/cr)" % (int(round(credits)), money(rate)), rate*credits),
             ("Student Services Fee", 150 + h % 180),
             ("Technology Fee",        90 + h % 110),
             ("Health Services Fee",   70 + h % 90),
             ("Registration Fee",      50.0)]
    items = [(d, float(v)) for d, v in items]
    subtotal = sum(v for _, v in items)
    # metodo de pago deterministico
    if h % 3 == 0:
        method = "Financial Aid Disbursement"
    else:
        last4 = f"{(h % 9000)+1000}"
        method = f"Visa ending {last4}"
    return rate, items, subtotal, method

# -------- un recibo --------
def build_pdf(g):
    univ = g["campus"]
    fname = f"{safe(univ)} - {safe(g['first']+' '+g['last'])} - Schedule.pdf"
    path = os.path.join(OUTDIR, fname)
    c = canvas.Canvas(path, pagesize=letter)
    set_meta(c, "Concise Student Schedule", g)

    # color emblematico de la universidad (de su logo)
    logo = find_logo(univ)
    primary = univ_color(logo)
    tcol = readable(primary)

    top = PAGE_H - 10
    c.setFillColor(primary); c.rect(0, top-6, PAGE_W, 6, fill=1, stroke=0)

    # logo + nombre universidad (ajusta tamano para no cortarse)
    draw_logo(c, logo, LM+4, top-78, 150, 62)
    tx = LM+168; avail = RM - tx - 4
    ts = fit_size(c, univ, avail, "Helvetica-Bold", 20, 10)
    c.setFillColor(tcol); c.setFont("Helvetica-Bold", ts)
    c.drawString(tx, top-42, univ)

    # tabs
    _lp = 0.299*primary.red*255 + 0.587*primary.green*255 + 0.114*primary.blue*255
    tabtxt = HexColor("#ffffff") if _lp < 140 else HexColor("#1a1a1a")
    ty = top-98
    c.setFillColor(primary); c.rect(LM, ty, 60, 15, fill=1, stroke=0)
    c.setFillColor(tabtxt); c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(LM+30, ty+4, "Student")
    c.setFillColor(HexColor("#303030")); c.rect(LM+62, ty, 80, 15, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff")); c.drawCentredString(LM+102, ty+4, "Financial Aid")
    c.setFillColor(LINK); c.setFont("Helvetica-Bold", 8)
    c.drawRightString(RM, ty+30, "RETURN TO MENU   SITE MAP   HELP   EXIT")

    # titulo + id
    ly = ty-26
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold", 17)
    c.drawString(LM, ly, "Concise Student Schedule")
    c.setFillColor(LINK); c.setFont("Helvetica-Bold", 8)
    c.drawRightString(RM, ly+8, f"{g['code']}  {g['first']} {g['last']}")
    c.setFillColor(HexColor("#333333")); c.setFont("Helvetica", 8)
    c.drawRightString(RM, ly-2, g["season"])
    c.drawRightString(RM, ly-12, f"{g['exp_m']} {g['exp_d']}, {g['exp_y']} {g['exp_h']}")
    c.setFillColor(primary); c.rect(LM, ly-20, RM-LM, 2.5, fill=1, stroke=0)

    # intro
    iy = ly-36
    c.setFillColor(primary); c.circle(LM+5, iy+2, 5, fill=1, stroke=0)
    c.setFillColor(HexColor("#333333")); c.setFont("Helvetica", 8)
    c.drawString(LM+16, iy, "This page lists the classes for which you are registered for the term. "
                            "All of the detail information about the class is included.")
    c.setFillColor(LINK); c.setFont("Helvetica-Bold", 9)
    c.drawString(LM+16, iy-18, "Buy your Textbooks")

    # bloque estudiante
    gy = iy-40; lh = 11; row = gy
    info = [("Name:", f"{g['first']} {g['last']}"),("Classification:", g["class"]),
            ("Level:", g["level"]),("College:", g["college"]),
            ("Major and\nDepartment:", g["major"]),("Minor:", g["minor"])]
    for lbl, val in info:
        n = max(lbl.count("\n"), val.count("\n"))+1
        c.setFillColor(HEADG); c.rect(LM, row-(n-1)*lh-2, 120, n*lh, fill=1, stroke=0)
        lines(c, LM+2, row, lbl, "Helvetica-Bold", 8, BLACK, lh)
        lines(c, LM+125, row, val, "Helvetica", 8, BLACK, lh)
        row -= n*lh + 2
    # direccion (de una sola linea -> partir por comas en 3)
    ax = 425
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold", 8); c.drawString(ax, gy, "Address:")
    parts = [p.strip() for p in g["addr"].split(",")]
    aline = [parts[0] if parts else ""]
    if len(parts) >= 4:
        aline = [parts[0], f"{parts[1]}, {parts[2]}", parts[3]]
    elif len(parts) > 1:
        aline = [parts[0], ", ".join(parts[1:])]
    c.setFont("Helvetica", 8)
    for i, ln in enumerate(aline):
        c.drawString(ax+42 if i==0 else ax+42, gy - i*lh, ln)

    # tabla cursos
    ty0 = row-14
    c.setFillColor(HEADG); c.rect(LM, ty0-18, RM-LM, 26, fill=1, stroke=0)
    for col in ORDER:
        lines(c, COLX[col], ty0, LABEL[col], "Helvetica-Bold", 7.5, THEAD, 9)
    c.setStrokeColor(RULE); c.setLineWidth(0.6); c.line(LM, ty0-20, RM, ty0-20)

    def two_date(s):
        s = _re.sub(r'^\s*([A-Za-z]{3})', lambda m: m.group(1).capitalize(), str(s).strip())
        p = s.split(", ")
        return f"{p[0]},\n{p[1]}" if len(p) == 2 else s
    def two_time(t):
        return t.replace(" - ", " -\n", 1)
    def wrap2(txt, maxw, font, size):
        words = str(txt).split(); l1=""; l2=""
        for w in words:
            if c.stringWidth((l1+" "+w).strip(), font, size) <= maxw or not l1:
                l1 = (l1+" "+w).strip()
            else:
                l2 = (l2+" "+w).strip()
        if l2: l2 = clip(c, l2, maxw, font, size)
        return l1 if not l2 else l1+"\n"+l2

    city = g["campus"]
    ap = [p.strip() for p in g["addr"].split(",")]
    if len(ap) >= 2: city = ap[1]
    MULTI = {"start","end","time","loc"}
    cy = ty0-30; shade=False; total=0.0
    for crs in g["courses"]:
        try: total += float(crs["credits"])
        except: pass
        if shade:
            c.setFillColor(LIGHT); c.rect(LM, cy-10, RM-LM, 20, fill=1, stroke=0)
        vals = {"crn":crs["crn"],"course":crs["course"],"title":crs["title"],"campus":city,
                "credits":crs["credits"],"level":("UG" if g["level"] in("Undergraduate","Associate") else "GR"),
                "start":two_date(g["start"]),"end":two_date(g["end"]),"days":crs["days"],
                "time":two_time(crs["time"]),"loc":wrap2(crs["loc"],COLW["loc"],"Helvetica",7.3),
                "instr":crs["instr"]}
        for col in ORDER:
            color = LINK if col=="course" else BLACK
            txt = vals[col] if col in MULTI else clip(c, vals[col], COLW[col], "Helvetica", 7.3)
            lines(c, COLX[col], cy, txt, "Helvetica", 7.3, color, 9)
        cy -= 20; shade = not shade

    cy -= 2
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold", 8)
    c.drawString(COLX["campus"], cy, "Total"); c.drawString(COLX["campus"], cy-10, "Credits:")
    c.setFont("Helvetica", 8); c.drawString(COLX["credits"], cy-5, f"{total:.3f}")
    c.setStrokeColor(RULE); c.setLineWidth(1); c.line(LM, cy-24, RM, cy-24)
    c.setFillColor(LINK); c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W/2, cy-46, "[ Student Detail Schedule ]")

    # Issue / Expiration (verificacion: emision <=90 dias, caducidad no vencida)
    issue = norm_md(f"{g['exp_m']} {g['exp_d']}, {g['exp_y']}")
    expire = norm_md(g["end"])
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold", 8)
    c.drawString(LM, cy-64, "Issue Date: ")
    c.setFont("Helvetica", 8); c.drawString(LM+58, cy-64, issue)
    c.setFont("Helvetica-Bold", 8); c.drawString(LM+170, cy-64, "Expiration Date: ")
    c.setFont("Helvetica", 8); c.drawString(LM+250, cy-64, expire)
    # pie
    c.setFillColor(primary); c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(PAGE_W/2, 24, "- Schedule")

    c.showPage(); c.save()
    return fname, bool(logo)

def build_payment(g):
    univ = g["campus"]
    name = f"{g['first']} {g['last']}"
    fname = f"{safe(univ)} - {safe(name)} - Payment Receipt.pdf"
    path = os.path.join(OUTDIR, fname)
    c = canvas.Canvas(path, pagesize=letter)
    set_meta(c, "Tuition Payment Receipt", g)

    logo = find_logo(univ)
    primary = univ_color(logo); tcol = readable(primary)
    _lp = 0.299*primary.red*255 + 0.587*primary.green*255 + 0.114*primary.blue*255
    tabtxt = HexColor("#ffffff") if _lp < 140 else HexColor("#1a1a1a")

    top = PAGE_H - 10
    c.setFillColor(primary); c.rect(0, top-6, PAGE_W, 6, fill=1, stroke=0)
    draw_logo(c, logo, LM+4, top-78, 150, 62)
    tx = LM+168; ts = fit_size(c, univ, RM-tx-4, "Helvetica-Bold", 20, 10)
    c.setFillColor(tcol); c.setFont("Helvetica-Bold", ts); c.drawString(tx, top-42, univ)
    # tab
    ty = top-98
    c.setFillColor(primary); c.rect(LM, ty, 110, 15, fill=1, stroke=0)
    c.setFillColor(tabtxt); c.setFont("Helvetica-Bold", 8); c.drawCentredString(LM+55, ty+4, "Student Account")
    c.setFillColor(LINK); c.setFont("Helvetica-Bold", 8)
    c.drawRightString(RM, ty+30, "ACCOUNT SUMMARY   MAKE A PAYMENT   HELP   EXIT")

    # titulo + id
    ly = ty-26
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold", 17); c.drawString(LM, ly, "Tuition Payment Receipt")
    c.setFillColor(LINK); c.setFont("Helvetica-Bold", 8); c.drawRightString(RM, ly+8, f"{g['code']}  {name}")
    c.setFillColor(HexColor("#333333")); c.setFont("Helvetica", 8)
    c.drawRightString(RM, ly-2, g["season"])
    c.drawRightString(RM, ly-12, f"Receipt No. {g.get('receipt') or g['code']}")
    c.setFillColor(primary); c.rect(LM, ly-20, RM-LM, 2.5, fill=1, stroke=0)

    # bloque estudiante
    gy = ly-40; lh=12; row=gy
    total_cr = sum(float(x["credits"]) for x in g["courses"] if x["credits"].strip())
    info = [("Name:", name),("Student ID:", g["code"]),("Level:", g["level"]),
            ("Program:", g["major"]),("Term:", g["season"]),("Total Credits:", f"{total_cr:.3f}")]
    for lbl,val in info:
        c.setFillColor(HEADG); c.rect(LM, row-2, 120, lh, fill=1, stroke=0)
        c.setFillColor(BLACK); c.setFont("Helvetica-Bold",8); c.drawString(LM+2,row,lbl)
        c.setFont("Helvetica",8); c.drawString(LM+125,row,str(val))
        row -= lh+2
    # issue / expiration (verificacion)
    issue = norm_md(f"{g['exp_m']} {g['exp_d']}, {g['exp_y']}"); expire = norm_md(g["end"])
    ax=330
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold",8); c.drawString(ax,gy,"Issue Date:")
    c.setFont("Helvetica",8); c.drawString(ax+90,gy,issue)
    c.setFont("Helvetica-Bold",8); c.drawString(ax,gy-14,"Expiration Date:")
    c.setFont("Helvetica",8); c.drawString(ax+90,gy-14,expire)
    c.setFont("Helvetica-Bold",8); c.drawString(ax,gy-28,"Billing Date:")
    c.setFont("Helvetica",8); c.drawString(ax+90,gy-28,f"{norm_md(g['start'])}")

    # tabla de cargos (datos vienen del Sheet)
    def _i(x):
        try: return int(float(x))
        except: return 0
    rate = _i(g["rate"]); method = g["method"] or "Payment on File"
    subtotal = _i(g["total"]) or (_i(g["tuition"])+_i(g["ssf"])+_i(g["tech"])+_i(g["health"])+_i(g["reg"]))
    items = [("Tuition  (%d cr @ %s/cr)" % (int(total_cr), money(rate)), _i(g["tuition"])),
             ("Student Services Fee", _i(g["ssf"])),
             ("Technology Fee",        _i(g["tech"])),
             ("Health Services Fee",   _i(g["health"])),
             ("Registration Fee",      _i(g["reg"]))]
    taby = row-16
    c.setFillColor(HEADG); c.rect(LM, taby-4, RM-LM, 18, fill=1, stroke=0)
    c.setFillColor(THEAD); c.setFont("Helvetica-Bold",8)
    c.drawString(LM+4, taby, "Description")
    c.drawRightString(RM-10, taby, "Amount")
    c.setStrokeColor(RULE); c.setLineWidth(0.6); c.line(LM, taby-7, RM, taby-7)
    yy = taby-22; shade=False
    for desc,amt in items:
        if shade: c.setFillColor(LIGHT); c.rect(LM, yy-4, RM-LM, 15, fill=1, stroke=0)
        c.setFillColor(BLACK); c.setFont("Helvetica",8.5); c.drawString(LM+6, yy, desc)
        c.drawRightString(RM-10, yy, money(amt)); yy-=15; shade=not shade
    c.setStrokeColor(RULE); c.setLineWidth(0.8); c.line(LM, yy+4, RM, yy+4)
    # totales
    def tot(lbl,val,bold=True,col=BLACK):
        nonlocal yy
        c.setFillColor(col); c.setFont("Helvetica-Bold" if bold else "Helvetica",9)
        c.drawRightString(RM-120, yy, lbl); c.drawRightString(RM-10, yy, val); yy-=15
    yy-=6
    tot("Total Charges:", money(subtotal))
    tot(f"Payment Received ({method}):", "-"+money(subtotal), bold=False)
    c.setStrokeColor(RULE); c.line(RM-230, yy+6, RM, yy+6)
    yy -= 10
    tot("Balance Due:", money(0.0), col=primary)

    c.setFillColor(HexColor("#666666")); c.setFont("Helvetica",7)
    c.drawString(LM, 40, "This receipt confirms payment for the term indicated above. Retain for your records.")
    c.setFillColor(primary); c.setFont("Helvetica-Bold",9)
    c.drawCentredString(PAGE_W/2, 24, "- Payment Receipt")
    c.showPage(); c.save()
    return fname, bool(logo)

def main():
    groups = leer()
    print(f"inscripciones: {len(groups)}")
    ok=0; nologo=set()
    for g in groups:
        f1,l1 = build_pdf(g)
        f2,l2 = build_payment(g)
        if not l1: nologo.add(g["campus"])
        ok += 2
        print(f"  [{'logo' if l1 else 'SIN LOGO'}] {f1}")
        print(f"  [{'logo' if l2 else 'SIN LOGO'}] {f2}")
    print(f"\nPDFs generados: {ok} ({len(groups)} schedules + {len(groups)} payment receipts) en {OUTDIR}")
    if nologo: print("sin logo:", sorted(nologo))

if __name__ == "__main__":
    main()
