"""Planted cases for analysis/drift.py (specs/SPEC_drift.md, instrument check 1): 10 texts with planted non-Latin passages that
the script detector must flag at the planted token, 10 texts it must not flag; and planted repeats, loops and phrases.

    uv run --no-project --with numpy --with tokenizers python -m studies.rlneurons.analysis.drift_test
"""
from studies.rlneurons.analysis import drift as D

CLEAN = ("Okay, so I need to find the number of ordered pairs $(a, b)$ with $a^2 + b^2 = 2025$.\n\nFirst, note that $2025 = 45^2$, so we "
         "want lattice points on a circle of radius 45. Let me factor: $45 = 3^2 \\cdot 5$. The prime 5 is congruent to 1 mod 4, so "
         "$r_2(n) = 4(d_1(n) - d_3(n))$.\n\n") + "".join(
    f"Step {k}: consider the case $a = {k}$. Then $b^2 = 2025 - {k * k} = {2025 - k * k}$, which is {'not ' if k % 7 else ''}a perfect square, "
    f"so this case gives {'no' if k % 7 else 'two'} solutions.\n" for k in range(1, 45)) + "\nSo the total is $\\boxed{12}$.\n"

PLANT = {
    "chinese": "我们需要重新考虑这个问题。首先，注意到圆上的格点数等于四倍的因子差。因此答案应该是十二。",
    "chinese_short": "因此，答案是十二",
    "chinese_in_math": "所以 $a = 27$，那么 $b = 36$，验证：$27^2 + 36^2 = 2025$，成立。",
    "japanese": "ここで問題をもう一度考え直してみましょう。円周上の格子点の数を数えます。",
    "korean": "이제 문제를 다시 생각해 봅시다. 원 위의 격자점의 개수를 세어야 합니다.",
    "russian": "Теперь рассмотрим задачу заново. Число целых точек на окружности равно двенадцати.",
    "arabic": "لننظر إلى المسألة مرة أخرى. عدد النقاط الصحيحة على الدائرة يساوي اثني عشر.",
    "hindi": "अब हम इस प्रश्न पर फिर से विचार करते हैं। वृत्त पर बिंदुओं की संख्या बारह है।",
    "thai": "ตอนนี้เรามาพิจารณาปัญหานี้อีกครั้ง จำนวนจุดบนวงกลมเท่ากับสิบสอง",
    "mixed": "Wait, 让我重新检查 the case a = 27: 这里 b 应该是 36, 没错。",
}
NEGATIVE = {
    "clean": "",
    "latex": "We have $\\alpha + \\beta = \\frac{\\pi}{2}$ and $\\sum_{k=1}^{n} \\binom{n}{k} = 2^n - 1$, so $\\theta \\in \\mathbb{R}$.",
    "greek_unicode": "Let α, β, γ be the angles, with α + β + γ = π and Δ = b² − 4ac ≥ 0; then λ₁ ≤ μ ≤ σ, and Σ θ_k = 2π, φ(n) = Ω(ω).",
    "diacritics": "By the Erdős–Szekeres theorem, Poincaré's lemma, Hölder's and Möbius' results, Łukasiewicz, Čech, Gödel, Fejér, Kőnig, Ångström, Nguyễn.",
    "math_symbols": "For x ∈ ℝ, n ∈ ℕ, z ∈ ℂ: ∀ε > 0 ∃δ, ∫₀¹ f ≤ ∑ aₙ ⊂ ℤ, ℵ₀ < 𝔠, 𝑥 ↦ 𝑓(𝑥), ℓ², ℏ, ∂Ω, ⌊x⌋, √2 ≠ ½, ∞.",
    "fullwidth_punctuation": "The answer is 12，as shown。 （see above） 「quoted」 … — 12！",
    "four_stray_letters": "Here the symbol 中 appears, and later 文, then Ш for the Tate-Shafarevich group, and א for aleph.",
    "emoji_arrows": "So the answer is 12 ✓ ✅ → ⇒ ★ 😀 • ① ② ™ © µ ª º ß þ ð æ œ.",
    "code": "for i in range(45):\n    if (2025 - i*i)**0.5 == int((2025 - i*i)**0.5): print(i)  # naïve façade coöperate",
    "far_apart": "字" + " and then a long stretch of English follows here." * 6 + "字" + " and more English text follows after it." * 7 + "字" + " again English." * 20 + "字 字",
}


