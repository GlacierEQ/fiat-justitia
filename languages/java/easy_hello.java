// Java — Easy Example: Deterministic Hello
//
// What: Prints a stable greeting and exits successfully.
// Where: JVM bootstrap, CI smoke, and portable service entrypoints.
// When: Use when the platform contract is the JVM itself.
// Why: Java remains the baseline runtime for enterprise and Android ecosystems.
// How: A single public class with a main method and no external dependencies.

public final class easy_hello {
    public static void main(String[] args) {
        System.out.println("{\"status\":\"VERIFIED\",\"language\":\"java\",\"message\":\"hello-tower\"}");
    }

    private easy_hello() {}
}
