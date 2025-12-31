import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const topics = [
  { id: "1. dereceden bir bilinmeyenli denklemler", label: "1. Dereceden Bir Bilinmeyenli Denklemler" },
  { id: "1. dereceden denklem ve eşitsizlikler", label: "1. Dereceden Denklem ve Eşitsizlikler" },
  { id: "ardışık sayılar", label: "Ardışık Sayılar" },
  { id: "asal ve aralarında asal sayılar", label: "Asal ve Aralarında Asal Sayılar" },
  { id: "asal çarpanlara ayırma", label: "Asal Çarpanlara Ayırma" },
  { id: "basit eşitsizlikler", label: "Basit Eşitsizlikler" },
  { id: "binom", label: "Binom" },
  { id: "bölme - bölünebilme", label: "Bölme - Bölünebilme" },
  { id: "çokgen ve dörtgenlerin özellikleri", label: "Çokgen ve Dörtgenlerin Özellikleri" },
  { id: "dik üçgen ve trigonometri", label: "Dik Üçgen ve Trigonometri" },
  { id: "dörtgenler", label: "Dörtgenler" },
  { id: "ebob - ekok", label: "EBOB - EKOK" },
  { id: "eşkenar dörtgen, dikdörtgen", label: "Eşkenar Dörtgen, Dikdörtgen" },
  { id: "faktöriyel", label: "Faktöriyel" },
  { id: "fonksiyon kavramı ve özellikleri", label: "Fonksiyon Kavramı ve Özellikleri" },
  { id: "fonksiyonlar", label: "Fonksiyonlar" },
  { id: "fonksiyonun tersi", label: "Fonksiyonun Tersi" },
  { id: "grafik problemleri", label: "Grafik Problemleri" },
  { id: "hız problemleri", label: "Hız Problemleri" },
  { id: "ikinci dereceden denklemler", label: "İkinci Dereceden Denklemler" },
  { id: "ikinci dereceden denklemler, karmaşık sayılar", label: "İkinci Dereceden Denklemler, Karmaşık Sayılar" },
  { id: "işçi problemleri", label: "İşçi Problemleri" },
  { id: "kar-zarar, yüzde, karışım, hareket problemleri", label: "Kar-Zarar, Yüzde, Karışım, Hareket Problemleri" },
  { id: "kare, deltoid", label: "Kare, Deltoid" },
  { id: "karmaşık sayılar", label: "Karmaşık Sayılar" },
  { id: "karışım problemleri", label: "Karışım Problemleri" },
  { id: "katı cisimler - prizmalar", label: "Katı Cisimler - Prizmalar" },
  { id: "kesir problemleri", label: "Kesir Problemleri" },
  { id: "kombinasyon", label: "Kombinasyon" },
  { id: "kümeler", label: "Kümeler" },
  { id: "köklü sayılar", label: "Köklü Sayılar" },
  { id: "küme problemleri", label: "Küme Problemleri" },
  { id: "kümeler ve kartezyen çarpım", label: "Kümeler ve Kartezyen Çarpım" },
  { id: "mantık", label: "Mantık" },
  { id: "mutlak değer", label: "Mutlak Değer" },
  { id: "olasılık", label: "Olasılık" },
  { id: "oran - orantı", label: "Oran - Orantı" },
  { id: "periyodik problemler", label: "Periyodik Problemler" },
  { id: "permütasyon, kombinasyon, binom", label: "Permütasyon, Kombinasyon, Binom" },
  { id: "polinomlar", label: "Polinomlar" },
  { id: "polinomlar ve çarpanlara ayırma", label: "Polinomlar ve Çarpanlara Ayırma" },
  { id: "rasyonel sayılar", label: "Rasyonel Sayılar" },
  { id: "sayma", label: "Sayma" },
  { id: "sayma, küme ve fonksiyon ilişkisi", label: "Sayma, Küme ve Fonksiyon İlişkisi" },
  { id: "sayı basamakları", label: "Sayı Basamakları" },
  { id: "sayı problemleri", label: "Sayı Problemleri" },
  { id: "sayı, kesir, yaş, işçi problemleri", label: "Sayı, Kesir, Yaş, İşçi Problemleri" },
  { id: "tek ve çift sayılar", label: "Tek ve Çift Sayılar" },
  { id: "temel kavramlar", label: "Temel Kavramlar" },
  { id: "temel kavramlar, sayı basmakları, sayı kümeleri", label: "Temel Kavramlar, Sayı Basamakları, Sayı Kümeleri" },
  { id: "üçgende eşlik ve benzerlik", label: "Üçgende Eşlik ve Benzerlik" },
  { id: "üçgende temel kavramlar, üçgen eşitsizliği, üçgenin yardımcı elemanları", label: "Üçgende Temel Kavramlar, Üçgen Eşitsizliği, Üçgenin Yardımcı Elemanları" },
  { id: "üçgenin alanı", label: "Üçgenin Alanı" },
  { id: "üçgenler", label: "Üçgenler" },
  { id: "üslü ve köklü ifadeler", label: "Üslü ve Köklü İfadeler" },
  { id: "veri", label: "Veri" },
  { id: "yamuk, paralelkenar", label: "Yamuk, Paralelkenar" },
  { id: "yaş problemleri", label: "Yaş Problemleri" },
  { id: "yüzde problemleri", label: "Yüzde Problemleri" },
  { id: "çarpanlara ayırma", label: "Çarpanlara Ayırma" },
  { id: "üslü sayılar", label: "Üslü Sayılar" },
];

interface TopicSelectorProps {
  selected: string | null;
  onSelect: (topic: string) => void;
}

export function TopicSelector({ selected, onSelect }: TopicSelectorProps) {
  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-foreground">Konu Seç</label>
      <Select value={selected || ""} onValueChange={onSelect}>
        <SelectTrigger className="w-full h-12 text-base">
          <SelectValue placeholder="Bir konu girin..." />
        </SelectTrigger>
        <SelectContent className="bg-card border-border z-50">
          {topics.map((topic) => (
            <SelectItem key={topic.id} value={topic.id} className="cursor-pointer">
              <span>{topic.label}</span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
