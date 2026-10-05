# language: Python 3, file: rider_schedule.py, deps: pip install reportlab
# Edit STUDENT / COURSES / META below, run: python rider_schedule.py -> Concise_Student_Schedule.pdf

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# ----------------------------------------------------------------------------
# EDITABLE DATA
# ----------------------------------------------------------------------------
META = {
    "file_banner": "Concise Student Schedule.pdf",
    "file_sub":    "Saved to Dropbox · Jan 30, 2021 at 10:59 PM",
    "title":       "Concise Student Schedule",
    "student_id":  "006583195",
    "student_top": "Yordelie Cabreja",
    "term":        "Spring 2021",
    "stamp":       "Jan 30, 2021 10:58 pm",
    "intro":       "This page lists the classes for which you are registered for the term. "
                   "All of the detail information about the class is included.",
    "textbooks":   "Buy your Textbooks",
    "release":     "RELEASE: 8.7.1",
}

STUDENT = [
    ("Name:",              "Yordelie Cabreja"),
    ("Classification:",    "Freshmen"),
    ("Level:",             "Undergraduate"),
    ("College:",           "Liberal Arts and Sciences"),
    ("Major and\nDepartment:", "Health Sciences, Dept of Bio,Behv Neuro&Hlth\nSc"),
    ("",                   "Liberal Arts and Sciences"),
    ("Minor:",             "Health Administration"),
]

ADDRESS = [
    "749 Mary St.",
    "Perth Amboy, New",
    "Jersey  08861-2540",
    "Middlesex",
]

# row: crn, course, title, campus, credits, level, start, end, days, time, location, instructor
COURSES = [
    [["22139", "CMP 120\nL1", "Expository Writing", "Lawrenceville", "3.000", "UG",
      "Feb 01,\n2021", "May 11,\n2021", "TR", "1:10 pm -\n2:40 pm", "Online/Remote\nCLASS", "Strom"]],
    [["22068", "MTH 205", "Precalculus", "Lawrenceville", "4.000", "UG",
      "Feb 01,\n2021", "May 11,\n2021", "MTWF", "8:00 am -\n9:00 am", "Online/Remote\nCLASS", "Turkowski"]],
    [["24081", "NCT 023\n01", "Success Strategies\nfor Science", "Lawrenceville", "0.000", "UG",
      "Feb 01,\n2021", "May 11,\n2021", "R", "11:30 am -\n12:30 pm", "Online/Remote\nCLASS", "Houser"]],
    [["23339", "PSY 100\nN1", "Introduction to\nPsychology", "Lawrenceville", "3.000", "UG",
      "Feb 01,\n2021", "May 11,\n2021", "TR", "2:50 pm -\n4:20 pm", "Bart Luedeke\nCenter 245", "Dewees"],
     ["", "", "", "", "", "",
      "Feb 01,\n2021", "May 11,\n2021", "TR", "2:50 pm -\n4:20 pm", "Hybrid CLASS", "Dewees"]],
    [["22205", "SOC 201\nD1", "Health Care\nIn Society", "Lawrenceville", "3.000", "UG",
      "Feb 01,\n2021", "May 11,\n2021", "MWF", "11:30 am -\n12:30 pm", "Online/Remote\nCLASS", "Kubik"]],
]
TOTAL_CREDITS = "13.000"

# ----------------------------------------------------------------------------
# COLORS / GEOMETRY
# ----------------------------------------------------------------------------
MAROON   = HexColor("#7a001f")
GREY_BAR = HexColor("#9b9b9b")
LINKBLUE = HexColor("#1a4f8b")
HEADGRY  = HexColor("#e9e9e9")
LIGHTROW = HexColor("#eef0f2")
BLACK    = HexColor("#1a1a1a")
TABHEAD  = HexColor("#555f63")

PAGE_W, PAGE_H = letter
LM = 10
RM = PAGE_W - 10

COLX = {
    "crn": 12, "course": 44, "title": 84, "campus": 190, "credits": 243,
    "level": 280, "start": 308, "end": 350, "days": 396, "time": 430,
    "loc": 483, "instr": 560,
}
COL_ORDER = ["crn", "course", "title", "campus", "credits", "level",
             "start", "end", "days", "time", "loc", "instr"]
COL_LABEL = {
    "crn": "CRN", "course": "Course", "title": "Title", "campus": "Campus",
    "credits": "Credits", "level": "Level", "start": "Start\nDate",
    "end": "End\nDate", "days": "Days", "time": "Time", "loc": "Location",
    "instr": "Instructor",
}


def draw_lines(c, x, y, text, font, size, color, leading, link=False):
    c.setFont(font, size)
    c.setFillColor(color)
    for i, ln in enumerate(str(text).split("\n")):
        yy = y - i * leading
        c.drawString(x, yy, ln)
        if link:
            w = c.stringWidth(ln, font, size)
            c.setStrokeColor(color); c.setLineWidth(0.4)
            c.line(x, yy - 1.5, x + w, yy - 1.5)
    return y - text.count("\n") * leading


