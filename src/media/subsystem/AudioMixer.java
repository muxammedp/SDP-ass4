package media.subsystem;

public final class AudioMixer {
    public AudioData toMono(AudioData audio) {
        if (audio.channels() == 1) {
            return audio;
        }
        int[] stereo = audio.samples();
        int[] mono = new int[stereo.length / 2];
        for (int frame = 0; frame < mono.length; frame++) {
            int left = stereo[frame * 2];
            int right = stereo[frame * 2 + 1];
            mono[frame] = (left + right) / 2;
        }
        return new AudioData(audio.sampleRate(), 1, mono);
    }
}
