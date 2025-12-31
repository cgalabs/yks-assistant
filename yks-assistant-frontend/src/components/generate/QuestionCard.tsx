import { useState } from "react";
import { ThumbsUp, ThumbsDown, Eye, EyeOff, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { LatexRenderer } from "@/components/ui/LatexRenderer";

interface QuestionCardProps {
  question: {
    id: string;
    text: string;
    options: { label: string; text: string }[];
    answer: string;
    solution: string | string[];
  };
  index: number;
}

export function QuestionCard({ question, index }: QuestionCardProps) {
  const [showAnswer, setShowAnswer] = useState(false);
  const [showSolution, setShowSolution] = useState(false);
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);

  return (
    <div
      className="bg-card rounded-2xl border border-border p-5 shadow-sm animate-slide-up"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      {/* Question Number */}
      <div className="flex items-center justify-between mb-4">
        <span className="px-3 py-1 gradient-primary text-primary-foreground rounded-full text-xs font-medium">
          Soru {index + 1}
        </span>
        <div className="flex gap-1">
          <Button
            variant={feedback === "up" ? "success" : "ghost"}
            size="icon-sm"
            onClick={() => setFeedback("up")}
          >
            <ThumbsUp className="w-3.5 h-3.5" />
          </Button>
          <Button
            variant={feedback === "down" ? "destructive" : "ghost"}
            size="icon-sm"
            onClick={() => setFeedback("down")}
          >
            <ThumbsDown className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      {/* Question Text */}
      <div className="text-foreground mb-4 leading-relaxed whitespace-pre-wrap">
        <LatexRenderer>{question.text}</LatexRenderer>
      </div>

      {/* Options */}
      <div className="space-y-2 mb-4">
        {question.options.map((option) => (
          <div
            key={option.label}
            className={cn(
              "flex items-start gap-3 p-3 rounded-xl border transition-all",
              showAnswer && option.label === question.answer
                ? "border-success bg-success/10"
                : "border-border bg-secondary/30"
            )}
          >
            <span
              className={cn(
                "flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium",
                showAnswer && option.label === question.answer
                  ? "bg-success text-success-foreground"
                  : "bg-secondary text-muted-foreground"
              )}
            >
              {option.label}
            </span>
            <span className="text-sm text-foreground pt-0.5">
              <LatexRenderer>{option.text}</LatexRenderer>
            </span>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowAnswer(!showAnswer)}
          className="flex-1 gap-2"
        >
          {showAnswer ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          {showAnswer ? "Gizle" : "Cevabı Göster"}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowSolution(!showSolution)}
          className="gap-2"
        >
          {showSolution ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          Çözüm
        </Button>
      </div>

      {/* Solution */}
      {showSolution && (
        <div className="mt-4 pt-4 border-t border-border animate-fade-in">
          <h4 className="text-sm font-medium text-foreground mb-3">Çözüm:</h4>
          <div className="space-y-2">
            {Array.isArray(question.solution) ? (
              question.solution.map((step, i) => (
                <div key={i} className="flex gap-2 text-sm text-muted-foreground">
                  <span className="text-primary font-medium">{i + 1}.</span>
                  <span>
                    <LatexRenderer>{step}</LatexRenderer>
                  </span>
                </div>
              ))
            ) : (
              <div className="text-sm text-muted-foreground whitespace-pre-wrap">
                <LatexRenderer>{question.solution}</LatexRenderer>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
