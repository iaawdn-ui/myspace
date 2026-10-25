from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, KeepTogether, Flowable
from reportlab.pdfbase.pdfmetrics import stringWidth
import re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'narrations/AI101_Module_01_Foundations.pdf'
source=(ROOT/'narrations/AI101_Module_01_Foundations.md').read_text()
NAVY=colors.HexColor('#17283F'); IVORY=colors.HexColor('#F7F4EC'); GOLD=colors.HexColor('#B28A4A'); TEAL=colors.HexColor('#416A70'); INK=colors.HexColor('#243246'); MUTED=colors.HexColor('#687486')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverTitleX',fontName='Times-Bold',fontSize=29,leading=35,textColor=NAVY,spaceAfter=7*mm))
styles.add(ParagraphStyle(name='H1x',fontName='Times-Bold',fontSize=20,leading=25,textColor=NAVY,spaceBefore=6*mm,spaceAfter=3*mm,keepWithNext=True))
styles.add(ParagraphStyle(name='H2x',fontName='Times-Bold',fontSize=15,leading=19,textColor=TEAL,spaceBefore=4*mm,spaceAfter=2*mm,keepWithNext=True))
styles.add(ParagraphStyle(name='Bodyx',fontName='Helvetica',fontSize=9.7,leading=14.5,textColor=INK,spaceAfter=3*mm))
styles.add(ParagraphStyle(name='Smallx',fontName='Helvetica',fontSize=8.5,leading=12,textColor=MUTED,spaceAfter=2*mm))
styles.add(ParagraphStyle(name='Listx',fontName='Helvetica',fontSize=9.5,leading=14,textColor=INK,leftIndent=12,firstLineIndent=-10,spaceAfter=2*mm))
styles.add(ParagraphStyle(name='Captionx',fontName='Helvetica-Oblique',fontSize=8.5,leading=12,textColor=MUTED,alignment=TA_CENTER,spaceBefore=2*mm,spaceAfter=3*mm))
class AgentDiagram(Flowable):
 def __init__(self): Flowable.__init__(self); self.width=165*mm; self.height=65*mm
 def draw(self):
  c=self.canv; boxes=[(5,25,45,25,'ENVIRONMENT'),(105,25,45,25,'AGENT')]
  for x,y,w,h,label in boxes:
   c.setFillColor(IVORY);c.setStrokeColor(NAVY);c.roundRect(x*mm,y*mm,w*mm,h*mm,3*mm,fill=1,stroke=1)
   c.setFillColor(NAVY);c.setFont('Helvetica-Bold',8);c.drawCentredString((x+w/2)*mm,(y+h/2-1)*mm,label)
  c.setStrokeColor(TEAL);c.setLineWidth(1.6)
  # directional arrows and labels
  for x1,x2,y,label in [(50,105,43,'percept'),(105,50,31,'action')]:
   c.line(x1*mm,y*mm,x2*mm,y*mm); direction=1 if x2>x1 else -1
   p=c.beginPath(); p.moveTo(x2*mm,y*mm);p.lineTo((x2-3*direction)*mm,(y+1.7)*mm);p.lineTo((x2-3*direction)*mm,(y-1.7)*mm);p.close()
   c.setFillColor(TEAL);c.drawPath(p,fill=1,stroke=0)
   c.setFont('Helvetica',7);c.setFillColor(TEAL);c.drawCentredString(77.5*mm,(y+2)*mm,label)
  c.setFillColor(GOLD);c.setFont('Helvetica-Bold',7);c.drawCentredString(82.5*mm,6*mm,'GOAL + PERFORMANCE MEASURE guide action selection')
class MapDiagram(Flowable):
 def __init__(self): Flowable.__init__(self);self.width=165*mm;self.height=52*mm
 def draw(self):
  c=self.canv; cols=[NAVY,TEAL,GOLD]; groups=[('TASKS',['perception','planning','language','decision']),('METHODS',['rules','search','learning','optimization']),('APPLICATIONS',['robotics','health','industry','accessibility'])]
  for i,(head,items) in enumerate(groups):
   x=(i*57+2)*mm;c.setFillColor(cols[i]);c.roundRect(x,8*mm,49*mm,38*mm,2*mm,fill=1,stroke=0);c.setFillColor(colors.white);c.setFont('Helvetica-Bold',8);c.drawCentredString(x+24.5*mm,39*mm,head)
   c.setFont('Helvetica',7)
   for j,item in enumerate(items):c.drawCentredString(x+24.5*mm,(31-j*5)*mm,item)
  c.setStrokeColor(GOLD);c.setDash(2,2)
  for y in [25,19,13]:c.line(51*mm,y*mm,61*mm,y*mm);c.line(108*mm,y*mm,118*mm,y*mm)
  c.setDash()

