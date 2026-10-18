package media.subsystem;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public final class MetadataReader {
    public EncodedMedia read(Path source) throws IOException {
        List<String> lines = Files.readAllLines(source, StandardCharsets.UTF_8);
        if (lines.size() != 5 || !lines.get(0).equals("SAMPLEMEDIA/1")) {
            throw new IllegalArgumentException("Expected a five-line SAMPLEMEDIA/1 file.");
        }
        String format = value(lines.get(1), "format");
        int sampleRate = Integer.parseInt(value(lines.get(2), "sampleRate"));
        int channels = Integer.parseInt(value(lines.get(3), "channels"));
        String[] tokens = value(lines.get(4), "data").split(",", -1);
        int[] values = new int[tokens.length];
        for (int index = 0; index < tokens.length; index++) {
            values[index] = Integer.parseInt(tokens[index].trim());
        }
        return new EncodedMedia(format, sampleRate, channels, values);
    }

    private String value(String line, String key) {
        String prefix = key + "=";
        if (!line.startsWith(prefix) || line.length() == prefix.length()) {
            throw new IllegalArgumentException("Missing or empty field: " + key);
        }
        return line.substring(prefix.length()).trim();
    }
}
