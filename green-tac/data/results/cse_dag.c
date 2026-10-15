#include <stdio.h>

int program(void) {
    int a = 0;
    int b = 0;
    int t1 = 0;
    int t3 = 0;
    int t5 = 0;
    int t6 = 0;
    int t7 = 0;
    int x = 0;
    int y = 0;
    t1 = a + b;
    t3 = t1 * t1;
    t5 = t3 + t1;
    x = t5;
    t6 = a + b;
    t7 = t6 * 2;
    y = t7;
    return 0;
}

int main(void){
    int rc = 0;
    for (int i = 0; i < 1; ++i) rc |= program();
    return rc;
}
