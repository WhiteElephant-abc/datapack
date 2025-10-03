import top.fifthlight.bazel.worker.api.WorkRequest;
import top.fifthlight.bazel.worker.api.Worker;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class McfunctionProcessor extends Worker {
    public static void main(String[] args) throws Exception {
        new McfunctionProcessor().run();
    }

    @Override
    protected int handleRequest(WorkRequest request, PrintWriter out) {
        var args = request.arguments();
        if (args.size() < 2) {
            out.println("Usage: McfunctionProcessor <input_file> <output_file>");
            return 1;
        }

        var inputFile = args.get(0);
        var outputFile = args.get(1);

        try {
            processFile(inputFile, outputFile);
        } catch (IOException e) {
            out.println("Error processing file: " + e.getMessage());
            e.printStackTrace(out);
            return 1;
        }
        return 0;
    }

    private static void processFile(String inputPath, String outputPath) throws IOException {
        var inputLines = Files.readAllLines(Paths.get(inputPath));
        var processedLines = processLines(inputLines);

        // 确保输出目录存在
        var outputFile = Paths.get(outputPath);
        var outputDir = outputFile.getParent();
        if (outputDir != null) {
            Files.createDirectories(outputDir);
        }

        Files.write(outputFile, processedLines);
    }

    private static List<String> processLines(List<String> rawLines) {
        List<String> result = new ArrayList<>();
        StringBuilder currentCommand = new StringBuilder();
        
        for (String line : rawLines) {
            String trimmed = line.trim();
            
            // 跳过空行和注释行
            if (trimmed.isEmpty() || trimmed.startsWith("#")) {
                continue;
            }
            
            // 处理续行（以反斜杠结尾）
            if (trimmed.endsWith("\\")) {
                // 移除反斜杠，严格保留内容
                String lineWithoutBackslash = trimmed.substring(0, trimmed.length() - 1);
                
                // 直接拼接，不添加任何字符
                currentCommand.append(lineWithoutBackslash);
            } else {
                // 普通行，直接拼接
                currentCommand.append(trimmed);
                
                // 添加完整的命令到结果中
                String finalCommand = currentCommand.toString().trim();
                
                if (!finalCommand.isEmpty()) {
                    result.add(finalCommand);
                }
                
                // 重置当前命令
                currentCommand.setLength(0);
            }
        }

        // 处理最后一个可能未完成的命令
        if (!currentCommand.isEmpty()) {
            var finalCommand = currentCommand.toString().trim();
            if (!finalCommand.isEmpty()) {
                result.add(finalCommand);
            }
        }

        return result;
    }
}