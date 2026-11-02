#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("Hello from C!\n");

    if (argc > 1) {
        printf("Argument: %s\n", argv[1]);
    }

    return 0;
}