import java.io.*;
import java.nio.file.*;
import java.util.*;

public class McfunctionProcessor {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: McfunctionProcessor <input_file> <output_file>");
            System.exit(1);
        }
        
        String inputFile = args[0];
        String outputFile = args[1];
        
        try {
            processFile(inputFile, outputFile);
        } catch (IOException e) {
            System.err.println("Error processing file: " + e.getMessage());
            System.exit(1);
        }
    }
    
    private static void processFile(String inputPath, String outputPath) throws IOException {
        List<String> inputLines = Files.readAllLines(Paths.get(inputPath));
        List<String> processedLines = processLines(inputLines);
        
        // 确保输出目录存在
        Path outputFile = Paths.get(outputPath);
        Path outputDir = outputFile.getParent();
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
                // 移除反斜杠并添加到当前命令
                String lineWithoutBackslash = trimmed.substring(0, trimmed.length() - 1).trim();
                if (currentCommand.length() > 0) {
                    currentCommand.append(" ");
                }
                currentCommand.append(lineWithoutBackslash);
            } else {
                // 普通行，完成当前命令
                if (currentCommand.length() > 0) {
                    currentCommand.append(" ");
                }
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
        if (currentCommand.length() > 0) {
            String finalCommand = currentCommand.toString().trim();
            if (!finalCommand.isEmpty()) {
                result.add(finalCommand);
            }
        }
        
        return result;
    }
}