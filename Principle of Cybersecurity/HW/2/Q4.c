#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    int diff, size = 16;
    char *buf1, *buf2, *buf3;
    buf1 = (char *)malloc(size);
    buf2 = (char *)malloc(size + 8);
    buf3 = (char *)malloc(size + 16);
    diff = buf3 - buf1;
    printf("DIFF : %d\n", diff);
    memset(buf2, '1', size + 8);
    printf("BEFORE: buf2 = %s\n", buf2);
    memset(buf3, '2', size + 16);
    printf("BEFORE: buf3 = %s\n", buf3);
    memset(buf1, 'a', diff);
    printf("AFTER: buf1 = %s\n", buf1);
    return 0;
}   