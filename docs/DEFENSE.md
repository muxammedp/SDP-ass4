# Facade defense preparation

## Opening explanation

I chose media conversion because the caller would otherwise have to parse the file, select two codecs, decode samples, mix channels, encode the result, and save it. My facade replaces this sequence with one `convert` call. The subsystem still performs the actual work.

```java
MediaConversionFacade converter = new MediaConversionFacade();
Path output = converter.convert(
        Path.of("samples/stereo.pcm"), "delta", Path.of("converted.delta"));
```

## Walkthrough

1. Show `Main`: it imports the facade and its exception, with no subsystem imports.
2. Show `MediaConversionFacade.convert`: target validation, reading, decoding, mixing, encoding, and writing are ordered explicitly.
3. Show `DeltaCodec`: encoding stores differences; decoding reconstructs samples by cumulative addition.
4. Show `AudioMixer`: it averages each pair of interleaved stereo samples.
5. Show `MediaWriter`: existing output is rejected, data is written to a temporary sibling file, and the temporary file is removed in `finally`.
6. Run `build.ps1` and demonstrate a conversion with the commands in the README.

## Questions and answers

**What is a Facade?** A structural pattern that gives a simple entry point to a set of collaborating subsystem classes.

**What exactly does yours hide?** Container parsing, selecting source and target codecs, sequencing decode/mix/encode, building the output container, temporary-file handling, and translating failures into `ConversionException`.

**Why is it more than a wrapper?** The single method coordinates several different objects. It does not just forward one call to one underlying object.

**Does the facade contain conversion algorithms?** No. Delta arithmetic belongs to `DeltaCodec`, channel averaging belongs to `AudioMixer`, and file I/O belongs to the reader and writer.

**Can advanced clients bypass the facade?** Yes. The subsystem types are public, have public methods, and do not import the facade. For example, an advanced caller can create an `AudioMixer` and call `toMono` directly. Our CLI deliberately does not do that.

**Why is `CodecFactory` not the facade?** It only selects a codec. The facade coordinates the complete use case, including reading, decoding, mixing, encoding, and writing.

**How is this different from Adapter?** Adapter makes an existing interface fit another expected interface. This facade supplies a simpler interface to several collaborating classes.

**How is this different from Mediator?** A mediator manages communication among colleagues that normally know the mediator. Here the subsystem classes do not know the facade exists.

**Are these real MP3 or WAV files?** No. They are documented teaching containers with real sample transformations. The assignment permits simulated media data. Delta encoding here is a reversible representation, not a claim of file-size compression.

**Is conversion lossless?** Mono PCM to delta and back is lossless. Stereo-to-mono averaging loses independent channel information. Integer division truncates fractional averages toward zero.

**Why can a delta exceed 32767?** A transition from 32767 to -32768 has delta -65535. Encoded deltas use Java `int`; reconstructed PCM samples must fit signed 16-bit range.

**What happens if something fails?** The facade returns no output path and throws `ConversionException` with the original cause. Validation and decoding finish before writing. Existing files are never intentionally overwritten; a temporary file is cleaned up if writing or moving fails. The implementation does not claim crash-safe durability or a transaction across multiple files.

**How would you add another codec?** Implement `Codec`, register the name in `CodecFactory`, add an example and tests, and update documentation. The client and orchestration sequence can remain unchanged. The factory switch is a deliberate simple choice for two codecs; a larger plugin system could use a registry.

**What are the limits?** Only mono/stereo, signed 16-bit decoded samples, small files held in memory, two custom text encodings, and no real audio playback or resampling.

## Russian concept notes

Facade — это удобная точка входа. Клиент знает, что хочет получить, но не должен знать порядок работы подсистем. Здесь клиент вызывает `convert`, а фасад организует чтение, декодирование, сведение каналов, кодирование и запись.

Не путай координацию с выполнением: фасад решает, какой шаг вызвать следующим; вычисления выполняют подсистемы. Они ничего не знают о фасаде и доступны отдельно.
