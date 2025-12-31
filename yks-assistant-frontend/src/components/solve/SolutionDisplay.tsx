import { useState } from "react";
import { ThumbsUp, ThumbsDown, Copy, Sparkles, Check, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";

interface SolutionStep {
  step: number;
  content: string;
}

interface SolutionDisplayProps {
  steps: SolutionStep[];
  finalAnswer: string;
  topic?: string;
  difficulty?: string;
  onGenerateSimilar: () => void;
}

export function SolutionDisplay({
  steps,
  finalAnswer,
  topic = "Fonksiyonlar",
  difficulty = "Orta",
  onGenerateSimilar,
}: SolutionDisplayProps) {
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const handleCopy = async () => {
    const text = steps.map((s) => `${s.step}. ${s.content}`).join("\n") + `\n\nCevap: ${finalAnswer}`;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    toast({ title: "Kopyalandı", description: "Çözüm panoya kopyalandı" });
    setTimeout(() => setCopied(false), 2000);
  };

  const handleFeedback = (vote: "up" | "down") => {
    setFeedback(vote);
    toast({
      title: vote === "up" ? "Teşekkürler! 🎉" : "Geri bildirimin için teşekkürler",
      description: vote === "up" ? "Çözüm beğenildi" : "Daha iyi çözümler için çalışıyoruz",
    });
  };

  return (
    <div className="space-y-4 animate-slide-up">
      {/* Topic & Difficulty Tags */}
      <div className="flex gap-2">
        <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-medium">
          {topic}
        </span>
        <span className="px-3 py-1 bg-secondary text-muted-foreground rounded-full text-xs font-medium">
          {difficulty}
        </span>
      </div>

      {/* Solution Steps */}
      <div className="bg-card rounded-2xl border border-border p-5 shadow-sm">
        <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
          <span className="w-6 h-6 rounded-full gradient-primary flex items-center justify-center">
            <Check className="w-3 h-3 text-primary-foreground" />
          </span>
          Çözüm Adımları
        </h3>

        <div className="space-y-3">
          {steps.map((step, index) => (
            <div
              key={step.step}
              className="flex gap-3 animate-fade-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-secondary flex items-center justify-center text-xs font-medium text-muted-foreground">
                {step.step}
              </div>
              <p className="text-sm text-foreground leading-relaxed pt-0.5">
                {step.content}
              </p>
            </div>
          ))}
        </div>

        {/* Final Answer */}
        <div className="mt-5 pt-4 border-t border-border">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Cevap:</span>
            <span className="text-2xl font-bold text-gradient">{finalAnswer}</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <Button
            variant={feedback === "up" ? "success" : "outline"}
            size="icon"
            onClick={() => handleFeedback("up")}
            className={cn(feedback === "up" && "shadow-md")}
          >
            <ThumbsUp className="w-4 h-4" />
          </Button>
          <Button
            variant={feedback === "down" ? "destructive" : "outline"}
            size="icon"
            onClick={() => handleFeedback("down")}
          >
            <ThumbsDown className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={handleCopy}>
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          </Button>
        </div>

        <Button variant="default" onClick={onGenerateSimilar} className="gap-2">
          <Sparkles className="w-4 h-4" />
          Benzer Üret
        </Button>
      </div>
    </div>
  );
}
