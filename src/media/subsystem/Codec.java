package media.subsystem;

public interface Codec {
    int[] decode(int[] values);
    int[] encode(int[] samples);
}
