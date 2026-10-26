a = 6; b = 3; c = 0;

p = (a = a + b) * (b = b - 1)
    - -(a % 4) * 5 / (1 + 1);

q = !(p > 25 || c) && (c = p % 7) == 6
    || (b = 50);

r = (a != 9 || (b = 100))
    && ((c = c + 1) < 0 || (c = c + 10)) > 10;

s = (a < b)
    + (c > 5) * 2
    + (p >= 17 && r) * 4
    + !(q && !r) * 8;

z = y = (p - s) % 5 + - - c / 2;
k = 0 && (1 % (b - 100)) || 1 || 1 / 0;
m = (z - 3 * y) % 7;
n = (z - 3 * y) / 7;

t = (a == 9) + (b == 100) + (c == 17)
    + (y == z) + (k && m < 0) * 10;

score = 0;
guard = 0;

if ((p >= 20 && q) || (!r && k)) {
    if ((a == 9) && ((guard = guard + 1) > 0)) {
        score = score + (p - s) * 2;
    } else {
        score = -100;
    }
} else if (!(m >= 0) && n <= 0) {
    score = score + 7;
} else {
    score = score - 7;
}

i = 0;
hits = 0;
acc = 0;

while ((i = i + 1) <= 5 && !(hits > 10)) {
    j = 0;

    while ((j = j + 1) <= 3) {
        value = (i * j + p - s) % 7;

        if (value % 2 == 0 && (i != j || value == 0)) {
            acc = acc + value;
            hits = hits + 1;
        } else if (!(value < 3) || (i == j && value != 0)) {
            acc = acc - (value / 2);
        } else {
            acc = acc + 1;
        }
    }
}

if (hits > 0)
    if (acc >= 0 && !(score < 0))
        branch = 1;
    else
        branch = 2;
else
    branch = 3;

safe = (b == 100 || (guard = guard + 100))
    && !(false && (1 / 0));

skipped = false && (guard = 999)
    || true || (1 % 0);

u = v = (acc + score) * (branch != 3)
    + (safe && skipped) * 10;

final = u + v + hits
    + (guard == 1) * 100
    + !!k * 1000;