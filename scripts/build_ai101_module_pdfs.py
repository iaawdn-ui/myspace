"""Render AI.101 Markdown module manuscripts to polished PDFs with custom diagrams."""
from pathlib import Path
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, Flowable

ROOT=Path(__file__).resolve().parents[1]
NAVY=colors.HexColor('#17283F'); IVORY=colors.HexColor('#F7F4EC'); GOLD=colors.HexColor('#B28A4A'); TEAL=colors.HexColor('#416A70'); INK=colors.HexColor('#243246'); MUTED=colors.HexColor('#687486')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverTitleMod',fontName='Times-Bold',fontSize=28,leading=34,textColor=NAVY,spaceAfter=6*mm))
styles.add(ParagraphStyle(name='H1Mod',fontName='Times-Bold',fontSize=20,leading=24,textColor=NAVY,spaceBefore=6*mm,spaceAfter=3*mm,keepWithNext=True))
styles.add(ParagraphStyle(name='H2Mod',fontName='Times-Bold',fontSize=15,leading=19,textColor=TEAL,spaceBefore=4*mm,spaceAfter=2*mm,keepWithNext=True))
styles.add(ParagraphStyle(name='BodyMod',fontName='Helvetica',fontSize=9.5,leading=14.2,textColor=INK,spaceAfter=3*mm))
styles.add(ParagraphStyle(name='SmallMod',fontName='Helvetica',fontSize=8.5,leading=12,textColor=MUTED,spaceAfter=2*mm))
styles.add(ParagraphStyle(name='ListMod',fontName='Helvetica',fontSize=9.2,leading=13.5,textColor=INK,leftIndent=12,firstLineIndent=-10,spaceAfter=2*mm))
styles.add(ParagraphStyle(name='CaptionMod',fontName='Helvetica-Oblique',fontSize=8.2,leading=11,textColor=MUTED,alignment=TA_CENTER,spaceBefore=1*mm,spaceAfter=3*mm))

