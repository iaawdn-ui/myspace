from pathlib import Path
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'AI_ROBOTICS_BACHELOR_VIDEO_SERIES_PROMPTS.md').read_text()
items=[]
for m in re.finditer(r'^#### (AI\.\d+) — (.+)$', source, re.M):
    start=m.end(); nxt=re.search(r'^#### AI\.', source[start:], re.M)
    text=source[start:start+nxt.start() if nxt else len(source)-start].strip()
    text=re.sub(r'\*\*','',text)
    items.append((m.group(1),m.group(2),text))

navy=colors.HexColor('#17283F'); ink=colors.HexColor('#243246'); gold=colors.HexColor('#B28A4A'); ivory=colors.HexColor('#F7F4EC'); muted=colors.HexColor('#687486'); teal=colors.HexColor('#416A70')
path=ROOT/'AI_Robotics_Presentation_Design_Atlas.pdf'
doc=SimpleDocTemplate(str(path),pagesize=landscape(A4),rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=17*mm,title='AI & Robotics Presentation Design Atlas',author='Myspace — Academic Presentation Design')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverTitle',parent=styles['Title'],fontName='Times-Bold',fontSize=30,leading=36,textColor=ivory,alignment=TA_LEFT,spaceAfter=9*mm))
styles.add(ParagraphStyle(name='CoverSub',parent=styles['Normal'],fontName='Times-Roman',fontSize=15,leading=22,textColor=colors.HexColor('#D8D5CC')))
styles.add(ParagraphStyle(name='CourseTitle',parent=styles['Heading1'],fontName='Times-Bold',fontSize=22,leading=27,textColor=navy,spaceAfter=2*mm))
styles.add(ParagraphStyle(name='Kicker',parent=styles['Normal'],fontName='Helvetica-Bold',fontSize=8,leading=10,textColor=gold,spaceAfter=2*mm))
styles.add(ParagraphStyle(name='BodyClassic',parent=styles['BodyText'],fontName='Helvetica',fontSize=9.2,leading=13,textColor=ink,spaceAfter=2*mm))
styles.add(ParagraphStyle(name='Label',parent=styles['Normal'],fontName='Helvetica-Bold',fontSize=8,leading=10,textColor=teal,spaceAfter=1.3*mm))
styles.add(ParagraphStyle(name='Small',parent=styles['BodyText'],fontName='Helvetica',fontSize=8,leading=11,textColor=muted))
styles.add(ParagraphStyle(name='SectionHead',parent=styles['Heading2'],fontName='Times-Bold',fontSize=15,leading=18,textColor=navy,spaceBefore=4*mm,spaceAfter=2*mm))

def frame(canvas,doc):
    canvas.saveState(); w,h=landscape(A4)
    if doc.page>1:
        canvas.setFillColor(ivory); canvas.rect(0,0,w,h,fill=1,stroke=0)
        canvas.setStrokeColor(gold); canvas.setLineWidth(.7); canvas.line(18*mm,h-12*mm,w-18*mm,h-12*mm)
        canvas.setFont('Helvetica-Bold',7); canvas.setFillColor(muted); canvas.drawString(18*mm,h-9*mm,'AI & ROBOTICS ENGINEERING  /  PRESENTATION DESIGN ATLAS')
        canvas.setFont('Helvetica',8); canvas.drawRightString(w-18*mm,9*mm,f'{doc.page-1:02d}  •  COURSE DESIGN SHEET')
    canvas.restoreState()

