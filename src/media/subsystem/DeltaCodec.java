package media.subsystem;

public final class DeltaCodec implements Codec {
    @Override
    public int[] decode(int[] values) {
        int[] samples = new int[values.length];
        long previous = 0;
        for (int index = 0; index < values.length; index++) {
            long sample = previous + values[index];
            if (sample < Short.MIN_VALUE || sample > Short.MAX_VALUE) {
                throw new IllegalArgumentException("Delta stream exceeds the signed 16-bit range.");
            }
            samples[index] = (int) sample;
            previous = sample;
        }
        return samples;
    }

    @Override
    public int[] encode(int[] samples) {
        int[] values = new int[samples.length];
        int previous = 0;
        for (int index = 0; index < samples.length; index++) {
            int sample = samples[index];
            if (sample < Short.MIN_VALUE || sample > Short.MAX_VALUE) {
                throw new IllegalArgumentException("PCM samples must be signed 16-bit values.");
            }
            values[index] = sample - previous;
            previous = sample;
        }
        return values;
    }
}
