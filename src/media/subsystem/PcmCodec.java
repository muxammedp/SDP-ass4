package media.subsystem;

public final class PcmCodec implements Codec {
    @Override
    public int[] decode(int[] values) {
        return values.clone();
    }

    @Override
    public int[] encode(int[] samples) {
        return samples.clone();
    }
}
