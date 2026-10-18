package media.subsystem;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.stream.Collectors;

public final class MediaWriter {
    public Path write(EncodedMedia media, Path destination) throws IOException {
        Path target = destination.toAbsolutePath().normalize();
        if (Files.exists(target)) {
            throw new java.nio.file.FileAlreadyExistsException(target.toString());
        }
        String data = Arrays.stream(media.values())
                .mapToObj(Integer::toString)
                .collect(Collectors.joining(","));
        String content = String.join("\n", "SAMPLEMEDIA/1", "format=" + media.format(),
                "sampleRate=" + media.sampleRate(), "channels=" + media.channels(), "data=" + data) + "\n";
        Path temporary = Files.createTempFile(target.getParent(), ".conversion-", ".tmp");
        try {
            Files.writeString(temporary, content, StandardCharsets.UTF_8);
            return Files.move(temporary, target);
        } finally {
            Files.deleteIfExists(temporary);
        }
    }
}
