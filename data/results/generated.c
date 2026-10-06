#include <stdio.h>

int program(void) {
    int t1 = 0;
    int t10 = 0;
    int t2 = 0;
    int t3 = 0;
    int t4 = 0;
    int t5 = 0;
    int t6 = 0;
    int t7 = 0;
    int t8 = 0;
    int t9 = 0;
    int x = 0;
    int y = 0;
    int z = 0;
    x = 3;
    t1 = 240;
    y = 240;
    t2 = 240;
    z = 240;
    t3 = 765;
    y = 765;
    t4 = 765;
    z = 765;
    t5 = 243;
    y = 243;
    t6 = 243;
    z = 243;
    t7 = 646;
    y = 646;
    t8 = 646;
    z = 646;
    t9 = 1560;
    y = 1560;
    t10 = 1560;
    z = 1560;
    return 0;
}

int main(void){
    int rc = 0;
    for (int i = 0; i < 2; ++i) rc |= program();
    return rc;
}
