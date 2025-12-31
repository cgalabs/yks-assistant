import { useState } from "react";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";

const counts = [1, 5, 10];

interface CountSelectorProps {
  selected: number;
  onSelect: (count: number) => void;
}

export function CountSelector({ selected, onSelect }: CountSelectorProps) {
  const [customValue, setCustomValue] = useState("");
  const isCustom = !counts.includes(selected) && selected > 0;

  const handleCustomChange = (value: string) => {
    setCustomValue(value);
    const num = parseInt(value, 10);
    if (!isNaN(num) && num > 0 && num <= 50) {
      onSelect(num);
    }
  };

  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-foreground">Soru Sayısı</label>
      <div className="flex gap-2">
        {counts.map((count) => (
          <button
            key={count}
            onClick={() => {
              setCustomValue("");
              onSelect(count);
            }}
            className={cn(
              "flex-1 py-3 px-4 rounded-xl border-2 font-medium text-sm transition-all duration-200",
              selected === count
                ? "border-primary bg-primary/10 text-primary shadow-md"
                : "border-border bg-card text-muted-foreground hover:border-primary/30"
            )}
          >
            {count}
          </button>
        ))}
        <div className="flex-1">
          <Input
            type="number"
            placeholder="Özel"
            min={1}
            max={50}
            value={isCustom ? selected.toString() : customValue}
            onChange={(e) => handleCustomChange(e.target.value)}
            className={cn(
              "h-full text-center border-2 rounded-xl",
              isCustom
                ? "border-primary bg-primary/10 text-primary"
                : "border-border"
            )}
          />
        </div>
      </div>
    </div>
  );
}
