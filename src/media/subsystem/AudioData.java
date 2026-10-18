package media.subsystem;

public record AudioData(int sampleRate, int channels, int[] samples) {
    public AudioData {
        if (sampleRate < 1 || sampleRate > 192000) {
            throw new IllegalArgumentException("Sample rate must be between 1 and 192000.");
        }
        if (channels != 1 && channels != 2) {
            throw new IllegalArgumentException("Only mono and stereo are supported.");
        }
        if (samples == null || samples.length == 0 || samples.length % channels != 0) {
            throw new IllegalArgumentException("Audio must contain complete, non-empty frames.");
        }
        for (int sample : samples) {
            if (sample < Short.MIN_VALUE || sample > Short.MAX_VALUE) {
                throw new IllegalArgumentException("Decoded samples must be signed 16-bit values.");
            }
        }
        samples = samples.clone();
    }

    @Override
    public int[] samples() {
        return samples.clone();
    }
}
