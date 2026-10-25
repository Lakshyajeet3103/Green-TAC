a = 2;
b = 5;
ready = a < b && !(b == 0);
if (ready && (a != 0 || b > 10)) {
    result = 1;
} else if (!ready) {
    result = 2;
} else {
    result = 3;
}
i = 0;
while (i < 5 && ready) {
    i = i + 1;
    ready = i < 3;
}
safe = true || (1 / 0);
