package media.subsystem;

public record EncodedMedia(String format, int sampleRate, int channels, int[] values) {
    public EncodedMedia {
        if (format == null || format.isBlank() || values == null) {
            throw new IllegalArgumentException("Format and encoded values are required.");
        }
        values = values.clone();
    }

    @Override
    public int[] values() {
        return values.clone();
    }
}