def page(canvas,doc):
 canvas.saveState();w,h=A4
 if doc.page>1:
  canvas.setFillColor(IVORY);canvas.rect(0,0,w,h,fill=1,stroke=0)
  canvas.setStrokeColor(GOLD);canvas.line(18*mm,h-13*mm,w-18*mm,h-13*mm)
  canvas.setFont('Helvetica-Bold',7);canvas.setFillColor(MUTED);canvas.drawString(18*mm,h-10*mm,'TRIUNE BIBLICAL UNIVERSITY GLOBAL EXTENSION USA  •  AI.101')
 canvas.setStrokeColor(GOLD);canvas.line(18*mm,13*mm,w-18*mm,13*mm)
 canvas.setFont('Helvetica-Bold',7);canvas.setFillColor(MUTED);canvas.drawString(18*mm,8*mm,'TRIUNE BIBLICAL UNIVERSITY GLOBAL EXTENSION USA')
 canvas.setFont('Helvetica',7);canvas.drawRightString(w-18*mm,8*mm,f'AI.101 — INTRODUCTION TO ARTIFICIAL INTELLIGENCE  •  {doc.page}');canvas.restoreState()

doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=19*mm,leftMargin=19*mm,topMargin=21*mm,bottomMargin=19*mm,title='AI.101 Module 1 — What Is Artificial Intelligence?',author='Triune Biblical University Global Extension USA')
story=[]
# custom cover with photo
story += [Spacer(1,12*mm),Paragraph('AI.101  /  INTRODUCTION TO ARTIFICIAL INTELLIGENCE',styles['Smallx']),Paragraph('What Is Artificial Intelligence?',styles['CoverTitleX'])]
img=ROOT/'assets/ai101_realistic_lab_cover.png'
if img.exists():
 im=Image(str(img),width=169*mm,height=95*mm); story += [im,Paragraph('A documentary-style illustrative view of students working with a mobile robot.',styles['Captionx'])]
story += [Spacer(1,4*mm),Paragraph('<b>MODULE 1 · FOUNDATIONS</b><br/>University-level narration manuscript with guided visual cues, diagrams, practical work, and assessment.',styles['Bodyx'])]
notice=Table([[Paragraph('<b>Course target:</b> at least 100,000 spoken words, developed as sequenced modules. This PDF is the first installment, not the complete course. This course manuscript excludes faith-related content.',styles['Bodyx'])]],colWidths=[169*mm]);notice.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#ECE7DB')),('BOX',(0,0),(-1,-1),.7,GOLD),('LEFTPADDING',(0,0),(-1,-1),5*mm),('RIGHTPADDING',(0,0),(-1,-1),5*mm),('TOPPADDING',(0,0),(-1,-1),4*mm),('BOTTOMPADDING',(0,0),(-1,-1),2*mm)]));story += [notice,PageBreak()]
# Learning objectives
story += [Paragraph('Learning objectives',styles['H1x'])]
for line in ['Give a careful working definition of artificial intelligence.','Distinguish a task from a method.','Explain the agent–environment interaction loop.','Recognize symbolic, statistical, connectionist, and hybrid approaches.','Specify a small AI task using observations, actions, constraints, and measurable outcomes.']:
 story.append(Paragraph('• '+line,styles['Listx']))
story += [Spacer(1,3*mm),Paragraph('Agent–environment loop',styles['H1x']),AgentDiagram(),Paragraph('The agent receives percepts, selects actions, and changes the environment. A goal and performance measure define what counts as useful behavior.',styles['Captionx']),PageBreak()]
# parse markdown headings and paragraphs after first known heading
lines=source.splitlines();started=False;para=[]
for line in lines:
 if line.startswith('## Lecture narration'): started=True;continue
 if not started: continue
 if line.startswith('## Module 1 visual'): break
 if line.startswith('### '):
  if para:
   story.append(Paragraph(' '.join(para),styles['Bodyx']));para=[]
  story.append(Paragraph(line[4:],styles['H2x']))
 elif line.startswith('[VISUAL:'):
  if para: story.append(Paragraph(' '.join(para),styles['Bodyx']));para=[]
  story.append(Paragraph(line[9:-1],styles['Smallx']))
  if 'agent–environment' in line.lower():story.append(AgentDiagram())
  if 'conceptual map' in line.lower() or 'three nested bands' in line.lower():story.append(MapDiagram())
 elif line.strip()=='':
  if para: story.append(Paragraph(' '.join(para),styles['Bodyx']));para=[]
 elif line.startswith('1.') or re.match(r'^\d+\.',line):
  if para: story.append(Paragraph(' '.join(para),styles['Bodyx']));para=[]
  story.append(Paragraph(line,styles['Listx']))
 else: para.append(line.strip())
if para:story.append(Paragraph(' '.join(para),styles['Bodyx']))
story += [PageBreak(),Paragraph('Visual assets and teaching notes',styles['H1x']),Paragraph('Task–method–application map',styles['H2x']),MapDiagram(),Paragraph('Course map: tasks describe what a system is meant to do; methods describe how it is done; application areas describe where the system is used. Connections cross categories.',styles['Captionx'])]
doc.build(story,onFirstPage=page,onLaterPages=page)
print(OUT)
