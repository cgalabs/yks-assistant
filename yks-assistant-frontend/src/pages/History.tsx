import { useState } from "react";
import { Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { HistoryItem } from "@/components/history/HistoryItem";
import { cn } from "@/lib/utils";

const mockHistory = [
  { id: "1", type: "solve" as const, topic: "Fonksiyonlar - f(x) = 2x + 3", timestamp: "10 dk önce", correct: true },
  { id: "2", type: "generate" as const, topic: "Fonksiyonlar", timestamp: "25 dk önce", count: 5 },
  { id: "3", type: "solve" as const, topic: "Problemler - Yaş problemi", timestamp: "1 saat önce", correct: false },
  { id: "4", type: "solve" as const, topic: "Geometri - Üçgen alanı", timestamp: "2 saat önce", correct: true },
  { id: "5", type: "generate" as const, topic: "Sayılar", timestamp: "3 saat önce", count: 10 },
  { id: "6", type: "solve" as const, topic: "Denklemler - 2x + 5 = 11", timestamp: "4 saat önce", correct: true },
];

type FilterType = "all" | "solve" | "generate";

export default function History() {
  const [filter, setFilter] = useState<FilterType>("all");

  const filteredHistory = filter === "all"
    ? mockHistory
    : mockHistory.filter(item => item.type === filter);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground mb-1">Geçmiş</h1>
        <p className="text-muted-foreground text-sm">
          Son çözümler ve üretimler
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {[
          { id: "all", label: "Tümü" },
          { id: "solve", label: "Çözümler" },
          { id: "generate", label: "Üretimler" },
        ].map((f) => (
          <Button
            key={f.id}
            variant={filter === f.id ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter(f.id as FilterType)}
            className={cn(
              filter !== f.id && "bg-card"
            )}
          >
            {f.label}
          </Button>
        ))}
      </div>

      {/* History List */}
      <div className="space-y-3">
        {filteredHistory.length > 0 ? (
          filteredHistory.map((item, index) => (
            <HistoryItem key={item.id} item={item} index={index} />
          ))
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Henüz kayıt yok</p>
          </div>
        )}
      </div>
    </div>
  );
}
