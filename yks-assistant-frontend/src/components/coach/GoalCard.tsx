import { Target, TrendingUp, AlertCircle } from "lucide-react";

interface GoalCardProps {
  dailyGoal: number;
  completed: number;
  weakTopics: string[];
}

export function GoalCard({ dailyGoal, completed, weakTopics }: GoalCardProps) {
  const progress = Math.round((completed / dailyGoal) * 100);

  return (
    <div className="bg-card rounded-2xl border border-border p-5 shadow-sm space-y-4">
      {/* Daily Goal */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center shadow-md">
            <Target className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Günlük Hedef</p>
            <p className="text-xl font-bold text-foreground">{dailyGoal} soru</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gradient">{progress}%</p>
          <p className="text-xs text-muted-foreground">{completed}/{dailyGoal}</p>
        </div>
      </div>

      {/* Weak Topics */}
      <div className="pt-4 border-t border-border">
        <div className="flex items-center gap-2 mb-3">
          <AlertCircle className="w-4 h-4 text-warning" />
          <span className="text-sm font-medium text-foreground">Zayıf Konular</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {weakTopics.map((topic) => (
            <span
              key={topic}
              className="px-3 py-1.5 bg-warning/10 text-warning rounded-full text-xs font-medium"
            >
              {topic}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
