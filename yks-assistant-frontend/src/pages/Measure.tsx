import { useState } from "react";
import { Upload, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { measureQuestion } from "@/lib/api";
import { toast } from "sonner";

type MeasureState = "idle" | "uploading" | "analyzing" | "done";

interface QualityResult {
  overallScore: number;
  criteria: {
    name: string;
    score: number;
    description: string;
  }[];
  feedback: string;
}

const mockResult: QualityResult = {
  overallScore: 78,
  criteria: [
    { name: "Konu Uyumu", score: 85, description: "ÖSYM formatına konu uyumu" },
    { name: "Zorluk Seviyesi", score: 72, description: "TYT seviyesine uygunluk" },
    { name: "Dil ve Anlatım", score: 80, description: "Soru ifadesinin netliği" },
    { name: "Şık Kalitesi", score: 75, description: "Çeldiricilerin uygunluğu" },
  ],
  feedback: "Bu soru TYT matematik formatına büyük ölçüde uygun. Şıkların dağılımı ve zorluk seviyesi iyi. Çeldiriciler daha güçlü olabilir.",
};

export default function Measure() {
  const [state, setState] = useState<MeasureState>("idle");
  const [result, setResult] = useState<QualityResult | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleUpload = async (file: File) => {
    setState("uploading");

    try {
      const data = await measureQuestion(file);
      setState("analyzing");

      // Map backend response to QualityResult
      const mappedResult: QualityResult = {
        overallScore: Math.round(data.result.osym_similarity * 100),
        criteria: [
          {
            name: "Soru Yapısı",
            score: Math.round(data.result.feature_scores.stem_patterns * 100),
            description: "ÖSYM soru kalıplarının kullanımı"
          },
          {
            name: "Uzunluk",
            score: Math.round(data.result.feature_scores.char_length * 100),
            description: "İdeal soru uzunluğu dengesi"
          },
          {
            name: "Şık Kalitesi",
            score: Math.round(data.result.feature_scores.choice_types * 100),
            description: "Seçeneklerin yapısal tutarlılığı"
          },
          {
            name: "Görsel Uyum",
            score: Math.round(data.result.feature_scores.figure_consistency * 100),
            description: "Şekil ve metin referans uyumu"
          },
        ],
        feedback: `${data.result.reasoning} ${data.result.top_feature_gaps.join(" ")}`,
      };

      setState("done");
      setResult(mappedResult);
    } catch (error) {
      console.error("Measure failed:", error);
      toast.error("Soru analizi sırasında bir hata oluştu.");
      setState("idle");
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleUpload(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleUpload(file);
    }
  };

  const resetMeasure = () => {
    setState("idle");
    setResult(null);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400";
    if (score >= 60) return "text-amber-400";
    return "text-red-400";
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return "bg-emerald-500";
    if (score >= 60) return "bg-amber-500";
    return "bg-red-500";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-foreground mb-1">Soru Kalitesi Ölç</h1>
        <p className="text-muted-foreground text-sm">
          Sorunun ÖSYM formatına yakınlığını analiz et
        </p>
      </div>

      {/* Upload Area */}
      {state === "idle" && (
        <Card
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`p-8 border-2 border-dashed transition-all duration-200 cursor-pointer ${dragActive
            ? "border-primary bg-primary/10"
            : "border-border hover:border-primary/50"
            }`}
        >
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            <div>
              <p className="font-medium text-foreground mb-1">
                Soru görselini yükle
              </p>
              <p className="text-sm text-muted-foreground">
                PNG, JPG veya sürükle bırak
              </p>
            </div>
            <div className="relative">
              <input
                type="file"
                className="absolute inset-0 opacity-0 cursor-pointer"
                onChange={handleFileChange}
                accept="image/*"
              />
              <Button
                variant="outline"
                className="bg-background/50 hover:bg-primary/10 hover:border-primary/50 hover:text-primary transition-all duration-300"
              >
                Dosya Seç
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Loading States */}
      {(state === "uploading" || state === "analyzing") && (
        <Card className="p-8">
          <div className="flex flex-col items-center gap-4 text-center">
            <Loader2 className="w-12 h-12 text-primary animate-spin" />
            <div>
              <p className="font-medium text-foreground">
                {state === "uploading" ? "Yükleniyor..." : "Analiz ediliyor..."}
              </p>
              <p className="text-sm text-muted-foreground">
                {state === "uploading"
                  ? "Soru görseli işleniyor"
                  : "ÖSYM formatıyla karşılaştırılıyor"}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Results */}
      {state === "done" && result && (
        <div className="space-y-4 animate-fade-in">
          {/* Overall Score */}
          <Card className="p-6 text-center glass">
            <div className="mb-4">
              <div className={`text-5xl font-bold ${getScoreColor(result.overallScore)}`}>
                %{result.overallScore}
              </div>
              <div className="text-muted-foreground text-sm mt-1">ÖSYM Uyumluluk Skoru</div>
            </div>
            <div className="flex items-center justify-center gap-2">
              {result.overallScore >= 70 ? (
                <>
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-emerald-400 font-medium">Kabul Edilebilir</span>
                </>
              ) : (
                <>
                  <AlertCircle className="w-5 h-5 text-amber-400" />
                  <span className="text-amber-400 font-medium">İyileştirme Gerekli</span>
                </>
              )}
            </div>
          </Card>

          {/* Criteria Breakdown */}
          <Card className="p-4 glass">
            <h3 className="font-semibold text-foreground mb-4">Detaylı Analiz</h3>
            <div className="space-y-4">
              {result.criteria.map((criterion) => (
                <div key={criterion.name}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-foreground">{criterion.name}</span>
                    <span className={`text-sm font-bold ${getScoreColor(criterion.score)}`}>
                      %{criterion.score}
                    </span>
                  </div>
                  <Progress
                    value={criterion.score}
                    className="h-2"
                    indicatorClassName={getScoreBg(criterion.score)}
                  />
                  <p className="text-xs text-muted-foreground mt-1">{criterion.description}</p>
                </div>
              ))}
            </div>
          </Card>

          {/* Feedback */}
          <Card className="p-4 glass">
            <h3 className="font-semibold text-foreground mb-2">Geri Bildirim</h3>
            <p className="text-sm text-muted-foreground">{result.feedback}</p>
          </Card>

          <Button
            onClick={resetMeasure}
            className="w-full bg-primary/90 hover:bg-primary transition-all duration-300 shadow-glow hover:shadow-glow-lg hover:-translate-y-0.5"
          >
            Yeni Soru Ölç
          </Button>
        </div>
      )}
    </div>
  );
}
