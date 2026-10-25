from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]/'AI101_Introduction_to_Artificial_Intelligence_Slides.pdf'
W,H=1280,720
NAVY=HexColor('#17283F'); IVORY=HexColor('#F7F4EC'); GOLD=HexColor('#B28A4A'); TEAL=HexColor('#416A70'); INK=HexColor('#243246'); MUTED=HexColor('#687486'); PALE=HexColor('#E9E4D8'); WHITE=white
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('AI.101 — Introduction to Artificial Intelligence | Lecture Slides')
c.setAuthor('Myspace — Academic Presentation Design')

def wrap(text,font,size,maxw):
    words=text.split(); lines=[]; line=''
    for word in words:
        test=(line+' '+word).strip()
        if stringWidth(test,font,size)<=maxw: line=test
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    return lines

def base(section,num,dark=False):
    bg=NAVY if dark else IVORY; fg=IVORY if dark else INK
    c.setFillColor(bg); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(GOLD); c.rect(68,H-62,44,4,fill=1,stroke=0)
    c.setFont('Helvetica-Bold',13); c.setFillColor(GOLD); c.drawString(126,H-66,section.upper())
    c.setStrokeColor(GOLD); c.setLineWidth(1); c.line(68,38,W-68,38)
    c.setFont('Helvetica',11); c.setFillColor(MUTED if not dark else HexColor('#C6C3BA')); c.drawString(68,19,'AI.101  •  INTRODUCTION TO ARTIFICIAL INTELLIGENCE')
    c.drawRightString(W-68,19,f'{num:02d}  /  12')
    return fg

def title(txt,sub=None,dark=False):
    fg=IVORY if dark else NAVY
    c.setFillColor(fg); c.setFont('Times-Bold',42); c.drawString(68,H-139,txt)
    if sub:
        c.setFont('Helvetica',18); c.setFillColor(HexColor('#D8D5CC') if dark else MUTED); c.drawString(70,H-174,sub)

def bullet_list(items,x,y,width,size=22,color=INK,leading=37):
    for it in items:
        c.setFillColor(GOLD); c.circle(x,y+6,5,fill=1,stroke=0)
        lines=wrap(it,'Helvetica',size,width-28)
        c.setFillColor(color); c.setFont('Helvetica',size)
        for j,line in enumerate(lines): c.drawString(x+20,y-j*leading,line)
        y-=len(lines)*leading+19

def box(x,y,w,h,head,body,accent=GOLD,dark=False):
    c.setFillColor(HexColor('#223750') if dark else WHITE); c.roundRect(x,y,w,h,13,fill=1,stroke=0)
    c.setFillColor(accent); c.rect(x,y+h-7,w,7,fill=1,stroke=0)
    c.setFillColor(IVORY if dark else NAVY); c.setFont('Times-Bold',22); c.drawString(x+22,y+h-43,head)
    lines=wrap(body,'Helvetica',16,w-44); c.setFillColor(HexColor('#D8D5CC') if dark else INK); c.setFont('Helvetica',16)
    for i,line in enumerate(lines[:5]): c.drawString(x+22,y+h-76-i*23,line)

def pill(x,y,label):
    w=stringWidth(label,'Helvetica-Bold',14)+28
    c.setFillColor(NAVY); c.roundRect(x,y,w,32,16,fill=1,stroke=0)
    c.setFillColor(IVORY); c.setFont('Helvetica-Bold',14); c.drawCentredString(x+w/2,y+10,label)

# 1 cover
base('course opening',1,True)
c.setFillColor(GOLD); c.setFont('Helvetica-Bold',15); c.drawString(76,550,'BACHELOR OF ARTIFICIAL INTELLIGENCE & ROBOTICS ENGINEERING')
c.setFillColor(IVORY); c.setFont('Times-Bold',60); c.drawString(72,450,'Introduction to')
c.drawString(72,380,'Artificial Intelligence')
c.setFont('Helvetica',22); c.setFillColor(HexColor('#D8D5CC')); c.drawString(78,320,'AI.101  |  Foundations, ideas and intelligent systems')
# decorative agent diagram
c.setStrokeColor(GOLD); c.setLineWidth(2)
for (x,y,r,label) in [(935,475,58,'SENSE'),(1090,355,62,'REASON'),(920,230,55,'ACT')]:
    c.setFillColor(HexColor('#223750')); c.circle(x,y,r,fill=1,stroke=1); c.setFillColor(IVORY); c.setFont('Helvetica-Bold',15); c.drawCentredString(x,y-5,label)
