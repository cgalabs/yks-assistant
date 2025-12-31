import { User, Settings, LogOut, BookOpen, Trophy, Target } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// Mock user data
const mockUser = {
  name: "Mehmet Yılmaz",
  email: "mehmet@example.com",
  avatar: null,
  stats: {
    totalSolved: 127,
    totalGenerated: 45,
    streak: 5,
    accuracy: 78,
  },
  weakTopics: ["Fonksiyonlar", "Geometri"],
  strongTopics: ["Sayılar", "Denklemler"],
};

export default function Profile() {
  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <div className="text-center">
        <div className="w-20 h-20 rounded-full gradient-primary flex items-center justify-center text-primary-foreground mx-auto mb-3 shadow-lg">
          <User className="w-10 h-10" />
        </div>
        <h1 className="text-xl font-bold text-foreground">{mockUser.name}</h1>
        <p className="text-muted-foreground text-sm">{mockUser.email}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-3">
        <Card className="p-4 text-center glass">
          <BookOpen className="w-6 h-6 text-primary mx-auto mb-2" />
          <div className="text-2xl font-bold text-foreground">{mockUser.stats.totalSolved}</div>
          <div className="text-xs text-muted-foreground">Çözülen Soru</div>
        </Card>
        <Card className="p-4 text-center glass">
          <Target className="w-6 h-6 text-primary mx-auto mb-2" />
          <div className="text-2xl font-bold text-foreground">%{mockUser.stats.accuracy}</div>
          <div className="text-xs text-muted-foreground">Doğruluk</div>
        </Card>
        <Card className="p-4 text-center glass">
          <Trophy className="w-6 h-6 text-accent mx-auto mb-2" />
          <div className="text-2xl font-bold text-foreground">{mockUser.stats.streak}</div>
          <div className="text-xs text-muted-foreground">Gün Seri</div>
        </Card>
        <Card className="p-4 text-center glass">
          <BookOpen className="w-6 h-6 text-secondary-foreground mx-auto mb-2" />
          <div className="text-2xl font-bold text-foreground">{mockUser.stats.totalGenerated}</div>
          <div className="text-xs text-muted-foreground">Üretilen Soru</div>
        </Card>
      </div>

      {/* Topics */}
      <Card className="p-4 glass">
        <h3 className="font-semibold text-foreground mb-3">Konu Analizi</h3>
        <div className="space-y-3">
          <div>
            <div className="text-xs text-muted-foreground mb-1">Güçlü Konular</div>
            <div className="flex gap-2 flex-wrap">
              {mockUser.strongTopics.map((topic) => (
                <span
                  key={topic}
                  className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-medium"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground mb-1">Geliştirilmeli</div>
            <div className="flex gap-2 flex-wrap">
              {mockUser.weakTopics.map((topic) => (
                <span
                  key={topic}
                  className="px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 text-xs font-medium"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Actions */}
      <div className="space-y-2">
        <Button variant="outline" className="w-full justify-start gap-3">
          <Settings className="w-5 h-5" />
          Ayarlar
        </Button>
        <Button variant="outline" className="w-full justify-start gap-3 text-destructive hover:text-destructive">
          <LogOut className="w-5 h-5" />
          Çıkış Yap
        </Button>
      </div>
    </div>
  );
}
