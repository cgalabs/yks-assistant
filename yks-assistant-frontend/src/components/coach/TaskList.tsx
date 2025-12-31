import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Check, Circle, ArrowRight, Camera, Sparkles, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Task {
  id: string;
  text: string;
  action: "solve" | "generate" | "review";
  completed: boolean;
}

interface TaskListProps {
  tasks: Task[];
  onTaskToggle: (id: string) => void;
}

const actionIcons = {
  solve: Camera,
  generate: Sparkles,
  review: RotateCcw,
};

const actionRoutes = {
  solve: "/solve",
  generate: "/generate",
  review: "/history",
};

export function TaskList({ tasks, onTaskToggle }: TaskListProps) {
  const navigate = useNavigate();

  return (
    <div className="bg-card rounded-2xl border border-border p-5 shadow-sm">
      <h3 className="font-semibold text-foreground mb-4">Bugün Yapılacaklar</h3>
      
      <div className="space-y-3">
        {tasks.map((task, index) => {
          const Icon = actionIcons[task.action];
          
          return (
            <div
              key={task.id}
              className={cn(
                "flex items-center gap-3 p-3 rounded-xl border transition-all duration-200 animate-slide-up",
                task.completed
                  ? "bg-success/5 border-success/30"
                  : "bg-secondary/30 border-border hover:border-primary/30"
              )}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <button
                onClick={() => onTaskToggle(task.id)}
                className={cn(
                  "w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all",
                  task.completed
                    ? "bg-success border-success"
                    : "border-muted-foreground/30 hover:border-primary"
                )}
              >
                {task.completed && <Check className="w-3.5 h-3.5 text-success-foreground" />}
              </button>
              
              <div className="flex-1 flex items-center gap-2">
                <Icon className={cn(
                  "w-4 h-4",
                  task.completed ? "text-success" : "text-primary"
                )} />
                <span className={cn(
                  "text-sm",
                  task.completed ? "text-muted-foreground line-through" : "text-foreground"
                )}>
                  {task.text}
                </span>
              </div>
              
              {!task.completed && (
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={() => navigate(actionRoutes[task.action])}
                >
                  <ArrowRight className="w-4 h-4" />
                </Button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