def at(clean: str, plant: str, where: float) -> tuple:
    c = clean.index("\n", int(len(clean) * where)) + 1
    return clean[:c] + plant + "\n" + clean[c:], c


def check_scripts():
    for k, (name, plant) in enumerate(PLANT.items()):
        text, c = at(CLEAN, plant, 0.08 * (k + 1))
        ids, offsets = D.encode(text)
        s = D.signs(text, ids, offsets)
        assert len(s["episodes"]) == 1, f"positive {name}: {len(s['episodes'])} episodes, not 1"
        e = s["episodes"][0]
        want = len(D.encode(text[:c])[0])
        assert abs(e["start_tok"] - want) <= 12, f"positive {name}: start token {e['start_tok']}, planted at {want}"
        assert e["start_tok"] <= e["detect_tok"] <= e["end_tok"] <= want + len(D.encode(plant)[0]) + 2, f"positive {name}: {e}"
        assert e["back"] is True, f"positive {name}: English resumes after the plant, back = {e['back']}"
    for name, neg in NEGATIVE.items():
        text, _ = at(CLEAN, neg, 0.5)
        ids, offsets = D.encode(text)
        s = D.signs(text, ids, offsets)
        assert not s["episodes"], f"negative {name}: flagged {s['episodes']}"
    text = CLEAN + PLANT["chinese"] * 30                         # ends in Chinese: no way back
    e = D.signs(text, *D.encode(text))["episodes"]
    assert len(e) == 1 and e[0]["back"] is None
    text = CLEAN + PLANT["chinese"] * 30 + ("\n" + PLANT["chinese_in_math"]) * 40
    e = D.signs(text, *D.encode(text))["episodes"]
    assert len(e) == 1 and e[0]["letters"] > 1000
    print("script detector: 10 planted positives flagged at the planted token, 10 negatives not flagged")


def check_other():
    ids, offsets = D.encode(CLEAN)
    s = D.signs(CLEAN, ids, offsets)
    assert s["loop_tok"] is None and s["wait_end"] == 0 and s["restart_end"] == 0 and s["rep50_end"] < 0.01, s
    loop = CLEAN + "Wait, let me check the sum of the squares again.\nSo b is 36 here.\n" * 400
    ids, offsets = D.encode(loop)
    s = D.signs(loop, ids, offsets)
    n0 = len(D.encode(CLEAN)[0])
    assert s["loop_tok"] is not None and n0 < s["loop_tok"] < n0 + 3000, (s["loop_tok"], n0)
    assert s["rep50"][-1] > 0.5 and s["rep50"][0] < 0.01, s["rep50"]         # the first 1,000 tokens are the clean text
    assert s["wait_end"] == 400 and s["wait"][0] == 0 and s["wait"][-1] > 300
    text = CLEAN + "Hmm. Let me start over.\n" + CLEAN.replace("Step", "Case") + "This is getting too complicated. Maybe try a different approach.\n"
    s = D.signs(text, *D.encode(text))
    assert s["restart_end"] == 3 and s["wait_end"] == 0, s["restart_end"]
    assert s["rep50_end"] < 0.05, s["rep50_end"]                             # a rewritten copy (Step -> Case) is not a repeat of 50 tokens
    text = CLEAN + CLEAN
    s = D.signs(text, *D.encode(text))
    assert 0.4 < s["rep50_end"] < 0.55, s["rep50_end"]                       # an exact copy: the second half repeats
    print("loop rule A, repeated windows, wait and restart phrases: planted cases found, clean text has none")


if __name__ == "__main__":
    check_scripts()
    check_other()
