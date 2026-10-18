import java.nio.file.InvalidPathException;
import java.nio.file.Path;
import media.ConversionException;
import media.MediaConversionFacade;

public final class Main {
    public static void main(String[] args) {
        if (args.length != 3) {
            System.err.println("Usage: java -cp out Main <source> <pcm|delta> <destination>");
            System.exit(2);
        }
        try {
            MediaConversionFacade converter = new MediaConversionFacade();
            Path result = converter.convert(Path.of(args[0]), args[1], Path.of(args[2]));
            System.out.println("Converted to mono " + args[1] + ": " + result);
        } catch (ConversionException | InvalidPathException exception) {
            System.err.println(exception.getMessage());
            System.exit(1);
        }
    }
}
