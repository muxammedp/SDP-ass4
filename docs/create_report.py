from pathlib import Path
import argparse
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Table, TableStyle, Flowable

ROOT = Path(__file__).resolve().parents[1]
(ROOT / '.work').mkdir(exist_ok=True)
parser = argparse.ArgumentParser(description='Build the assignment report with an optional verified repository URL.')
parser.add_argument('--repository')
args = parser.parse_args()
NAVY = colors.HexColor('#20354D')
GRAY = colors.HexColor('#D9D9D9')

def draw_diagram(c):
    def box(x, y, w, h, title, lines=(), tag=None):
        c.setStrokeColor(NAVY)
        c.setFillColor(colors.HexColor('#F2F5F8'))
        c.rect(x, y, w, h, fill=1)
        c.setFillColor(colors.black)
        c.setFont('Helvetica-Bold', 14)
        if tag:
            c.setFont('Helvetica', 11)
            c.drawCentredString(x+w/2, y+h-16, tag)
            c.setFont('Helvetica-Bold', 14)
            c.drawCentredString(x+w/2, y+h-34, title)
            split = y+h-43
        else:
            c.drawCentredString(x+w/2, y+h-21, title)
            split = y+h-31
        c.line(x, split, x+w, split)
        c.setFont('Helvetica', 11)
        for i, line in enumerate(lines):
            c.drawString(x+10, split-18-i*16, line)

    def arrow(points, dashed=False, triangle=False):
        import math
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.3)
        c.setDash([5, 4] if dashed else [])
        p=c.beginPath(); p.moveTo(*points[0])
        for point in points[1:]: p.lineTo(*point)
        c.drawPath(p)
        c.setDash([])
        x,y=points[-1]; px,py=points[-2]
        a=math.atan2(y-py,x-px)
        q1=(x-11*math.cos(a)+5*math.sin(a),y-11*math.sin(a)-5*math.cos(a))
        q2=(x-11*math.cos(a)-5*math.sin(a),y-11*math.sin(a)+5*math.cos(a))
        p=c.beginPath();p.moveTo(*q1);p.lineTo(x,y);p.lineTo(*q2)
        if triangle:
            p.close();c.setFillColor(colors.white);c.drawPath(p,fill=1)
        else: c.drawPath(p)

    box(280,545,220,65,'Main',['+ main(args): void'],'<<Client>>')
    box(200,395,380,112,'MediaConversionFacade',[
        '- reader, codecs, mixer, writer',
        '+ convert(source, targetFormat, destination): Path'], '<<Facade>>')
    arrow([(390,545),(390,507)],True)
    c.setFont('Helvetica',11);c.drawString(403,524,'uses')
    specs=[(0,'MetadataReader',['+ read(source):','  EncodedMedia']),
           (200,'CodecFactory',['+ create(format): Codec']),
           (400,'AudioMixer',['+ toMono(audio):','  AudioData']),
           (600,'MediaWriter',['+ write(media, path):','  Path'])]
    for x,title,lines in specs:
        box(x,245,180,85,title,lines)
    for start,end in [(240,90),(340,290),(440,490),(540,690)]:
        arrow([(start,395),(end,330)])
    c.setFont('Helvetica',11);c.drawString(340,353,'owns and coordinates')
    box(200,100,180,100,'Codec',['+ decode(values): int[]','+ encode(samples): int[]'],'<<interface>>')
    arrow([(290,245),(290,200)],True)
    c.drawString(301,219,'returns')
    box(0,0,180,58,'PcmCodec',['copies sample values'])
    box(240,0,180,58,'DeltaCodec',['encodes differences'])
    arrow([(90,58),(90,145),(200,145)],True,True)
    arrow([(330,58),(330,100)],True,True)
    c.setFillColor(colors.black)
    c.setFont('Helvetica',12)
    for i,line in enumerate([
        'Solid arrows: facade holds subsystem references',
        'Dashed arrows: dependency',
        'Hollow triangle: interface implementation',
        '',
        'Data records: AudioData and EncodedMedia',
        'Public failure contract: ConversionException',
        'Full relationships: docs/facade.puml']):
        c.drawString(435,190-i*21,line)

diagram=canvas.Canvas(str(ROOT/'.work/diagram.pdf'),pagesize=(800,635))
diagram.translate(10,12);draw_diagram(diagram);diagram.save()

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportTitle',fontName='Helvetica-Bold',fontSize=24,leading=29,spaceAfter=14,textColor=colors.black))
styles.add(ParagraphStyle(name='BodyReport',fontName='Helvetica',fontSize=10.5,leading=15,spaceAfter=9))
styles.add(ParagraphStyle(name='CodeReport',fontName='Courier',fontSize=9,leading=12,spaceBefore=4,spaceAfter=8))
styles.add(ParagraphStyle(name='CaptionReport',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=10))
for name in ['Heading1','Heading2']:
    styles[name].textColor=colors.black
    styles[name].spaceBefore=12
    styles[name].spaceAfter=8
