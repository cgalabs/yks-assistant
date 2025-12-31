import { useCallback, useState } from "react";
import { Camera, Upload, Image as ImageIcon, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ImageUploaderProps {
  onImageSelect: (file: File | null, preview: string | null) => void;
  selectedImage: string | null;
}

export function ImageUploader({ onImageSelect, selectedImage }: ImageUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = () => {
          onImageSelect(file, reader.result as string);
        };
        reader.readAsDataURL(file);
      }
    },
    [onImageSelect]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = () => {
          onImageSelect(file, reader.result as string);
        };
        reader.readAsDataURL(file);
      }
    },
    [onImageSelect]
  );

  const clearImage = useCallback(() => {
    onImageSelect(null, null);
  }, [onImageSelect]);

  if (selectedImage) {
    return (
      <div className="relative rounded-2xl overflow-hidden border border-border bg-card animate-scale-in">
        <img
          src={selectedImage}
          alt="Yüklenen soru"
          className="w-full h-auto max-h-64 object-contain"
        />
        <Button
          variant="icon"
          size="icon-sm"
          className="absolute top-3 right-3 bg-card/90 backdrop-blur-sm"
          onClick={clearImage}
        >
          <X className="w-4 h-4" />
        </Button>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "relative border-2 border-dashed rounded-2xl p-8 transition-all duration-200",
        isDragging
          ? "border-primary bg-primary/5"
          : "border-border hover:border-primary/50 hover:bg-secondary/50"
      )}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        id="image-upload"
      />

      <div className="flex flex-col items-center gap-4 text-center">
        <div className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center shadow-lg">
          <ImageIcon className="w-8 h-8 text-primary-foreground" />
        </div>

        <div>
          <p className="font-semibold text-foreground mb-1">
            Soru fotoğrafını yükle
          </p>
          <p className="text-sm text-muted-foreground">
            Sürükle bırak veya tıkla
          </p>
        </div>

        <div className="flex gap-3 relative z-10">
          <Button
            variant="outline"
            size="sm"
            className="gap-2 bg-background/50 hover:bg-primary/10 hover:border-primary/50 hover:text-primary transition-all duration-300"
            asChild
          >
            <label htmlFor="image-upload" className="cursor-pointer">
              <Upload className="w-4 h-4" />
              Dosya Seç
            </label>
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="gap-2 bg-background/50 hover:bg-primary/10 hover:border-primary/50 hover:text-primary transition-all duration-300"
          >
            <Camera className="w-4 h-4" />
            Kamera
          </Button>
        </div>
      </div>
    </div>
  );
}
