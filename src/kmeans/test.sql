SELECT kmeans(ARRAY[x, y], 3,
        ARRAY[0.0, 0.0, 1.0, 0.5, -1.0, -0.5]) OVER (), x, y
FROM test_xy
LIMIT 10;
