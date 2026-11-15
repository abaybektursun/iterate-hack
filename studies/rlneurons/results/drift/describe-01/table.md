# Drift Q1: switches to a non-Latin script (attempt 0 of every sample; an episode = at least 5 non-Latin letters within 200 characters of each other)

| Cell | Samples | With a switch | Cap hits | Cap hits with a switch | Cap hits with > 20 Chinese characters | Finished with a switch | Switched: right | First switch at token: quartiles | Before 4,000 / 8,000 | First episode: back to English yes / no / text ends | Non-Latin share of letters after the switch: quartiles | Letters by script |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hard328_sft | 1312 | 156 | 378 | 99 | 86 | 57 | 39 | [10733, 13589, 15048] | 16 / 24 | 135 / 2 / 19 | [0.012, 0.042, 0.073] | {'CJK': 40579, 'CYRILLIC': 369, 'HANGUL': 180, 'HIRAGANA': 77, 'ARABIC': 62, 'KATAKANA': 9, 'THAI': 6, 'DEVANAGARI': 3, 'TELUGU': 2, 'MALAYALAM': 1, 'TAMIL': 1} |
| hard328_rl | 1312 | 12 | 114 | 3 | 1 | 9 | 1 | [4512, 12145, 13884] | 3 / 5 | 12 / 0 / 0 | [0.001, 0.006, 0.025] | {'CJK': 1010, 'HANGUL': 30, 'ARABIC': 19, 'CYRILLIC': 12, 'HIRAGANA': 2, 'THAI': 2} |
| hard328_base | 1312 | 9 | 286 | 5 | 2 | 4 | 0 | [11111, 12173, 13132] | 1 / 2 | 5 / 1 / 3 | [0.006, 0.008, 0.072] | {'CJK': 2996, 'HIRAGANA': 1225, 'KATAKANA': 699, 'CYRILLIC': 77, 'ARABIC': 11, 'HANGUL': 9, 'THAI': 5, 'TAMIL': 4, 'ARMENIAN': 3, 'DEVANAGARI': 2} |
| fresh_sft | 544 | 104 | 248 | 76 | 66 | 28 | 14 | [11353, 13583, 15121] | 5 / 15 | 87 / 5 / 12 | [0.024, 0.042, 0.08] | {'CJK': 30903, 'CYRILLIC': 378, 'HANGUL': 100, 'ARABIC': 76, 'HIRAGANA': 65, 'KATAKANA': 7, 'THAI': 5, 'HEBREW': 2, 'DEVANAGARI': 1, 'BENGALI': 1, 'GURMUKHI': 1} |
| fresh_rl | 544 | 9 | 84 | 4 | 3 | 5 | 0 | [12955, 13379, 14416] | 0 / 1 | 8 / 0 / 1 | [0.008, 0.021, 0.05] | {'CJK': 1519, 'HIRAGANA': 203, 'KATAKANA': 63, 'CYRILLIC': 40, 'ARABIC': 17, 'DEVANAGARI': 16, 'HANGUL': 10, 'THAI': 4, 'HEBREW': 3, 'BENGALI': 2, 'TAMIL': 2, 'MALAYALAM': 1, 'GURMUKHI': 1, 'GUJARATI': 1, 'TELUGU': 1} |
| fresh_base | 544 | 6 | 219 | 1 | 0 | 5 | 1 | [3488, 6029, 11584] | 2 / 4 | 4 / 1 / 1 | [0.004, 0.023, 0.048] | {'CJK': 1952, 'CYRILLIC': 85, 'GURMUKHI': 36} |
| math500_sft | 2000 | 61 | 93 | 19 | 17 | 42 | 34 | [3750, 10249, 13147] | 16 / 27 | 57 / 0 / 4 | [0.004, 0.034, 0.068] | {'CJK': 12908, 'CYRILLIC': 122, 'HANGUL': 53, 'ARABIC': 45, 'HIRAGANA': 30, 'KATAKANA': 5, 'DEVANAGARI': 3, 'THAI': 3, 'TAMIL': 2, 'HEBREW': 2} |
| cap32_sft | 328 | 83 | 2 | 1 | 1 | 82 | 18 | [13971, 16774, 19499] | 0 / 2 | 80 / 3 / 0 | [0.021, 0.043, 0.07] | {'CJK': 39600, 'CYRILLIC': 366, 'HANGUL': 236, 'HIRAGANA': 88, 'ARABIC': 63, 'THAI': 6, 'DEVANAGARI': 4, 'KATAKANA': 3, 'TAMIL': 2, 'GURMUKHI': 1} |

## Problem or sample: pairs of samples of one problem that both switch (10,000 permutations)

| Cell | Problems with 0 / 1 / 2 / 3 / 4 switched samples | Pairs observed | Null A (flags over all samples): mean, p | Null B (flags over cap hits only): mean, p |
|---|---|---|---|---|
| hard328_sft | 226 / 65 / 23 / 11 / 3 | 74 | 27.8, 0.0001 | 48.9, 0.0001 |
| fresh_sft | 75 / 36 / 12 / 8 / 5 | 66 | 29.6, 0.0001 | 41.9, 0.0001 |
| math500_sft | 450 / 43 / 5 / 0 / 2 | 17 | 2.7, 0.0001 | 10.1, 0.0066 |