story=[]
# Cover
story += [Spacer(1,25*mm), Paragraph('AI & ROBOTICS<br/>ENGINEERING',ParagraphStyle('cover1',fontName='Times-Bold',fontSize=34,leading=39,textColor=ivory)),Spacer(1,7*mm),Paragraph('PRESENTATION DESIGN ATLAS',ParagraphStyle('cover2',fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=gold)),Spacer(1,6*mm),Paragraph('A classic visual system and course-by-course slide blueprint<br/>for all 48 undergraduate lecture series',styles['CoverSub']),Spacer(1,20*mm)]
cover=Table([[Paragraph('<b>DESIGN INTENT</b><br/><br/>A timeless academic character—deep ink blue, warm ivory, restrained brass, confident serif headlines and precise engineering diagrams. Every course receives its own visual emphasis while remaining part of one coherent degree programme.',ParagraphStyle('coverbox',fontName='Helvetica',fontSize=11,leading=16,textColor=ivory))]],colWidths=[240*mm],rowHeights=[39*mm])
cover.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),navy),('BOX',(0,0),(-1,-1),1,gold),('LEFTPADDING',(0,0),(-1,-1),12*mm),('RIGHTPADDING',(0,0),(-1,-1),12*mm),('TOPPADDING',(0,0),(-1,-1),7*mm)]))
story += [cover,Spacer(1,13*mm),Paragraph('720p • 16:9 • lecture-first • practical by design',ParagraphStyle('tag',fontName='Helvetica',fontSize=10,textColor=ivory)),PageBreak()]
# visual system page
story += [Paragraph('01  /  THE CLASSIC DESIGN SYSTEM',styles['Kicker']),Paragraph('One university identity. Forty-eight distinct course experiences.',styles['SectionHead']),Paragraph('The visual language should feel enduring rather than trendy: scholarly typography and generous whitespace paired with technically exact, modern imagery. The course title and section hierarchy stay consistent; accent imagery, diagrams and data colors adapt to the discipline.',styles['BodyClassic'])]
rows=[[Paragraph('<b>ELEMENT</b>',styles['Small']),Paragraph('<b>SPECIFICATION</b>',styles['Small'])],
[Paragraph('Palette',styles['BodyClassic']),Paragraph('Midnight navy #17283F; warm ivory #F7F4EC; antique brass #B28A4A; slate ink #243246; muted teal #416A70. Use red only for hazards/errors and green only for validated states.',styles['BodyClassic'])],
[Paragraph('Typography',styles['BodyClassic']),Paragraph('Titles: stately serif (Times/Source Serif style). Body, labels, code and measurements: highly legible sans serif. Equations use a clear math font. Keep body text large enough for projection.',styles['BodyClassic'])],
[Paragraph('Composition',styles['BodyClassic']),Paragraph('16:9 canvas; clear title band; one principal idea per slide; 60/40 visual-to-text balance; consistent margins, page numbers and section markers. Avoid dense paragraphs and ornamental clutter.',styles['BodyClassic'])],
[Paragraph('Diagram language',styles['BodyClassic']),Paragraph('Thin navy strokes, brass highlights for the active path, teal for inputs/feedback, restrained labels, explicit units and a visible legend. Animate in teachable steps; include static fallback frames.',styles['BodyClassic'])],
[Paragraph('Photography & renders',styles['BodyClassic']),Paragraph('Use authentic laboratories, hardware and industrial contexts. Prefer editorial documentary framing and realistic 3D renders; label illustrative renderings and avoid misleading stock imagery.',styles['BodyClassic'])],
[Paragraph('Accessibility',styles['BodyClassic']),Paragraph('High contrast, captions, concise alt descriptions, color-independent distinctions, readable equations and code, deliberate pacing, and no information conveyed by color alone.',styles['BodyClassic'])]]
t=Table(rows,colWidths=[42*mm,218*mm],repeatRows=1); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),navy),('TEXTCOLOR',(0,0),(-1,0),ivory),('BACKGROUND',(0,1),(-1,-1),colors.white),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F0EDE4')]),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#D5D0C4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),4*mm),('RIGHTPADDING',(0,0),(-1,-1),4*mm),('TOPPADDING',(0,0),(-1,-1),2.4*mm),('BOTTOMPADDING',(0,0),(-1,-1),2.4*mm)])); story += [t,Spacer(1,5*mm),Paragraph('<b>Reusable lecture rhythm:</b> Opening question → objectives → intuition → formal model → animated diagram → worked example → demonstration → lab challenge → application/case study → knowledge check → summary and next-step preview.',styles['BodyClassic']),PageBreak()]