class Diagram(Flowable):
 def __init__(self,kind): Flowable.__init__(self); self.kind=kind; self.width=165*mm; self.height=62*mm
 def draw(self):
  c=self.canv
  if self.kind=='peas':
   labels=[('P','PERFORMANCE','safe delivery • time • energy'),('E','ENVIRONMENT','corridors • people • doors'),('A','ACTUATORS','wheels • brake • alert'),('S','SENSORS','camera • lidar • encoders')]
   for i,(letter,head,body) in enumerate(labels):
    x=(i%2)*81*mm; y=(1-i//2)*28*mm
    c.setFillColor(colors.white);c.setStrokeColor(GOLD if i%2==0 else TEAL);c.roundRect(x,y,76*mm,24*mm,3*mm,fill=1,stroke=1)
    c.setFillColor(NAVY);c.setFont('Times-Bold',16);c.drawString(x+4*mm,y+14*mm,letter)
    c.setFont('Helvetica-Bold',7.3);c.drawString(x+13*mm,y+16*mm,head)
    c.setFillColor(INK);c.setFont('Helvetica',7);c.drawString(x+13*mm,y+7*mm,body)
  elif self.kind=='boundary':
   c.setStrokeColor(GOLD);c.setLineWidth(1.3)
   c.roundRect(5*mm,8*mm,63*mm,43*mm,3*mm,fill=0,stroke=1)
   c.setFillColor(NAVY);c.setFont('Helvetica-Bold',8);c.drawCentredString(36*mm,46*mm,'ROBOT ONLY')
   c.setFillColor(TEAL);c.setFont('Helvetica',7);c.drawCentredString(36*mm,36*mm,'sensors • motors • onboard code')
   c.setStrokeColor(TEAL);c.roundRect(76*mm,4*mm,84*mm,51*mm,3*mm,fill=0,stroke=1)
   c.setFillColor(NAVY);c.setFont('Helvetica-Bold',8);c.drawCentredString(118*mm,49*mm,'FULL OPERATING CONTEXT')
   c.setFillColor(INK);c.setFont('Helvetica',7)
   for j,label in enumerate(['robot + map + building services','people + doors + elevators','network + operator + safety policy']):c.drawCentredString(118*mm,(37-j*9)*mm,label)
   c.setStrokeColor(GOLD);c.setLineWidth(1.4);c.line(68*mm,30*mm,76*mm,30*mm)
  else:
   dims=['Observable','Deterministic','Episodic','Static','Discrete','Single agent']
   for i,label in enumerate(dims):
    x=2*mm+(i%3)*55*mm;y=(1-i//3)*26*mm
    c.setFillColor(NAVY);c.roundRect(x,y,50*mm,19*mm,2*mm,fill=1,stroke=0)
    c.setFillColor(colors.white);c.setFont('Helvetica-Bold',7);c.drawCentredString(x+25*mm,y+11*mm,label)
    c.setFont('Helvetica',6.3);c.drawCentredString(x+25*mm,y+4*mm,'← campus robot →')
   c.setFillColor(TEAL);c.setFont('Helvetica-Bold',7.5);c.drawCentredString(82*mm,2*mm,'Typical profile: partial • stochastic • sequential • dynamic • mixed • multi-agent')

def make_pdf(md_path):
 text=md_path.read_text(); lines=text.splitlines()
 title=next((x[2:].strip() for x in lines if x.startswith('# ')),md_path.stem)
 module=next((x[2:].strip() for x in lines if x.startswith('## Narration manuscript')), 'Lecture narration')
 out=md_path.with_suffix('.pdf')
 doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=19*mm,leftMargin=19*mm,topMargin=21*mm,bottomMargin=19*mm,title=title,author='Triune Biblical University Global Extension USA')
 def footer(canvas,doc):
  canvas.saveState();w,h=A4
  if doc.page>1:
   canvas.setFillColor(IVORY);canvas.rect(0,0,w,h,fill=1,stroke=0)
   canvas.setStrokeColor(GOLD);canvas.line(18*mm,h-13*mm,w-18*mm,h-13*mm)
   canvas.setFont('Helvetica-Bold',7);canvas.setFillColor(MUTED);canvas.drawString(18*mm,h-10*mm,'AI.101  •  '+module.replace('Narration manuscript · ','').upper()[:70])
  canvas.setStrokeColor(GOLD);canvas.line(18*mm,13*mm,w-18*mm,13*mm)
  canvas.setFont('Helvetica-Bold',7);canvas.setFillColor(MUTED);canvas.drawString(18*mm,8*mm,'TRIUNE BIBLICAL UNIVERSITY GLOBAL EXTENSION USA')
  canvas.setFont('Helvetica',7);canvas.drawRightString(w-18*mm,8*mm,f'AI.101  •  {doc.page}');canvas.restoreState()
 story=[Spacer(1,8*mm),Paragraph(title.replace('&','&amp;'),styles['CoverTitleMod'])]
 img=ROOT/'assets/ai101_realistic_lab_cover.png'
 if img.exists():story.extend([Image(str(img),width=169*mm,height=95*mm),Paragraph('Illustrative engineering-laboratory image; not documentary evidence of a specific university or event.',styles['CaptionMod'])])
 story.extend([Paragraph(module.replace('&','&amp;'),styles['H2Mod']),Spacer(1,3*mm),Paragraph('<b>Academic level:</b> Bachelor of Artificial Intelligence and Robotics Engineering<br/><b>Content policy:</b> No faith-related content.',styles['BodyMod']),PageBreak()])
 in_body=False; para=[]
 def flush():
  nonlocal para
  if para:story.append(Paragraph(' '.join(para),styles['BodyMod']));para=[]
 for line in lines:
  if line.startswith('## Lecture narration'):in_body=True;continue
  if not in_body:continue
  if line.startswith('### '):
   flush();story.append(Paragraph(line[4:].replace('&','&amp;'),styles['H2Mod']))
  elif line.startswith('## '):
   flush();story.append(Paragraph(line[3:].replace('&','&amp;'),styles['H1Mod']))
  elif line.startswith('[DIAGRAM:'):
   flush();story.append(Paragraph(line[9:-1],styles['SmallMod']))
   kind='peas' if 'PEAS' in line.upper() else ('boundary' if 'boundar' in line.lower() else 'profile')
   story.extend([Diagram(kind),Paragraph('Diagram: '+('PEAS task specification' if kind=='peas' else 'System boundary' if kind=='boundary' else 'Environment classification profile'),styles['CaptionMod'])])
  elif line.startswith('[VISUAL:'):
   flush();story.append(Paragraph(line[8:-1],styles['SmallMod']))
  elif not line.strip():flush()
  elif line.startswith('- '):
   flush();story.append(Paragraph('• '+line[2:],styles['ListMod']))
  elif re.match(r'^\d+\.',line):
   flush();story.append(Paragraph(line,styles['ListMod']))
  else:para.append(line.strip())
 flush();doc.build(story,onFirstPage=footer,onLaterPages=footer)
 return out
if __name__=='__main__':
 for p in sorted((ROOT/'narrations').glob('AI101_Module_*.md')):print(make_pdf(p))