def build(path="Concise_Student_Schedule.pdf"):
    c = canvas.Canvas(path, pagesize=letter)

    # --- Dropbox file banner strip ---
    c.setFillColor(HexColor("#f7f7f7")); c.rect(0, PAGE_H - 52, PAGE_W, 52, fill=1, stroke=0)
    c.setFillColor(LINKBLUE); c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_W/2, PAGE_H - 20, META["file_banner"])
    c.setFillColor(HexColor("#777777")); c.setFont("Helvetica", 7.5)
    c.drawCentredString(PAGE_W/2, PAGE_H - 33, META["file_sub"])

    top = PAGE_H - 52

    # maroon top rule
    c.setFillColor(MAROON); c.rect(0, top - 6, PAGE_W, 6, fill=1, stroke=0)

    # crest
    sx, sy = LM + 4, top - 70
    c.setFillColor(MAROON); c.rect(sx, sy, 56, 58, fill=1, stroke=0)
    p = c.beginPath(); p.moveTo(sx, sy); p.lineTo(sx + 28, sy - 16); p.lineTo(sx + 56, sy)
    c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff")); c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(sx + 28, sy + 46, "1865")
    c.circle(sx + 28, sy + 26, 11, fill=1, stroke=0)

    c.setFillColor(MAROON); c.setFont("Times-Bold", 34)
    c.drawString(sx + 70, sy + 26, "RIDER")
    c.setFillColor(HexColor("#4a4a4a")); c.setFont("Times-Roman", 15)
    c.drawString(sx + 72, sy + 8, "U N I V E R S I T Y")

    # tabs
    ty = sy - 20
    c.setFillColor(MAROON); c.rect(LM, ty, 60, 15, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff")); c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(LM + 30, ty + 4, "Student")
    c.setFillColor(HexColor("#303030")); c.rect(LM + 62, ty, 80, 15, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.drawCentredString(LM + 102, ty + 4, "Financial Aid")

    # nav links
    c.setFillColor(LINKBLUE); c.setFont("Helvetica-Bold", 8)
    c.drawRightString(RM, ty + 30, "RETURN TO MENU   SITE MAP   HELP   EXIT")

    # title + id block
    ly = ty - 26
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold", 17)
    c.drawString(LM, ly, META["title"])
    c.setFillColor(LINKBLUE); c.setFont("Helvetica-Bold", 8)
    c.drawRightString(RM, ly + 8, META["student_id"] + "  " + META["student_top"])
    c.setFillColor(HexColor("#333333")); c.setFont("Helvetica", 8)
    c.drawRightString(RM, ly - 2, META["term"])
    c.drawRightString(RM, ly - 12, META["stamp"])

    c.setFillColor(MAROON); c.rect(LM, ly - 20, RM - LM, 2.5, fill=1, stroke=0)

    # intro
    iy = ly - 36
    c.setFillColor(MAROON); c.circle(LM + 5, iy + 2, 5, fill=1, stroke=0)
    c.setFillColor(HexColor("#333333")); c.setFont("Helvetica", 8)
    c.drawString(LM + 16, iy, META["intro"])
    c.setFillColor(LINKBLUE); c.setFont("Helvetica-Bold", 9)
    c.drawString(LM + 16, iy - 18, META["textbooks"])

    # student info grid
    gy = iy - 40
    line_h = 11
    row = gy
    for label, val in STUDENT:
        nlab = max(label.count("\n"), val.count("\n")) + 1
        c.setFillColor(HEADGRY)
        c.rect(LM, row - (nlab-1)*line_h - 2, 120, nlab*line_h, fill=1, stroke=0)
        draw_lines(c, LM + 2, row, label, "Helvetica-Bold", 8, BLACK, line_h)
        draw_lines(c, LM + 125, row, val, "Helvetica", 8, BLACK, line_h)
        row -= nlab * line_h + 2

    # address box
    ax = 425
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold", 8)
    c.drawString(ax, gy, "Address:")
    c.setFont("Helvetica", 8)
    c.drawString(ax + 42, gy, ADDRESS[0])
    for i, ln in enumerate(ADDRESS[1:], 1):
        c.drawString(ax + 42, gy - i * line_h, ln)

    # registration table
    ty0 = row - 14
    c.setFillColor(HEADGRY); c.rect(LM, ty0 - 18, RM - LM, 26, fill=1, stroke=0)
    for col in COL_ORDER:
        draw_lines(c, COLX[col], ty0, COL_LABEL[col], "Helvetica-Bold", 7.5, TABHEAD, 9)
    c.setStrokeColor(GREY_BAR); c.setLineWidth(0.6)
    c.line(LM, ty0 - 20, RM, ty0 - 20)

    cy = ty0 - 30
    shade = False
    for course in COURSES:
        for r in course:
            rowdata = dict(zip(COL_ORDER, r))
            nl = max(str(v).count("\n") for v in r) + 1
            block_h = nl * 10
            if shade:
                c.setFillColor(LIGHTROW)
                c.rect(LM, cy - block_h + 6, RM - LM, block_h, fill=1, stroke=0)
            for col in COL_ORDER:
                val = rowdata[col]
                if val == "":
                    continue
                color = LINKBLUE if col == "course" else BLACK
                draw_lines(c, COLX[col], cy, val, "Helvetica", 7.3, color, 10)
            cy -= block_h + 4
        shade = not shade

    cy -= 4
    c.setFillColor(BLACK); c.setFont("Helvetica-Bold", 8)
    c.drawString(COLX["campus"], cy, "Total")
    c.drawString(COLX["campus"], cy - 10, "Credits:")
    c.setFont("Helvetica", 8)
    c.drawString(COLX["credits"], cy, TOTAL_CREDITS)

    c.setStrokeColor(GREY_BAR); c.setLineWidth(1)
    c.line(LM, cy - 24, RM, cy - 24)
    c.setFillColor(LINKBLUE); c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W/2, cy - 46, "[ Student Detail Schedule ]")

    c.showPage()
    c.save()
    print("wrote", path)


if __name__ == "__main__":
    build()