# course sheets
for idx,(code,title,desc) in enumerate(items,1):
    # Pick an art direction matched to content, deterministic and useful.
    lower=(title+' '+desc).lower()
    if any(x in lower for x in ['ethic','social','human-robot','interaction']): art='Human-centered editorial photography; warm ivory canvas, trust/safety callouts, stakeholder maps and scenario decision trees.'
    elif any(x in lower for x in ['vision','perception','image','graphics']): art='Dark navy image-analysis canvas with annotated real imagery, crisp bounding boxes, calibration overlays, color-space comparisons and progressive pipeline reveals.'
    elif any(x in lower for x in ['control','signal','fuzzy']): art='Instrument-panel precision: ivory technical sheets, navy block diagrams, brass signal traces, plotted response curves and clearly labeled axes/units.'
    elif any(x in lower for x in ['robot','mobile','navigation','kinematic','manipulation','path','swarm','simulation','design']): art='Mechanical editorial: realistic robot/lab hero imagery, exploded views, coordinate frames, motion trails and brass-highlighted components.'
    elif any(x in lower for x in ['machine learning','neural','deep learning','reinforcement','pattern','artificial intelligence','natural language']): art='Data-science lecture aesthetic: clean plots, model pipeline diagrams, dark code panels, annotated datasets and carefully distinguished training/test evidence.'
    elif any(x in lower for x in ['embedded','internet of things','computer architecture','cyber-physical']): art='Systems-engineering blueprint: device photography, layered architecture, buses/protocols, timing diagrams and hardware-to-cloud flow.'
    else: art='Scholarly technical plate: spacious ivory layout, navy structure, brass emphasis, precise diagrams, real-world engineering photography and restrained data graphics.'
    story += [Paragraph(f'{idx+1:02d}  /  {code}  •  PRESENTATION DESIGN',styles['Kicker']),Paragraph(f'{code} — {title}',styles['CourseTitle'])]
    story += [Paragraph('<b>Course visual direction</b>',styles['Label']),Paragraph(art,styles['BodyClassic'])]
    # Summarized course scope from original prompt.
    plain=re.sub(r'\s+',' ',desc)
    if len(plain)>700: plain=plain[:697].rsplit(' ',1)[0]+'…'
    story += [Paragraph('<b>Content anchor</b>',styles['Label']),Paragraph(plain,styles['BodyClassic'])]
    table_data=[[Paragraph('<b>SLIDE / VISUAL SEQUENCE</b>',styles['Small']),Paragraph('<b>DESIGN TREATMENT</b>',styles['Small'])],
    [Paragraph('01 · Opening / motivating problem',styles['BodyClassic']),Paragraph('Full-bleed but restrained real-world image or system render; serif course title, course code, one compelling question.',styles['BodyClassic'])],
    [Paragraph('02 · Learning map / objectives',styles['BodyClassic']),Paragraph('Three to five outcomes, staged as a clear route through the module; establish prerequisite links and vocabulary.',styles['BodyClassic'])],
    [Paragraph('03 · Core concept / model',styles['BodyClassic']),Paragraph('One idea per frame; reveal diagram in logical order, define symbols on first use, connect intuition to formal notation.',styles['BodyClassic'])],
    [Paragraph('04 · Worked example / visualization',styles['BodyClassic']),Paragraph('Show inputs, intermediate steps and result; annotate decisions, units, assumptions and common failure cases.',styles['BodyClassic'])],
    [Paragraph('05 · Demonstration / lab',styles['BodyClassic']),Paragraph('Split-screen workflow: equipment or software context beside focused steps; show expected output and troubleshooting cues.',styles['BodyClassic'])],
    [Paragraph('06 · Application / assessment',styles['BodyClassic']),Paragraph('Case-study image or scenario, constraints and trade-offs; end with a knowledge check, practical task and summary.',styles['BodyClassic'])]]
    tb=Table(table_data,colWidths=[76*mm,184*mm],repeatRows=1); tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),navy),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F0EDE4')]),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#D5D0C4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),3*mm),('RIGHTPADDING',(0,0),(-1,-1),3*mm),('TOPPADDING',(0,0),(-1,-1),1.6*mm),('BOTTOMPADDING',(0,0),(-1,-1),1.6*mm)]))
    story += [tb,Spacer(1,3*mm),Paragraph('<b>Signature asset:</b> A single technically accurate hero diagram or system view used on the course opener, then unpacked and revisited in later modules. <b>Delivery:</b> 720p, 16:9; captions and static diagram alternatives included.',styles['Small'])]
    if idx<len(items): story.append(PageBreak())

doc.build(story,onFirstPage=lambda c,d: (c.saveState(),c.setFillColor(navy),c.rect(0,0,landscape(A4)[0],landscape(A4)[1],fill=1,stroke=0),c.setStrokeColor(gold),c.setLineWidth(1.5),c.line(18*mm,18*mm,landscape(A4)[0]-18*mm,18*mm),c.restoreState()),onLaterPages=frame)
print(f'Created {path} with {len(items)} course design sheets.')
