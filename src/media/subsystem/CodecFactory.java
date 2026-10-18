package media.subsystem;

public final class CodecFactory {
    public Codec create(String format) {
        if (format == null) {
            throw new IllegalArgumentException("Target format is required.");
        }
        return switch (format) {
            case "pcm" -> new PcmCodec();
            case "delta" -> new DeltaCodec();
            default -> throw new IllegalArgumentException("Unsupported format: " + format);
        };
    }
}
