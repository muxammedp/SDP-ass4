import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import media.ConversionException;
import media.MediaConversionFacade;

public final class FacadeTests {
    private final MediaConversionFacade facade = new MediaConversionFacade();
    private final Path directory;
    private int passed;
    private int sequence;

    private FacadeTests(Path directory) {
        this.directory = directory;
    }

    public static void main(String[] args) throws Exception {
        Path directory = Files.createTempDirectory("facade-tests-").toAbsolutePath().normalize();
        try {
            FacadeTests tests = new FacadeTests(directory);
            tests.run();
            System.out.println("SUMMARY: " + tests.passed + "/" + tests.passed + " PASS");
        } finally {
            try (var paths = Files.walk(directory)) {
                for (Path path : paths.sorted(Comparator.reverseOrder()).toList()) {
                    if (!path.toAbsolutePath().normalize().startsWith(directory)) {
                        throw new IOException("Cleanup path is outside the test directory.");
                    }
                    Files.delete(path);
                }
            }
        }
    }

    private void run() throws Exception {
        Path stereo = file("pcm", 44100, 2, "1000,3000,2000,4000,-1000,1000,32767,32767,-32768,-32768");
        Path delta = nextPath();
        facade.convert(stereo, "delta", delta);
        equal("stereo to delta", content("delta", 44100, 1, "2000,1000,-3000,32767,-65535"), Files.readString(delta));
        Path restored = nextPath();
        facade.convert(delta, "pcm", restored);
        equal("delta to PCM", content("pcm", 44100, 1, "2000,3000,0,32767,-32768"), Files.readString(restored));
        Path mono = file("pcm", 22050, 1, "-32768,-1,0,1,32767");
        Path encoded = nextPath();
        facade.convert(mono, "delta", encoded);
        Path decoded = nextPath();
        facade.convert(encoded, "pcm", decoded);
        equal("mono lossless round trip", Files.readString(mono), Files.readString(decoded));
        Path same = nextPath();
        facade.convert(mono, "pcm", same);
        equal("same format conversion", Files.readString(mono), Files.readString(same));
        Path odd = file("pcm", 8000, 2, "-1,0,0,1");
        Path rounded = nextPath();
        facade.convert(odd, "pcm", rounded);
        equal("averages truncate toward zero", content("pcm", 8000, 1, "0,0"), Files.readString(rounded));
        Path stereoDelta = file("delta", 16000, 2, "1000,2000,-1000,2000");
        Path mixed = nextPath();
        facade.convert(stereoDelta, "pcm", mixed);
        equal("decode before mixing", content("pcm", 16000, 1, "2000,3000"), Files.readString(mixed));
        rejects("unsupported target", stereo, "mp3", nextPath());
        rejects("unsupported source", file("mp3", 44100, 1, "0"), "pcm", nextPath());
        rejects("missing input", nextPath(), "pcm", nextPath());
        Path broken = nextPath();
        Files.writeString(broken, "not a media file\n");
        rejects("bad header", broken, "pcm", nextPath());
        rejects("non-numeric payload", file("pcm", 44100, 1, "abc"), "pcm", nextPath());
        rejects("incomplete stereo frame", file("pcm", 44100, 2, "1,2,3"), "pcm", nextPath());
        rejects("invalid sample rate", file("pcm", 0, 1, "0"), "pcm", nextPath());
        rejects("unsupported channel count", file("pcm", 44100, 3, "0,0,0"), "pcm", nextPath());
        rejects("PCM out of range", file("pcm", 44100, 1, "32768"), "delta", nextPath());
        rejects("delta overflow", file("delta", 44100, 1, "32767,2147483647"), "pcm", nextPath());
        rejects("empty audio", file("pcm", 44100, 1, ""), "pcm", nextPath());
        rejects("empty final token", file("pcm", 44100, 1, "1,"), "pcm", nextPath());
        rejects("missing output directory", mono, "pcm", directory.resolve("missing/result.pcm"));
        Path existing = nextPath();
        Files.writeString(existing, "keep me");
        rejects("existing output preserved", mono, "pcm", existing);
        rejects("source cannot be overwritten", mono, "delta", mono);
        rejects("null input", null, "pcm", nextPath());
        rejects("null target", mono, null, nextPath());
        rejects("null destination", mono, "pcm", null);
        try (var files = Files.list(directory)) {
            equal("no temporary files remain", false,
                    files.anyMatch(path -> path.getFileName().toString().startsWith(".conversion-")));
        }
    }

    private void rejects(String name, Path source, String format, Path destination) throws Exception {
        String previous = destination != null && Files.isRegularFile(destination) ? Files.readString(destination) : null;
        try {
            facade.convert(source, format, destination);
            throw new AssertionError(name + ": conversion unexpectedly succeeded");
        } catch (ConversionException expected) {
            if (expected.getCause() == null) {
                throw new AssertionError(name + ": original cause was lost");
            }
            if (destination != null) {
                if (previous == null && Files.exists(destination)) {
                    throw new AssertionError(name + ": failed conversion created an output");
                }
                if (previous != null && !previous.equals(Files.readString(destination))) {
                    throw new AssertionError(name + ": existing file was changed");
                }
            }
            pass(name);
        }
    }

    private Path file(String format, int sampleRate, int channels, String data) throws IOException {
        Path path = nextPath();
        Files.writeString(path, content(format, sampleRate, channels, data));
        return path;
    }

    private String content(String format, int sampleRate, int channels, String data) {
        return "SAMPLEMEDIA/1\nformat=" + format + "\nsampleRate=" + sampleRate
                + "\nchannels=" + channels + "\ndata=" + data + "\n";
    }

    private Path nextPath() {
        return directory.resolve("case-" + ++sequence + ".media");
    }

    private void equal(String name, Object expected, Object actual) {
        if (!expected.equals(actual)) {
            throw new AssertionError(name + ": expected " + expected + ", received " + actual);
        }
        pass(name);
    }

    private void pass(String name) {
        passed++;
        System.out.println("PASS: " + name);
    }
}
