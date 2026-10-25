"""Generate an individual, slide-per-page 16:9 course PDF for each course except AI.101."""
from pathlib import Path
import re
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT=Path(__file__).resolve().parents[1]
TEXT=(ROOT/'AI_ROBOTICS_BACHELOR_VIDEO_SERIES_PROMPTS.md').read_text()
OUT=ROOT/'course_slide_decks'; OUT.mkdir(exist_ok=True)
W,H=1280,720
NAVY=HexColor('#17283F'); IVORY=HexColor('#F7F4EC'); GOLD=HexColor('#B28A4A'); TEAL=HexColor('#416A70'); INK=HexColor('#243246'); MUTED=HexColor('#687486'); WHITE=white

def wrap(text,font,size,maxw):
    words=text.split(); lines=[]; line=''
    for word in words:
        candidate=(line+' '+word).strip()
        if stringWidth(candidate,font,size)<=maxw: line=candidate
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    return lines

def get_courses():
    matches=list(re.finditer(r'^#### (AI\.\d+) — (.+)$',TEXT,re.M)); result=[]
    for i,m in enumerate(matches):
        start=m.end(); end=matches[i+1].start() if i+1<len(matches) else TEXT.find('\n## Recommended structure',start)
        body=re.sub(r'\*\*','',TEXT[start:end if end!=-1 else len(TEXT)]).strip()
        result.append((m.group(1),m.group(2),body))
    return result

def split_topics(body):
    body=re.sub(r'\*\*[^*]+\*\*:?','',body)
    # Convert prose lists into digestible visual topic labels, excluding practical directive boilerplate.
    body=re.sub(r'\*\*Mandatory practicals?\*\*:?','',body,flags=re.I)
    bits=re.split(r';|,|\.(?:\s+|$)|\n|\u2022',body)
    cleaned=[]
    for b in bits:
        b=re.sub(r'\s+',' ',b).strip(' .:-—')
        b=re.sub(r'^(Teach|Cover|Include|Use|Explain|Focus on|The course must guide|Students must|Conclude with|End with)\s+','',b,flags=re.I)
        if len(b)>3 and len(b)<120 and b.lower() not in ('mandatory practical','mandatory practicals'):
            cleaned.append(b[0].upper()+b[1:])
    unique=[]
    for b in cleaned:
        if b not in unique: unique.append(b)
    return unique[:16] or ['Foundations','Core methods','Practical implementation','Evaluation and applications']

def page_base(c,idx,total,section,dark=False):
    c.setFillColor(NAVY if dark else IVORY); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(GOLD); c.rect(62,H-61,44,4,fill=1,stroke=0)
    c.setFont('Helvetica-Bold',12); c.setFillColor(GOLD); c.drawString(120,H-64,section.upper())
    c.setStrokeColor(GOLD); c.setLineWidth(.8); c.line(62,39,W-62,39)
    c.setFont('Helvetica',10); c.setFillColor(HexColor('#C6C3BA') if dark else MUTED); c.drawString(62,20,'AI & ROBOTICS ENGINEERING  •  COURSE LECTURE')
    c.drawRightString(W-62,20,f'{idx:02d} / {total:02d}')

def heading(c,text,sub=None,dark=False):
    c.setFillColor(IVORY if dark else NAVY); c.setFont('Times-Bold',38)
    lines=wrap(text,'Times-Bold',38,1135)
    for i,line in enumerate(lines[:2]): c.drawString(65, H-138-i*46,line)
    if sub:
        c.setFont('Helvetica',17); c.setFillColor(HexColor('#D8D5CC') if dark else MUTED); c.drawString(68,H-188-(len(lines[:2])-1)*46,sub[:130])

def bullets(c,items,x,y,width,size=21,leading=32,color=INK):
    for item in items:
        c.setFillColor(GOLD); c.circle(x,y+5,4.5,fill=1,stroke=0)
        ls=wrap(item,'Helvetica',size,width-28)
        c.setFillColor(color); c.setFont('Helvetica',size)
        for j,line in enumerate(ls[:3]): c.drawString(x+18,y-j*leading,line)
        y-=len(ls[:3])*leading+17

