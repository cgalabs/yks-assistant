import { useState, useEffect } from "react";
import { RefreshCw, Loader2, Info, Target } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getCoachAdvice } from "@/lib/api";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";
import { GoalCard } from "@/components/coach/GoalCard";
import { TaskList } from "@/components/coach/TaskList";
import { ChatBox } from "@/components/chat/ChatBox";

const initialTasks = [
  { id: "1", text: "10 soru çöz", action: "solve" as const, completed: false },
  { id: "2", text: "5 kolay soru üret", action: "generate" as const, completed: false },
  { id: "3", text: "Yanlışlara bak", action: "review" as const, completed: false },
];

export default function Coach() {
  const [tasks, setTasks] = useState(initialTasks);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [advice, setAdvice] = useState<{ daily_plan: string, weekly_plan: string, focus_area: string } | null>(null);

  const handleTaskToggle = (id: string) => {
    setTasks(tasks.map(task =>
      task.id === id ? { ...task, completed: !task.completed } : task
    ));
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      // Send some context (mocked for now but could be real user data)
      const data = await getCoachAdvice({
        completed_tasks: tasks.filter(t => t.completed).length,
        total_tasks: tasks.length
      });
      setAdvice(data);
    } catch (error) {
      console.error("Coach failed:", error);
      toast.error("Koç tavsiyesi alınamadı.");
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    handleRefresh();
  }, []);

  const completedCount = tasks.filter(t => t.completed).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">YKS Koçu</h1>
        </div>
        <Button
          variant="outline"
          size="icon"
          onClick={handleRefresh}
          disabled={isRefreshing}
        >
          {isRefreshing ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content - Chat (Left/Wide) */}
        <div className="lg:col-span-2 space-y-4 order-2 lg:order-1">
          {advice && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-scale-in">
              <Card className="p-4 border-primary/20 bg-primary/5">
                <h3 className="font-semibold text-primary mb-1 flex items-center gap-2">
                  <Target className="w-4 h-4" /> Haftalık Hedef
                </h3>
                <p className="text-sm text-foreground">{advice.weekly_plan}</p>
              </Card>
              <Card className="p-4 border-warning/20 bg-warning/5">
                <h3 className="font-semibold text-warning mb-1 flex items-center gap-2">
                  <Info className="w-4 h-4" /> Dikkat Noktası
                </h3>
                <p className="text-sm text-foreground">{advice.focus_area}</p>
              </Card>
              <Card className="col-span-1 md:col-span-2 p-4 border-border">
                <h3 className="font-semibold text-foreground mb-2">Bugünkü Plan</h3>
                <p className="text-sm text-muted-foreground">{advice.daily_plan}</p>
              </Card>
            </div>
          )}

          <ChatBox
            context={{
              type: "coach",
              advice: advice,
              tasks: tasks
            }}
            placeholder="Programımı nasıl daha verimli hale getirebilirim?"
            title="Koçumla Sohbet"
            className="h-[500px]"
          />

          {completedCount === tasks.length && tasks.length > 0 && (
            <div className="text-center py-6 animate-scale-in glass rounded-xl border border-primary/20">
              <div className="text-4xl mb-2">🎉</div>
              <p className="font-semibold text-foreground">Tebrikler!</p>
              <p className="text-sm text-muted-foreground">
                Bugünkü tüm görevleri tamamladın
              </p>
            </div>
          )}
        </div>

        {/* Sidebar - Tools (Right/Narrow) */}
        <div className="space-y-6 order-1 lg:order-2">

          {/* Goal Card */}
          <GoalCard
            dailyGoal={25}
            completed={12}
            weakTopics={advice ? [advice.focus_area] : ["Analiz Bekleniyor..."]}
          />

          {/* Task List */}
          <TaskList tasks={tasks} onTaskToggle={handleTaskToggle} />
        </div>
      </div>
    </div>
  );
}
