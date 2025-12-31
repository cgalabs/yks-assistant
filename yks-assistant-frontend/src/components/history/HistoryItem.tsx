import { useNavigate } from "react-router-dom";
import { Clock, Camera, Sparkles, CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface HistoryItemProps {
  item: {
    id: string;
    type: "solve" | "generate";
    topic: string;
    timestamp: string;
    correct?: boolean;
    count?: number;
  };
  index: number;
}

export function HistoryItem({ item, index }: HistoryItemProps) {
  const navigate = useNavigate();
  const isSolve = item.type === "solve";

  const handleClick = () => {
    navigate(isSolve ? "/solve" : "/generate", {
      state: {
        fromHistory: true,
        item: item
      }
    });
  };

  return (
    <div
      onClick={handleClick}
      className="flex items-center gap-4 p-4 bg-card rounded-xl border border-border shadow-sm animate-slide-up cursor-pointer hover:border-primary/50 hover:bg-primary/5 transition-all active:scale-[0.98]"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      {/* Icon */}
      <div className={cn(
        "w-10 h-10 rounded-xl flex items-center justify-center",
        isSolve ? "bg-primary/10" : "bg-accent/10"
      )}>
        {isSolve ? (
          <Camera className="w-5 h-5 text-primary" />
        ) : (
          <Sparkles className="w-5 h-5 text-accent" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className="font-medium text-foreground truncate">{item.topic}</p>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Clock className="w-3 h-3" />
          <span>{item.timestamp}</span>
          {!isSolve && item.count && (
            <span className="px-2 py-0.5 bg-secondary rounded-full">
              {item.count} soru
            </span>
          )}
        </div>
      </div>

      {/* Status */}
      {isSolve && (
        <div>
          {item.correct ? (
            <CheckCircle2 className="w-5 h-5 text-success" />
          ) : (
            <XCircle className="w-5 h-5 text-destructive" />
          )}
        </div>
      )}
    </div>
  );
}