def card(c,x,y,w,h,title,body,accent=GOLD,dark=False):
    c.setFillColor(HexColor('#223750') if dark else WHITE); c.roundRect(x,y,w,h,12,fill=1,stroke=0)
    c.setFillColor(accent); c.rect(x,y+h-6,w,6,fill=1,stroke=0)
    c.setFillColor(IVORY if dark else NAVY); c.setFont('Times-Bold',19); c.drawString(x+17,y+h-37,title[:38])
    c.setFont('Helvetica',14); c.setFillColor(HexColor('#D8D5CC') if dark else INK)
    lines=wrap(body,'Helvetica',14,w-34)
    for j,l in enumerate(lines[:4]): c.drawString(x+17,y+h-64-j*20,l)

def build(code,name,body):
    topics=split_topics(body); shorttopics=topics[:12]
    filename=re.sub(r'[^A-Za-z0-9]+','_',f'{code}_{name}').strip('_')+'.pdf'
    c=canvas.Canvas(str(OUT/filename),pagesize=(W,H),pageCompression=1); total=10
    c.setTitle(f'{code} — {name} | Lecture slides')
    # 1 cover
    page_base(c,1,total,'COURSE OPENING',True)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold',14); c.drawString(70,548,'BACHELOR OF ARTIFICIAL INTELLIGENCE & ROBOTICS ENGINEERING')
    c.setFillColor(IVORY); c.setFont('Times-Bold',54)
    name_lines=wrap(name,'Times-Bold',54,770)
    for i,l in enumerate(name_lines[:2]): c.drawString(67,445-i*64,l)
    c.setFont('Helvetica',24); c.setFillColor(HexColor('#D8D5CC')); c.drawString(73,302,code+'  |  University lecture series')
    # decorative system motif
    center=(1000,355); c.setStrokeColor(GOLD); c.setLineWidth(2)
    points=[(900,455,'INPUT'),(1095,455,'MODEL'),(1095,250,'OUTPUT'),(900,250,'EVIDENCE')]
    for x,y,l in points:
        c.setFillColor(HexColor('#223750'));c.circle(x,y,46,fill=1,stroke=1);c.setFillColor(IVORY);c.setFont('Helvetica-Bold',11);c.drawCentredString(x,y-4,l)
    c.line(936,455,1059,455);c.line(1095,409,1095,296);c.line(1049,250,946,250);c.line(900,296,900,409)
    c.showPage()
    # 2 objectives
    page_base(c,2,total,'01 / LEARNING OBJECTIVES'); heading(c,'What you will learn','A practical progression from core ideas to engineering judgment')
    obj=[f'Explain and define {shorttopics[0].lower()}.',f'Apply key methods including {shorttopics[min(1,len(shorttopics)-1)].lower()}.',f'Build or analyze a practical system involving {shorttopics[min(2,len(shorttopics)-1)].lower()}.','Evaluate assumptions, limitations, performance and responsible use.']
    bullets(c,obj,82,475,1050)
    c.showPage()
    # 3 roadmap
    page_base(c,3,total,'02 / COURSE ROADMAP'); heading(c,'A connected learning journey','Each stage prepares the tools needed for the next.')
    stages=[('01','FOUNDATIONS',shorttopics[0]),('02','METHODS',shorttopics[min(1,len(shorttopics)-1)]),('03','SYSTEMS',shorttopics[min(2,len(shorttopics)-1)]),('04','PRACTICE','Laboratory, evaluation and project')]
    for i,(n,h,b) in enumerate(stages):
        x=68+i*296; card(c,x,250,260,180,h,b,GOLD if i%2==0 else TEAL)
        c.setFillColor(GOLD);c.setFont('Times-Bold',30);c.drawString(x+17,455,n)
        if i<3: c.setStrokeColor(GOLD);c.setLineWidth(2);c.line(x+260,340,x+289,340)
    c.showPage()
    # 4 topic map
    page_base(c,4,total,'03 / CONCEPT MAP'); heading(c,'The subject at a glance','A map of the ideas and techniques in this course')
    for i,t in enumerate(shorttopics[:8]):
        col=i%4; row=i//4; x=68+col*296; y=355-row*205
        card(c,x,y,262,145,f'{i+1:02d} · {t[:30]}',t,GOLD if i%2==0 else TEAL)
    c.showPage()
    # 5-6 two theory pages
    for p,group in [(5,shorttopics[:5]),(6,shorttopics[5:10] or shorttopics[:5])]:
        page_base(c,p,total,'04 / CORE THEORY'); heading(c,'Core ideas, made explicit',f'{code}  •  Distinguish definitions, assumptions and evidence')
        bullets(c,group,78,474,1080,20,31)
        c.setFillColor(TEAL);c.roundRect(760,120,420,64,12,fill=1,stroke=0);c.setFillColor(WHITE);c.setFont('Helvetica-Bold',14);c.drawCentredString(970,145,'DEFINE  →  MODEL  →  TEST  →  INTERPRET')
        c.showPage()
    # 7 visual framework
    page_base(c,7,total,'05 / VISUAL MODEL'); heading(c,'Follow the system through its stages','Use the process diagram to connect components and outcomes.')
    labels=['PROBLEM','INPUTS','METHOD','OUTPUT','EVALUATION']
    desc=[shorttopics[0],shorttopics[min(1,len(shorttopics)-1)],shorttopics[min(2,len(shorttopics)-1)],shorttopics[min(3,len(shorttopics)-1)],'Evidence, constraints and limitations']
    for i,(h,b) in enumerate(zip(labels,desc)):
        x=58+i*244; card(c,x,285,214,165,h,b,GOLD if i in (0,4) else TEAL)
        if i<4:
            c.setStrokeColor(GOLD);c.setLineWidth(3);c.line(x+214,365,x+237,365)
    c.setFillColor(MUTED);c.setFont('Helvetica',16);c.drawString(80,190,'Teaching sequence: reveal one component at a time; then replay the complete end-to-end flow.')
    c.showPage()
    # 8 application
    page_base(c,8,total,'06 / ENGINEERING APPLICATION'); heading(c,'From concept to a real engineering decision','A short case study for discussion and worked-example narration')
    card(c,76,348,330,180,'SCENARIO','A real task involving '+shorttopics[0].lower()+'.',GOLD)
    card(c,475,348,330,180,'CONSTRAINTS','Data, resources, safety and operating conditions shape the design.',TEAL)
    card(c,874,348,330,180,'DECISION','Select a method; justify the trade-offs and define success.',GOLD)
    bullets(c,['State assumptions before calculating or implementing.','Compare the expected result with observed evidence.'],100,260,1000,19,30)
    c.showPage()
    # 9 lab
    page_base(c,9,total,'07 / PRACTICAL LABORATORY',True); heading(c,'Laboratory · build, measure, improve','Students work through the following guided sequence.',True)
    lab=[f'Specify a measurable task using {shorttopics[0].lower()}.',f'Implement or simulate a baseline using {shorttopics[min(1,len(shorttopics)-1)].lower()}.','Run a controlled test and record results with units and conditions.','Diagnose a failure, revise the design and explain the improvement.']
    bullets(c,lab,82,475,1060,21,36,IVORY)
    c.showPage()
    # 10 review
    page_base(c,10,total,'08 / CHECKPOINT & NEXT STEPS'); heading(c,'Review · explain · apply')
    card(c,76,310,510,190,'KNOWLEDGE CHECK','What assumptions does the method make? What evidence would show that it works?',GOLD)
    card(c,694,310,510,190,'PRACTICAL CHALLENGE','Apply one course idea to a new context; state constraints, test criteria and likely failure modes.',TEAL)
    c.setFillColor(NAVY);c.setFont('Times-Bold',25);c.drawCentredString(640,190,'Key takeaway: make the model visible, test it, and communicate its limits.')
    c.setFillColor(MUTED);c.setFont('Helvetica',14);c.drawCentredString(640,130,'Course-series slide design • detailed narration, demonstrations and assessments expand each module.')
    c.showPage();c.save()

courses=get_courses()
for code,name,body in courses:
    if code=='AI.101': continue
    build(code,name,body)
print(f'Generated {len(courses)-1} individual subject slide PDFs in {OUT}')
