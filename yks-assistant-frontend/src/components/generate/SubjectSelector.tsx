import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { BookOpen } from "lucide-react";

const subjects = [
    { id: "tyt-matematik", label: "TYT Matematik" },
];

interface SubjectSelectorProps {
    selected: string | null;
    onSelect: (subject: string) => void;
}

export function SubjectSelector({ selected, onSelect }: SubjectSelectorProps) {
    return (
        <div className="space-y-3">
            <label className="text-sm font-medium text-foreground">Ders Seç</label>
            <Select value={selected || ""} onValueChange={onSelect}>
                <SelectTrigger className="w-full h-12 text-base">
                    <SelectValue placeholder="Bir ders girin..." />
                </SelectTrigger>
                <SelectContent className="bg-card border-border z-50">
                    {subjects.map((subject) => (
                        <SelectItem key={subject.id} value={subject.id} className="cursor-pointer">
                            <span className="flex items-center gap-2">
                                <BookOpen className="w-4 h-4 text-primary" />
                                <span>{subject.label}</span>
                            </span>
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>
        </div>
    );
}