styles['Heading1'].fontSize=17
styles['Heading1'].leading=21
styles['Heading2'].fontSize=12
styles['Heading2'].leading=16
story=[]
def p(text): story.append(Paragraph(text,styles['BodyReport']))
def h(text): story.append(Paragraph(text,styles['Heading1']))
def h2(text): story.append(Paragraph(text,styles['Heading2']))
def code(text): story.append(Preformatted(text,styles['CodeReport']))
def page(): story.append(PageBreak())
def table(rows,widths):
    cells=[[Paragraph(escape(x),styles['CaptionReport']) for x in row] for row in rows]
    t=Table(cells,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E7EDF3')),('GRID',(0,0),(-1,-1),0.5,GRAY),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)]))
    story.append(t);story.append(Spacer(1,10))

story.append(Paragraph('Media Conversion Facade',styles['ReportTitle']))
p('<b>Assignment 4 | Software Design Patterns</b><br/>Zhuman Mukhammed | SE-2522<br/>18 October 2026 | Java 17 | Option A')
h('Introduction')
p('The project demonstrates the Facade pattern using a media conversion subsystem. A caller supplies a source path, a target encoding and a destination path. One operation produces a mono output file while the facade coordinates parsing, codec selection, decoding, channel mixing, encoding and writing.')
p('Without the facade, a normal application client would need to know the subsystem types and the valid order of their operations. This design puts that orchestration in MediaConversionFacade and keeps each algorithm in its own subsystem class. Main depends only on the facade and its public error type.')
h('Conversion model')
p('The assignment permits simulated media. This implementation uses two custom text encodings of actual integer sample data: pcm stores sample values, and delta stores differences between consecutive values. These files are teaching containers, not standard PCM audio files, WAV files or MP3 files. No audio library is required.')
table([['Stage','Responsibility'],['Read','MetadataReader validates the container structure and parses fields.'],['Decode','CodecFactory selects a source codec; decoded audio is validated.'],['Mix','AudioMixer averages left and right samples for each stereo frame.'],['Encode','The target codec copies samples or computes their differences.'],['Save','MediaWriter creates the output without overwriting existing files.']],[68,431])
h2('A concrete transformation')
p('Stereo frames (1000, 3000), (2000, 4000), (-1000, 1000) become mono samples 2000, 3000, 0. Delta encoding produces 2000, 1000, -3000. Decoding reconstructs 2000, 3000, 0 by cumulative addition. The sample rate is preserved.')
p('The mono encoding round trip is lossless. Stereo mixing intentionally loses channel information, and integer division truncates fractional averages toward zero.')

page();h('UML class diagram')
class Diagram(Flowable):
    def __init__(self): Flowable.__init__(self); self.width=499; self.height=401
    def draw(self):
        self.canv.saveState();self.canv.scale(499/800,499/800);self.canv.translate(10,12);draw_diagram(self.canv);self.canv.restoreState()
story.append(Diagram())
story.append(Paragraph('Figure 1. Client, facade and operational subsystem classes. The editable PlantUML file also shows data-record dependencies, codec creation and the exception contract.',styles['CaptionReport']))
h2('Public API and dependency direction')
code('Path convert(Path source, String targetFormat, Path destination)\n        throws ConversionException')
p('The method returns the written file path. Parameters and results use standard Java types; clients do not construct codecs or exchange internal audio records. The public ConversionException preserves its original cause for diagnostics.')
p('The facade holds four subsystem objects and uses codecs returned by CodecFactory. PcmCodec and DeltaCodec implement the same Codec interface. AudioData validates decoded sample ranges and complete frames. Both data records copy arrays when constructed and when accessed.')
p('Subsystem classes are public and never reference the facade. Advanced clients may call them directly. This preserves the defining Facade property: the simplified entry point is a convenience, not an access barrier.')

page();h('Clean Code principles')
p('The following excerpts come from the implementation. The accompanying explanations identify the purpose of each design choice.')
h2('1 Meaningful names')
code('MediaConversionFacade converter = new MediaConversionFacade();\nPath result = converter.convert(\n        Path.of(args[0]), args[1], Path.of(args[2]));')
p('<b>Anchor:</b> src/Main.java. The class and method state the use case. Inside the facade, source, targetFormat, destination, decoded and mono identify the role and stage of each value. A caller can understand the operation without reading codec code.')
h2('2 Single responsibility')
code('AudioData mono = mixer.toMono(decoded);\nEncodedMedia output = new EncodedMedia(targetFormat,\n        mono.sampleRate(), mono.channels(),\n        encoder.encode(mono.samples()));\nreturn writer.write(output, destination);')
p('<b>Anchor:</b> MediaConversionFacade.convert. The facade orders operations and passes results between them. It delegates mixing to AudioMixer, encoding to Codec and output handling to MediaWriter. A change to delta arithmetic therefore belongs in DeltaCodec, rather than in the client or facade.')
h2('3 Encapsulation at the API boundary')
code('public Path convert(Path source, String targetFormat,\n        Path destination) throws ConversionException')
p('<b>Anchor:</b> MediaConversionFacade. The public conversion method contains no Codec, AudioData or EncodedMedia parameter. A simple caller uses paths and a format name. Internal records defensively copy arrays, preventing callers from silently mutating stored data through a shared array reference.')
p('The facade does not make subsystems private or inaccessible. It reduces the dependencies required for an ordinary client while preserving direct access for specialized clients.')

page();h('Clean Code and failure handling')
h2('4 Small focused operations')
code('for (int frame = 0; frame < mono.length; frame++) {\n    int left = stereo[frame * 2];\n    int right = stereo[frame * 2 + 1];\n    mono[frame] = (left + right) / 2;\n}')
p('<b>Anchor:</b> AudioMixer.toMono. This loop handles only channel mixing. It does not parse files, select formats or write output. AudioData has already checked that stereo frames are complete and that samples fit signed 16-bit range, so adding two samples is safe within a Java int.')
h2('5 Explicit error handling and cleanup')
code('} catch (IOException | IllegalArgumentException exception) {\n    throw new ConversionException(\n            "Conversion failed: " + exception.getMessage(),\n            exception);\n}')
p('<b>Anchor:</b> MediaConversionFacade.convert. The client receives one checked exception for expected conversion failures. The original exception remains available as the cause. Main prints the diagnostic and exits with status 1; incorrect command usage exits with status 2.')
code('try {\n    Files.writeString(temporary, content, StandardCharsets.UTF_8);\n    return Files.move(temporary, target);\n} finally {\n    Files.deleteIfExists(temporary);\n}')
p('<b>Anchor:</b> MediaWriter.write. Validation and transformations finish before the writer runs. An existing destination is rejected. Output is first written to a temporary sibling file, then moved without a replace option. The finally block removes a remaining temporary file on success or failure. This avoids deliberately overwriting user data and publishing a partially written file during ordinary handled failures.')
h2('Design tradeoffs')
p('The facade constructs its fixed collaborators directly to keep this small assignment easy to follow. Constructor injection would help a larger application substitute services. CodecFactory uses a two-case switch; adding a third codec requires updating that factory. Files are loaded into memory, so this design targets small examples. It does not claim crash-safe durability, standard audio compression, playback or resampling.')

page();h('Verification and demonstration')
p('The verification suite calls the facade and checks output file contents. It covers 25 successful and failing scenarios, including sample-level round trips, boundary values, malformed input, invalid metadata, unsupported formats, null arguments and protection of existing files. The saved verification log records the compiler and runtime used.')
table([['Coverage','Observed behavior'],['Conversion','Expected delta values, decoded PCM, mono round trip, same-format conversion, rounding, stereo delta input.'],['Invalid input','Unknown source/target format, missing file, bad header, non-numeric data, incomplete frames, invalid rate/channels, sample overflow, empty audio/token.'],['Output and API','Missing destination directory, preserved output/source, null arguments, no temporary files left.']],[105,394])
code('javac --release 17 -encoding UTF-8 -Xlint:all -Werror \\\n    -d out @sources.txt tests/FacadeTests.java\njava -cp out FacadeTests\n\njava -cp out Main samples/stereo.pcm delta converted.delta\njava -cp out Main converted.delta pcm restored.pcm')
p('The compiler command above is shown across two lines for readability; run it on one line. In PowerShell, quote the argument-file parameter as <font name="Courier">\'@sources.txt\'</font>. The provided build.ps1 automates compilation and verification. Use new destination filenames for repeated demonstrations.')
h('Conclusion')
p('MediaConversionFacade gives the client one meaningful operation over a collaborating subsystem. It hides the order of conversion steps, codec selection and output coordination. The subsystem retains the actual algorithms and remains directly usable, independent of the facade. The implementation demonstrates simplification through coordination rather than moving all behavior into one large class.')
h2('Repository and submission')
if args.repository:
    p('<b>GitHub repository:</b> ' + escape(args.repository))
    p('The project includes incremental Git commits, source files, examples, tests, the UML source and defense notes.')
else:
    p('<b>GitHub repository:</b> not yet published. The actual repository URL must be inserted before submission. The local project includes incremental Git commits, source files, examples, tests, the UML source and defense notes.')
p('<b>Assignment source:</b> Assignment_4_Facade_Pattern_Instructions.docx, supplied course handout. The handout limits generative AI to examples and clarification. The student should independently review and adapt this worked example before submitting under that policy.')

def footer(c,doc):
    c.saveState();c.setFillColor(colors.HexColor('#555555'));c.setFont('Helvetica',8)
    c.drawString(48,28,'Zhuman Mukhammed  |  SE-2522  |  Assignment 4')
    c.drawRightString(547,28,str(doc.page));c.restoreState()
doc=SimpleDocTemplate(str(ROOT/'report.pdf'),pagesize=(595.28,841.89),rightMargin=48,leftMargin=48,topMargin=42,bottomMargin=48,title='Media Conversion Facade',author='Zhuman Mukhammed')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(ROOT/'report.pdf')
