import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export type SolveStep = "upload" | "extract" | "solve" | "complete";

interface SolveStepperProps {
  currentStep: SolveStep;
}

const steps = [
  { id: "upload", label: "Yükle" },
  { id: "extract", label: "Oku" },
  { id: "solve", label: "Çöz" },
] as const;

export function SolveStepper({ currentStep }: SolveStepperProps) {
  const getStepState = (stepId: SolveStep) => {
    const stepOrder: SolveStep[] = ["upload", "extract", "solve", "complete"];
    const currentIndex = stepOrder.indexOf(currentStep);
    const stepIndex = stepOrder.indexOf(stepId);

    if (currentStep === "complete" || stepIndex < currentIndex) return "completed";
    if (stepIndex === currentIndex) return "active";
    return "pending";
  };

  return (
    <div className="flex items-center justify-center gap-2 py-4">
      {steps.map((step, index) => {
        const state = getStepState(step.id);
        
        return (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center gap-1.5">
              <div
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300",
                  state === "completed" && "gradient-primary text-primary-foreground shadow-md",
                  state === "active" && "gradient-primary text-primary-foreground shadow-glow animate-pulse-slow",
                  state === "pending" && "bg-secondary text-muted-foreground"
                )}
              >
                {state === "completed" ? (
                  <Check className="w-4 h-4" />
                ) : state === "active" ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  index + 1
                )}
              </div>
              <span
                className={cn(
                  "text-xs font-medium transition-colors",
                  state === "pending" ? "text-muted-foreground" : "text-foreground"
                )}
              >
                {step.label}
              </span>
            </div>
            
            {index < steps.length - 1 && (
              <div
                className={cn(
                  "w-12 h-0.5 mx-2 rounded-full transition-colors duration-300",
                  getStepState(steps[index + 1].id) !== "pending"
                    ? "gradient-primary"
                    : "bg-secondary"
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
