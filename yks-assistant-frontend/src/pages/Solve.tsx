import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { ImageUploader } from "@/components/solve/ImageUploader";
import { SolveStep } from "@/components/solve/SolveStepper";
import { SolutionDisplay } from "@/components/solve/SolutionDisplay";
import { Button } from "@/components/ui/button";
import { Sparkles, History as HistoryIcon } from "lucide-react";
import { ChatBox } from "@/components/chat/ChatBox";
import { solveQuestion } from "@/lib/api";
import { toast } from "sonner";

// Mock solution data
const mockSolution = {
  steps: [
    { step: 1, content: "Verilen fonksiyonu analiz edelim: f(x) = 2x + 3" },
    { step: 2, content: "x = 4 değerini fonksiyona yerleştirelim" },
    { step: 3, content: "f(4) = 2(4) + 3 = 8 + 3 = 11" },
    { step: 4, content: "Sonuç olarak f(4) = 11 bulunur" },
  ],
  finalAnswer: "C",
  topic: "Fonksiyonlar",
  difficulty: "Orta",
};

export default function Solve() {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<SolveStep>("upload");
  const [solution, setSolution] = useState<typeof mockSolution | null>(null);

  useEffect(() => {
    const historyState = location.state as { fromHistory?: boolean; item?: any };
    if (historyState?.fromHistory && historyState.item) {
      if (historyState.item.type === "solve") {
        setSolution(mockSolution);
        setCurrentStep("complete");
        setSelectedImage("https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=800&q=80");
        toast.success("Geçmiş çözüm yüklendi.");
      }
    }
  }, [location.state]);

  const handleImageSelect = (file: File | null, preview: string | null) => {
    setSelectedFile(file);
    setSelectedImage(preview);

    if (file) {
      simulateSolving(file);
    } else {
      setCurrentStep("upload");
      setSolution(null);
    }
  };

  const simulateSolving = async (file: File) => {
    setCurrentStep("extract");
    setSolution(null); // Reset previous solution

    try {
      const data = await solveQuestion(file);

      if (data.status === "error") {
        throw new Error(data.message);
      }

      const solveData = data.solution;
      setCurrentStep("solve");

      const formattedSolution = {
        steps: solveData.steps.map((s: string, i: number) => ({ step: i + 1, content: s })),
        finalAnswer: solveData.final_answer,
        topic: data.extracted?.topic_hint || "Karma",
        difficulty: "Orta",
      };

      setCurrentStep("complete");
      setSolution(formattedSolution);
    } catch (error) {
      console.error("Solve failed:", error);
      toast.error("Soru çözülürken bir hata oluştu.");
      setCurrentStep("upload");
      setSelectedFile(null);
      setSelectedImage(null);
    }
  };

  const handleGenerateSimilar = () => {
    navigate("/generate", {
      state: {
        prefill: {
          topic: solution?.topic,
          difficulty: solution?.difficulty
        }
      }
    });
  };

  return (
    <div className="h-[calc(100vh-8rem)]">
      <ChatBox
        title="Soru Çözüm Asistanı"
        placeholder={selectedImage ? "Bu çözümü açıklamamı ister misin?" : "Soru fotoğrafını buraya yükleyebilirsin."}
        className="h-full"
        headerAction={
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/history")}
            className="text-xs gap-2 hover:bg-primary/10 hover:text-primary transition-all"
          >
            <HistoryIcon className="w-3 h-3" />
            Geçmiş Sohbetler
          </Button>
        }
        context={{
          type: "solve",
          status: currentStep,
          solution: solution
        }}
      >
        <div className="p-4 space-y-4">
          <ImageUploader
            onImageSelect={handleImageSelect}
            selectedImage={selectedImage}
          />

          {(currentStep === "extract" || currentStep === "solve") && (
            <div className="flex flex-col items-center justify-center py-8 space-y-4 animate-in fade-in duration-300">
              <div className="relative">
                <div className="w-12 h-12 rounded-full border-2 border-primary/20 border-t-primary animate-spin" />
                <Sparkles className="absolute inset-0 m-auto w-5 h-5 text-primary animate-pulse" />
              </div>
              <p className="text-sm font-medium text-foreground animate-pulse">
                {currentStep === "extract" ? "Soru okunuyor..." : "Çözüm hazırlanıyor..."}
              </p>
            </div>
          )}

          {solution && currentStep === "complete" && (
            <div className="animate-in fade-in slide-in-from-top-4 duration-500">
              <SolutionDisplay
                steps={solution.steps}
                finalAnswer={solution.finalAnswer}
                topic={solution.topic}
                difficulty={solution.difficulty}
                onGenerateSimilar={handleGenerateSimilar}
              />
            </div>
          )}

          {!selectedImage && (
            <div className="text-center py-4 border-t border-border/50 mt-4">
              <p className="text-xs text-muted-foreground mb-3">
                veya direkt soru üret
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate("/generate")}
                className="gap-2 bg-background/50 hover:bg-primary/10 hover:border-primary/50 hover:text-primary transition-all duration-300"
              >
                <Sparkles className="w-3 h-3" />
                Soru Üret
              </Button>
            </div>
          )}
        </div>
      </ChatBox>
    </div>
  );
}
