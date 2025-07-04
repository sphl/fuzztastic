#include <stdio.h>

int add(int a, int b) { return a + b; }

int multiply(int x, int y) { return x * y; }

int main() {
    int result1 = add(5, 3);
    int result2 = multiply(4, 7);
    printf("Results: %d, %d\n", result1, result2);
    return 0;
}