c.line(980,440,1048,392); c.line(1052,301,970,267); c.line(883,278,902,421)
c.showPage()
# 2 question
base('01 / orientation',2); title('What makes a system intelligent?','Begin with behavior, not the label.')
box(70,130,520,300,'A useful starting point','An intelligent system perceives its environment, selects actions and adapts its behavior to achieve goals.',GOLD)
# agent loop diagram
nodes=[(760,390,'ENVIRONMENT'),(1015,390,'AGENT'),(1015,190,'ACTION'),(760,190,'PERCEPT')]
for x,y,l in nodes:
 c.setFillColor(WHITE); c.roundRect(x-92,y-35,184,70,14,fill=1,stroke=0); c.setFillColor(NAVY); c.setFont('Helvetica-Bold',16); c.drawCentredString(x,y-5,l)
c.setStrokeColor(TEAL); c.setLineWidth(4); c.line(852,390,918,390); c.line(1015,355,1015,227); c.line(923,190,852,190); c.line(760,225,760,355)
c.setFont('Helvetica',14); c.setFillColor(MUTED); c.drawString(860,408,'percept'); c.drawString(1027,286,'decision'); c.drawString(855,205,'effect'); c.drawString(770,286,'feedback')
c.showPage()
# 3 objectives
base('01 / orientation',3); title('By the end of this course, you can…')
bullet_list(['Explain major traditions in AI and how they complement one another.','Formulate an agent, search or reasoning problem with explicit assumptions.','Compare learning approaches using evidence, limitations and engineering trade-offs.','Build and evaluate a small intelligent system, then communicate its behavior responsibly.'],85,490,1040,24)
c.showPage()
# 4 timeline/history
base('02 / origins',4); title('AI is a field with several intellectual lineages','Ideas evolve; they do not simply replace one another.')
xs=[120,380,640,900,1140]; labels=['LOGIC &\nSYMBOLS','SEARCH &\nPLANNING','STATISTICAL\nLEARNING','DEEP\nLEARNING','GENERATIVE &\nHYBRID AI']
y=345;c.setStrokeColor(GOLD);c.setLineWidth(5);c.line(xs[0],y,xs[-1],y)
for i,(x,l) in enumerate(zip(xs,labels)):
 c.setFillColor(NAVY if i%2==0 else TEAL);c.circle(x,y,19,fill=1,stroke=0)
 c.setFillColor(NAVY);c.setFont('Helvetica-Bold',15)
 for j,line in enumerate(l.split('\n')):c.drawCentredString(x,y-65-j*20,line)
c.setFillColor(MUTED);c.setFont('Helvetica',16);c.drawString(95,135,'Through-line: represent a problem → reason or learn → act → evaluate the result.')
c.showPage()
# 5 paradigms
base('03 / ways of thinking',5); title('Four traditions. Different strengths.')
box(68,148,265,310,'Symbolic','Explicit rules, logic and structured knowledge. Strong when explanations and constraints matter.')
box(367,148,265,310,'Statistical','Models infer patterns from data. Strong when uncertainty and variation are central.',TEAL)
box(666,148,265,310,'Connectionist','Neural networks learn distributed representations. Powerful for perception and language.',GOLD)
box(965,148,245,310,'Hybrid','Combine learned components with rules, search or structured models.',TEAL)
c.showPage()
# 6 agent
base('04 / intelligent agents',6); title('Agent design begins with the task environment')
bullet_list(['Performance measure: what counts as success?','Environment: what can change, and what is hidden?','Actuators: what actions are available?','Sensors: what observations can the system receive?'],75,480,500,20)
box(690,272,485,190,'Example · delivery robot','Success balances safe arrival, time, energy and accessibility—not just shortest distance.',TEAL)
pill(720,180,'GOAL'); pill(830,180,'SENSORS'); pill(960,180,'ACTIONS'); pill(1080,180,'FEEDBACK')
c.showPage()
# 7 search
base('05 / problem solving',7); title('Search turns choices into a structured space','A search algorithm explores possible states toward a goal.')
# tree
levels=[[(640,490,'Start')],[(430,360,'A'),(850,360,'B')],[(300,225,'C'),(515,225,'D'),(765,225,'E'),(980,225,'Goal')]]
for lev in range(2):
 for i,(x,y,l) in enumerate(levels[lev]):
  children=levels[lev+1][i*2:i*2+2]
  for xx,yy,ll in children: c.setStrokeColor(MUTED);c.setLineWidth(2);c.line(x,y-20,xx,yy+20)
