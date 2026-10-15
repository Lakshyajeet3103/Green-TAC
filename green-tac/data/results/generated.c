#include <stdio.h>

int program(void) {
    int a = 0;
    int b = 0;
    int t1 = 0;
    int t10 = 0;
    int t11 = 0;
    int t2 = 0;
    int t3 = 0;
    int t4 = 0;
    int t5 = 0;
    int t6 = 0;
    int t7 = 0;
    int t8 = 0;
    int t9 = 0;
    int x0 = 0;
    int x1 = 0;
    int x2 = 0;
    int x3 = 0;
    int x4 = 0;
    int x5 = 0;
    int x6 = 0;
    int x7 = 0;
    int x8 = 0;
    int x9 = 0;
    int y = 0;
    a = 19;
    b = 9;
    t1 = 28;
    x0 = 28;
    t2 = 47;
    x1 = 47;
    t3 = 66;
    x2 = 66;
    t4 = 85;
    x3 = 85;
    t5 = 104;
    x4 = 104;
    t6 = 123;
    x5 = 123;
    t7 = 142;
    x6 = 142;
    t8 = 161;
    x7 = 161;
    t9 = 180;
    x8 = 180;
    t10 = 199;
    x9 = 199;
    t11 = 398;
    y = 398;
    return 0;
}

int main(void){
    int rc = 0;
    for (int i = 0; i < 50; ++i) rc |= program();
    return rc;
}
