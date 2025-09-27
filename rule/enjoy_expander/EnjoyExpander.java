import com.jfinal.template.Engine;
import com.jfinal.template.Template;
import com.jfinal.template.source.ClassPathSourceFactory;
import com.jfinal.template.source.FileSourceFactory;
import com.jfinal.template.stat.ParseException;
import com.jfinal.kit.Kv;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class EnjoyExpander {
    private static void usage() {
        System.err.println("Usage: EnjoyExpander -I <path> -Dkey=value <input> [-o output]");
        System.exit(1);
    }

    public static void main(String[] args) throws Exception {
        String inputFile = null;
        String outputFile = null;
        String basePath = ".";
        Map<String, String> data = new HashMap<>();

        // Parse args
        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "-I":
                    basePath = args[++i];
                    break;
                case "-D":
                    String[] kv = args[++i].split("=", 2);
                    if (kv.length < 1) {
                        usage();
                    }
                    data.put(kv[0], kv.length > 1 ? kv[1] : "");
                    break;
                case "-o":
                    outputFile = args[++i];
                    break;
                default:
                    if (!args[i].startsWith("-")) {
                        inputFile = args[i];
                    }
            }
        }

        if (inputFile == null) {
            usage();
        }

        // Setup engine
        Engine engine = new Engine();
        engine.setSourceFactory(new FileSourceFactory());
        engine.setBaseTemplatePath(basePath);

        // Load and render
        String inputStr = Files.readString(Paths.get(inputFile));
        Template template = engine.getTemplateByString(inputStr);
        String result = template.renderToString(data);

        Path outputPath = Paths.get(outputFile);
        var baseDir = outputPath.getParent();
        if (baseDir != null) {
            Files.createDirectories(baseDir);
        }

        // Output
        if (outputFile != null) {
            Files.writeString(outputPath, result);
        } else {
            System.out.println(result);
        }
    }
}
