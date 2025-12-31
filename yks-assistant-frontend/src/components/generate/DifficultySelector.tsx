import { cn } from "@/lib/utils";

const difficulties = [
  { id: "easy", label: "Kolay", color: "text-success" },
  { id: "medium", label: "Orta", color: "text-warning" },
  { id: "hard", label: "Zor", color: "text-destructive" },
];

interface DifficultySelectorProps {
  selected: string;
  onSelect: (difficulty: string) => void;
}

export function DifficultySelector({ selected, onSelect }: DifficultySelectorProps) {
  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-foreground">Zorluk</label>
      <div className="flex gap-2">
        {difficulties.map((diff) => (
          <button
            key={diff.id}
            onClick={() => onSelect(diff.id)}
            className={cn(
              "flex-1 py-3 px-4 rounded-xl border-2 font-medium text-sm transition-all duration-200",
              selected === diff.id
                ? "border-primary bg-primary/10 text-primary shadow-md"
                : "border-border bg-card text-muted-foreground hover:border-primary/30"
            )}
          >
            {diff.label}
          </button>
        ))}
      </div>
    </div>
  );
}