for level in levels:
 for x,y,l in level:
  c.setFillColor(GOLD if l=='Goal' else NAVY);c.circle(x,y,29,fill=1,stroke=0);c.setFillColor(WHITE);c.setFont('Helvetica-Bold',15);c.drawCentredString(x,y-5,l)
c.setFillColor(INK);c.setFont('Helvetica',17);c.drawString(95,110,'Breadth-first search: expand by depth.  A* search: combine path cost with an estimate to goal.')
c.showPage()
# 8 knowledge/reasoning
base('06 / knowledge & reasoning',8); title('Representations determine what can be reasoned about')
box(75,170,330,280,'Facts','Store observations or asserted truths with provenance and confidence.',GOLD)
box(475,170,330,280,'Rules','Encode relationships and conditions; trace how conclusions follow.',TEAL)
box(875,170,330,280,'Uncertainty','Represent incomplete evidence; update beliefs rather than pretending certainty.',GOLD)
c.setFillColor(NAVY);c.setFont('Times-Bold',24);c.drawCentredString(640,105,'Representation  →  inference  →  decision')
c.showPage()
# 9 machine learning
base('07 / learning from data',9); title('Learning is an evidence pipeline—not a magic box')
steps=[('DATA','examples'),('FEATURES','useful signal'),('MODEL','fit parameters'),('TEST','unseen cases'),('DEPLOY','monitor drift')]
x=75
for i,(h,b) in enumerate(steps):
 box(x,270,205,150,h,b,TEAL if i%2 else GOLD)
 if i<4:
  c.setStrokeColor(GOLD);c.setLineWidth(3);c.line(x+205,345,x+225,345)
 x+=235
c.setFillColor(MUTED);c.setFont('Helvetica',18);c.drawString(95,180,'Ask: what data was available, what was held out, and what errors matter in context?')
c.showPage()
# 10 applications
base('08 / AI in the world',10); title('One field, many kinds of systems')
box(75,345,330,155,'Perception','Vision, speech and sensing turn signals into useful representations.',TEAL)
box(475,345,330,155,'Language','Search, translation and dialogue systems process and generate text.',GOLD)
box(875,345,330,155,'Action','Robots and autonomous systems choose actions under constraints.',TEAL)
box(275,135,330,155,'Generative tools','Models produce new content; quality and provenance need evaluation.',GOLD)
box(675,135,330,155,'Decision support','Predictions inform people; responsibility and oversight remain essential.',TEAL)
c.showPage()
# 11 lab
base('09 / laboratory',11,True); title('Lab · build a small goal-directed agent', 'From specification to evidence',True)
bullet_list(['Define a grid world, start, goal and obstacles.','Implement a baseline random agent, then breadth-first search.','Measure path length, nodes expanded and success rate.','Change obstacles; explain when the first approach fails.'],85,490,1040,22,IVORY,38)
c.showPage()
# 12 knowledge check
base('10 / reflection & next steps',12); title('Check your understanding')
box(72,275,540,190,'Discuss','Can a system be useful without being intelligent? What evidence would change your answer?',GOLD)
box(668,275,540,190,'Apply','Choose one campus or community problem. Specify its goal, observations, actions and a measure of success.',TEAL)
c.setFillColor(NAVY);c.setFont('Times-Bold',25);c.drawCentredString(640,165,'Next: AI.101 continues with problem formulation and search strategies.')
c.setFont('Helvetica',15);c.setFillColor(MUTED);c.drawCentredString(640,112,'Remember: define the task, make assumptions visible, and evaluate behavior—not hype.')
c.showPage()
c.save()
print(OUT)
