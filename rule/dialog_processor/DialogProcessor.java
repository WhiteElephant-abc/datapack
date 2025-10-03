import top.fifthlight.bazel.worker.api.WorkRequest;
import top.fifthlight.bazel.worker.api.Worker;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class DialogProcessor extends Worker {
    public static void main(String[] args) throws Exception {
        new DialogProcessor().run();
    }

    @Override
    protected int handleRequest(WorkRequest request, PrintWriter out) {
        var args = request.arguments();
        if (args.size() < 3) {
            out.println("Usage: DialogProcessor <mcfunction_in> <json_in> <mcfunction_out>");
            return 1;
        }

        var mcfunctionIn = args.get(0);
        var jsonIn = args.get(1);
        var mcfunctionOut = args.get(2);

        try {
            processPair(mcfunctionIn, jsonIn, mcfunctionOut);
        } catch (Exception e) {
            out.println("Error processing dialog pair: " + e.getMessage());
            e.printStackTrace(out);
            return 1;
        }
        return 0;
    }

    private static void processPair(String mcfunctionPath, String jsonPath, String outputPath) throws Exception {
        // Read selector and replacement rules from mcfunction
        var lines = Files.readAllLines(Paths.get(mcfunctionPath));
        
        // 第一行仍然为选择器
        var selector = findSelector(lines);
        if (selector == null || selector.isEmpty()) {
            // Default to @s if not found to keep pipeline functional
            selector = "@s";
        }
        
        // 解析替换规则
        Map<String, String> replacementRules = parseReplacementRules(lines);

        // 先读取JSON并转换为SNBT格式
        var jsonText = Files.readString(Paths.get(jsonPath));
        var snbt = toSnbt(jsonText);
        
        // 在SNBT上应用替换规则
        for (Map.Entry<String, String> rule : replacementRules.entrySet()) {
            snbt = snbt.replace(rule.getKey(), rule.getValue());
        }

        var command = "$dialog show " + selector + " " + snbt;

        var outputFile = Paths.get(outputPath);
        var outputDir = outputFile.getParent();
        if (outputDir != null) {
            Files.createDirectories(outputDir);
        }
        Files.writeString(outputFile, command);
    }

    private static String findSelector(List<String> lines) {
        if (lines.isEmpty()) {
            return null;
        }

        // 只检查第一行
        String firstLine = lines.get(0);
        Pattern p = Pattern.compile("#(.*?)#");
        Matcher m = p.matcher(firstLine);
        if (m.find()) {
            var s = m.group(1).trim();
            if (!s.isEmpty()) {
                return s;
            }
        }
        return null;
    }

    private static Map<String, String> parseReplacementRules(List<String> lines) {
        Map<String, String> rules = new HashMap<>();

        // 跳过第一行（选择器行）
        for (int i = 1; i < lines.size(); i++) {
            String line = lines.get(i).trim();

            // 检查是否是替换规则行（以#开头）
            if (line.startsWith("#") && line.contains(":")) {
                int colonIndex = line.indexOf(':');
                if (colonIndex > 1) { // 确保冒号前有内容
                    String target = line.substring(1, colonIndex).trim();
                    String replacement = line.substring(colonIndex + 1).trim();

                    if (!target.isEmpty()) {
                        rules.put(target, replacement);
                    }
                }
            }
        }

        return rules;
    }

    private static String toSnbt(String json) throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        Object node = mapper.readValue(json, Object.class);
        return buildSnbt(node);
    }

    @SuppressWarnings("unchecked")
    private static String buildSnbt(Object node) {
        if (node == null) {
            return "null";
        }
        if (node instanceof Map) {
            var map = (Map<String, Object>) node;
            var parts = new ArrayList<String>();
            for (var entry : map.entrySet()) {
                String key = entry.getKey();
                String safeKey = isSafeIdentifier(key) ? key : quoteString(key);
                parts.add(safeKey + ":" + buildSnbt(entry.getValue()));
            }
            return "{" + String.join(",", parts) + "}";
        } else if (node instanceof List) {
            var list = (List<Object>) node;
            var parts = new ArrayList<String>();
            for (var item : list) {
                parts.add(buildSnbt(item));
            }
            return "[" + String.join(",", parts) + "]";
        } else if (node instanceof String) {
            // Keep macros like $(...) untouched inside the string
            return quoteString((String) node);
        } else if (node instanceof Number) {
            return node.toString();
        } else if (node instanceof Boolean) {
            return ((Boolean) node) ? "true" : "false";
        }
        // Fallback to quoted string
        return quoteString(String.valueOf(node));
    }

    private static boolean isSafeIdentifier(String s) {
        if (s == null || s.isEmpty()) return false;
        if (!Character.isLetter(s.charAt(0)) && s.charAt(0) != '_') return false;
        for (int i = 1; i < s.length(); i++) {
            char c = s.charAt(i);
            if (!Character.isLetterOrDigit(c) && c != '_') return false;
        }
        return true;
    }

    private static String quoteString(String s) {
        StringBuilder sb = new StringBuilder();
        sb.append('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"': sb.append("\\\""); break;
                case '\\': sb.append("\\\\"); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                default:
                    if (c < 0x20) {
                        String hex = Integer.toHexString(c);
                        sb.append("\\u");
                        for (int k = hex.length(); k < 4; k++) sb.append('0');
                        sb.append(hex);
                    } else {
                        sb.append(c);
                    }
            }
        }
        sb.append('"');
        return sb.toString();
    }
}
