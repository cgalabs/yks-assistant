import { useState, useEffect } from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

export function WarningPopup() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    // Check if user has already seen the popup (session based or local storage)
    // For this specific request ("linki kimseyle paylaşmayın"), showing it every time (session) or once (localStorage)
    // The user said "site açılınca popup çıksın", implying every visit or at least session.
    // Let's use sessionStorage so it shows up on new tabs/windows but not on reload if we wanted, 
    // BUT usually "warning" implies every time or check.
    // Let's stick to simple "always show on mount" for now, or check a flag.
    // However, user said "popupu okudum... diyince kapatabilirsin". 
    // Let's show it on mount.
    setOpen(true);
  }, []);

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className="text-destructive font-bold">⚠️ DİKKAT: Özel Deneme Sürümü</AlertDialogTitle>
          <AlertDialogDescription className="space-y-4 text-foreground">
            <p>
              Bu site <strong>yks-assistant</strong> projesinin <strong>deneysel (beta)</strong> sürümüdür.
            </p>
            <ul className="list-disc pl-5 space-y-2">
              <li>
                <strong>Erişim Kısıtlıdır:</strong> Bu link özeldir. Lütfen erişim yetkisi olmayan kişilerle <strong>PAYLAŞMAYINIZ</strong>.
              </li>
              <li>
                <strong>Kullanım Limiti:</strong> Yapay zeka modellerinin (LLM) kullanımında belirli limitler vardır. Lütfen sistemi aşırı (spam) kullanmaktan kaçınınız.
              </li>
              <li>
                <strong>Hata Payı:</strong> Modeller deneysel aşamadadır, hatalı veya eksik cevaplar verebilir. Her zaman kendi kontrolünüzü yapınız.
              </li>
              <li>
                <strong>Hatalar:</strong> Sitede geliştirme sürecine bağlı teknik aksaklıklar yaşanabilir.
              </li>
              <li>
                <strong>Kapsam:</strong> Modeller şu an için sadece <strong>TYT Matematik</strong> üzerine eğitilmiştir. Diğer derslerdeki performansı garanti edilmez.
              </li>
            </ul>
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogAction onClick={() => setOpen(false)} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
            Okudum, Anlıyorum
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
