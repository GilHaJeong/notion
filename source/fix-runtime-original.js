(function attachRuntime(root, factory) {
  const runtime = factory();

  if (typeof module === "object" && module.exports) {
    module.exports = runtime;
  }

  root.OratorioRuntime = runtime;
})(typeof globalThis === "object" ? globalThis : this, function createRuntime() {
  const validParts = new Set(["S", "A", "T", "B"]);
  const knownSongs = {
    6: { title: "첫 번째 에베소 교회", segment: "76~80" },
    9: { title: "두 번째 서머나 교회", segment: "153~156" }
  };
  const readiness = {
    ready: new Set([2, 3, 4]),
    nearly_stable: new Set([5, 12]),
    repeating: new Set([6, 9, 10, 11]),
    listening: new Set([1, 7, 8])
  };

  function normalizePart(value) {
    return validParts.has(value) ? value : "none";
  }

  function songStatus(number) {
    return Object.entries(readiness).find(([, numbers]) => numbers.has(number))?.[0] || "not_started";
  }

  function buildPublicSongs() {
    return Array.from({ length: 20 }, (_, index) => {
      const number = index + 1;
      const known = knownSongs[number] || {};

      return {
        id: `NO${String(number).padStart(2, "0")}`,
        no: number,
        title: known.title || "정본 제목 확인 필요",
        status: songStatus(number),
        needsFocus: number === 6 || number === 9,
        segment: known.segment || null
      };
    });
  }

  function practiceActionLabel(measure) {
    return measure ? `${measure}마디 연습하기` : "처음부터 연습하기";
  }

  function textureFor(screenId, part) {
    if (screenId !== "first_run_part_select") return null;
    if (part === "T" || part === "B") return "dak";
    if (part === "S" || part === "A") return "laid";
    return "cloud";
  }

  return Object.freeze({
    buildPublicSongs,
    normalizePart,
    practiceActionLabel,
    textureFor
  });
});
