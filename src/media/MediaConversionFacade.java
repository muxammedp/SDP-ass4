package media;

import java.io.IOException;
import java.nio.file.Path;
import media.subsystem.AudioData;
import media.subsystem.AudioMixer;
import media.subsystem.Codec;
import media.subsystem.CodecFactory;
import media.subsystem.EncodedMedia;
import media.subsystem.MediaWriter;
import media.subsystem.MetadataReader;

public final class MediaConversionFacade {
    private final MetadataReader reader = new MetadataReader();
    private final CodecFactory codecs = new CodecFactory();
    private final AudioMixer mixer = new AudioMixer();
    private final MediaWriter writer = new MediaWriter();

    public Path convert(Path source, String targetFormat, Path destination) throws ConversionException {
        try {
            if (source == null || destination == null) {
                throw new IllegalArgumentException("Source and destination are required.");
            }
            Codec encoder = codecs.create(targetFormat);
            EncodedMedia input = reader.read(source);
            Codec decoder = codecs.create(input.format());
            AudioData decoded = new AudioData(input.sampleRate(), input.channels(), decoder.decode(input.values()));
            AudioData mono = mixer.toMono(decoded);
            EncodedMedia output = new EncodedMedia(targetFormat, mono.sampleRate(), mono.channels(),
                    encoder.encode(mono.samples()));
            return writer.write(output, destination);
        } catch (IOException | IllegalArgumentException exception) {
            throw new ConversionException("Conversion failed: " + exception.getMessage(), exception);
        }
    }
}
