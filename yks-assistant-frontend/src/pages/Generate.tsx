import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SubjectSelector } from "@/components/generate/SubjectSelector";
import { TopicSelector } from "@/components/generate/TopicSelector";
import { DifficultySelector } from "@/components/generate/DifficultySelector";
import { QuestionCard } from "@/components/generate/QuestionCard";
import { generateQuestions } from "@/lib/api";
import { toast } from "sonner";

// Mock generated questions
const mockQuestions = [
  {
    id: "1",
    text: "f(x) = 3x - 5 fonksiyonu için f(4) değeri kaçtır?",
    options: [
      { label: "A", text: "5" },
      { label: "B", text: "7" },
      { label: "C", text: "9" },
      { label: "D", text: "11" },
      { label: "E", text: "13" },
    ],
    answer: "B",
    solution: [
      "f(x) = 3x - 5 fonksiyonunda x yerine 4 yazalım",
      "f(4) = 3(4) - 5",
      "f(4) = 12 - 5 = 7",
    ],
  },
  {
    id: "2",
    text: "g(x) = x² + 2x fonksiyonu için g(-1) değeri kaçtır?",
    options: [
      { label: "A", text: "-3" },
      { label: "B", text: "-1" },
      { label: "C", text: "0" },
      { label: "D", text: "1" },
      { label: "E", text: "3" },
    ],
    answer: "B",
    solution: [
      "g(x) = x² + 2x fonksiyonunda x yerine -1 yazalım",
      "g(-1) = (-1)² + 2(-1)",
      "g(-1) = 1 - 2 = -1",
    ],
  },
];

export default function Generate() {
  const location = useLocation();
  const prefill = location.state?.prefill;

  const [subject, setSubject] = useState<string | null>(null);
  const [topic, setTopic] = useState<string | null>(prefill?.topic?.toLowerCase() || null);
  const [difficulty, setDifficulty] = useState(prefill?.difficulty?.toLowerCase() === "orta" ? "medium" : "easy");
  const count = 1;
  const [isGenerating, setIsGenerating] = useState(false);
  const [questions, setQuestions] = useState<typeof mockQuestions | null>(null);

  useEffect(() => {
    if (location.state?.prefill) {
      setSubject("tyt-matematik");
      setTopic(location.state.prefill.topic);
      setDifficulty(location.state.prefill.difficulty);
    } else if (location.state?.fromHistory && location.state.item) {
      setSubject("tyt-matematik");
      // Split the topic if it contains extra info (like in Solve mock items)
      const topicLabel = location.state.item.topic.split(" - ")[0];
      setTopic(topicLabel);
      toast.success("Geçmiş üretim ayarları yüklendi.");
    }
  }, [location.state]);

  const handleGenerate = async () => {
    if (!topic) return;

    setIsGenerating(true);
    setQuestions(null);

    try {
      const data = await generateQuestions(topic, difficulty);

      // Map backend response: data.data.questions is an array of GeneratedQuestion
      const formattedQuestions = data.data.questions.map((q: any, i: number) => ({
        id: String(i + 1),
        text: q.problem_text,
        options: Object.entries(q.choices).map(([label, text]) => ({ label, text: String(text) })),
        answer: q.correct_answer,
        solution: q.solution,
      }));

      setQuestions(formattedQuestions);
    } catch (error) {
      console.error("Generate failed:", error);
      toast.error("Soru üretilirken bir hata oluştu.");
    } finally {
      setIsGenerating(false);
    }
  };

  const canGenerate = topic !== null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-foreground mb-1">Soru Üret</h1>
        <p className="text-muted-foreground text-sm">
          Konu ve zorluk seç, yapay zeka üretsin
        </p>
      </div>

      {/* Selectors */}
      {!questions && (
        <div className="space-y-5 animate-fade-in">
          <SubjectSelector selected={subject} onSelect={setSubject} />
          {subject && (
            <div className="animate-in fade-in slide-in-from-top-2 duration-500">
              <TopicSelector selected={topic} onSelect={setTopic} />
            </div>
          )}
          <DifficultySelector selected={difficulty} onSelect={setDifficulty} />

          <Button
            onClick={handleGenerate}
            disabled={!canGenerate || isGenerating}
            className="w-full gap-2 bg-primary/90 hover:bg-primary transition-all duration-300 shadow-glow hover:shadow-glow-lg hover:-translate-y-0.5"
            size="lg"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Üretiliyor...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Soru Üret
              </>
            )}
          </Button>
        </div>
      )}

      {/* Generated Questions */}
      {questions && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-foreground">
              Üretilen Sorular ({questions.length})
            </h2>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setQuestions(null)}
            >
              Yeniden Üret
            </Button>
          </div>

          {questions.map((q, index) => (
            <QuestionCard key={q.id} question={q} index={index} />
          ))}
        </div>
      )}
    </div>
  );
}
