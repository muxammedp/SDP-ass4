# Assignment 4 - Facade Pattern

Java 17 implementation of Option A: Media/File Conversion Facade.

`MediaConversionFacade.convert(source, targetFormat, destination)` coordinates file parsing, codec selection, decoding, stereo-to-mono mixing, encoding, and safe output creation. `Main` uses only the facade and its public exception.

## Run

Use JDK 17 or newer, not a Java 8 JRE. No Maven or external Java libraries are needed. Run commands from this project folder.

```powershell
javac --release 17 -encoding UTF-8 -d out '@sources.txt'
java -cp out Main samples/stereo.pcm delta converted.delta
Get-Content converted.delta
java -cp out Main converted.delta pcm restored.pcm
```

Choose a new output filename on each run. Existing files are deliberately preserved, and the destination directory must already exist.

Expected converted payload: `2000,1000,-3000,32767,-65535`.
Expected restored mono samples: `2000,3000,0,32767,-32768`.

For the optional local portable JDK, which is excluded from the submission archive:

```powershell
$jdk = (Get-ChildItem .tools/jdk* -Directory | Select-Object -First 1).FullName
& "$jdk/bin/java.exe" -cp out Main samples/stereo.pcm delta converted.delta
```

## Verify

```powershell
.\build.ps1
```

If Java is not on PATH, use `.\build.ps1 -JavaHome 'C:\path\to\jdk-17'` or set `JAVA_HOME`. The script also detects the optional JDK in `.tools`. It compiles with Java 17 compatibility, treats compiler warnings as errors, and runs 25 checks. A failed assertion returns a nonzero exit code. Checks use temporary files and remove them after execution.

Manual equivalent:

```powershell
javac --release 17 -encoding UTF-8 -Xlint:all -Werror -d out '@sources.txt' tests/FacadeTests.java
java -cp out FacadeTests
```

## File format and scope

These are simulated media containers, not WAV, MP3, or compressed audio. Every file contains exactly five lines:

```text
SAMPLEMEDIA/1
format=pcm
sampleRate=44100
channels=2
data=1000,3000,2000,4000
```

- `pcm`: comma-separated signed 16-bit sample values, stored as text.
- `delta`: first value is the first sample; each later value is the difference from the preceding sample in the interleaved stream. A delta may range from -65535 to 65535.
- Channels: 1 (mono) or 2 (interleaved left/right stereo).
- Sample rate: 1 to 192000 Hz, preserved by conversion.
- Output is always mono. Each stereo frame becomes `(left + right) / 2`, with integer division truncating toward zero. Stereo mixing loses channel information; the mono PCM/delta round trip is lossless.

The pipeline processes real integer samples. It does not merely change the extension or print conversion messages. Files are read into memory, so this example targets small teaching datasets.

## Structure

| Location | Responsibility |
| --- | --- |
| `src/Main.java` | CLI client |
| `src/media/MediaConversionFacade.java` | Coordinates the conversion |
| `src/media/ConversionException.java` | Stable facade error contract retaining the cause |
| `src/media/subsystem/MetadataReader.java` | Parses container metadata and numeric data |
| `src/media/subsystem/CodecFactory.java` | Selects PCM or delta codec |
| `src/media/subsystem/AudioMixer.java` | Converts stereo frames to mono |
| `src/media/subsystem/MediaWriter.java` | Writes through a temporary file and refuses overwrites |
| `src/media/subsystem/Codec.java` | Common encoding and decoding contract |
| `src/media/subsystem/PcmCodec.java` and `DeltaCodec.java` | Concrete codec algorithms |
| `src/media/subsystem/AudioData.java` and `EncodedMedia.java` | Data records with defensive array copies |
| `tests/FacadeTests.java` | End-to-end verification through the facade |
| `docs/facade.puml` and `docs/facade.png` | Editable UML source and rendered diagram |
| `report.pdf` | Assignment report with five Clean Code examples |
| `docs/DEFENSE.md` | Design walkthrough and defense questions |
| `verification.txt` | Saved validation evidence |

Subsystem classes are public and have no reference to the facade. Advanced callers can reuse them independently. The application client does not do this.

## Submission

The project includes local incremental Git commits. Publish the repository to your own GitHub account, then add its actual URL to the report before uploading the report and link to Moodle. No remote repository is assumed or fabricated here.

The supplied assignment limits AI use to examples and clarification. Review the implementation, adapt it independently, and ensure that your submission follows your course policy.
