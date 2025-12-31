import { useState, useRef, useEffect } from "react";
import { Send, User, Bot, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { sendMessage } from "@/lib/api";
import { cn } from "@/lib/utils";
import { LatexRenderer } from "@/components/ui/LatexRenderer";

interface Message {
    role: "user" | "assistant";
    content: string;
}

interface ChatBoxProps {
    context?: any;
    placeholder?: string;
    title?: string;
    className?: string;
    children?: React.ReactNode;
    headerAction?: React.ReactNode;
}

export function ChatBox({
    context,
    placeholder = "Bir şeyler sorun...",
    title = "YKS Asistanına Sor",
    className,
    children,
    headerAction
}: ChatBoxProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const viewportRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (viewportRef.current) {
            viewportRef.current.scrollTop = viewportRef.current.scrollHeight;
        }
    }, [messages, children, isLoading]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = { role: "user", content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const response = await sendMessage(input, messages, context);
            const assistantMessage: Message = { role: "assistant", content: response.response };
            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            console.error("Chat failed:", error);
            const errorMessage: Message = { role: "assistant", content: "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin." };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card className={cn("flex flex-col border-border/50 glass animate-fade-in overflow-hidden", className)}>
            {/* Chat Header */}
            <div className="p-3 border-b border-border/50 bg-secondary/30 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Bot className="w-4 h-4 text-primary" />
                    <span className="text-sm font-semibold text-foreground">{title}</span>
                </div>
                {headerAction}
            </div>



            {/* Messages Area */}
            <ScrollArea className="flex-1 p-4" viewportRef={viewportRef}>
                <div className="space-y-4">
                    {children && (
                        <div className="mb-4">
                            {children}
                        </div>
                    )}
                    {messages.length === 0 && !children && (
                        <div className="text-center text-sm text-muted-foreground py-8">
                            Henüz mesaj yok. Sorunuzu aşağıya yazabilirsiniz.
                        </div>
                    )}
                    {messages.map((msg, i) => (
                        <div
                            key={i}
                            className={cn(
                                "flex gap-3 text-sm animate-in fade-in slide-in-from-bottom-2",
                                msg.role === "user" ? "flex-row-reverse" : "flex-row"
                            )}
                        >
                            <div className={cn(
                                "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                                msg.role === "user" ? "bg-primary/20 text-primary" : "bg-muted text-muted-foreground"
                            )}>
                                {msg.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                            </div>

                            <div className={cn(
                                "p-3 rounded-2xl max-w-[80%]",
                                msg.role === "user"
                                    ? "bg-primary text-primary-foreground rounded-tr-none"
                                    : "bg-muted text-foreground rounded-tl-none"
                            )}>
                                <LatexRenderer>{msg.content}</LatexRenderer>
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="flex gap-3 text-sm animate-pulse">
                            <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                                <Bot className="w-4 h-4 text-muted-foreground" />
                            </div>
                            <div className="bg-muted p-3 rounded-2xl rounded-tl-none max-w-[80%] flex items-center gap-2">
                                <Loader2 className="w-3 h-3 animate-spin" />
                                Düşünüyor...
                            </div>
                        </div>
                    )}
                </div>
            </ScrollArea>

            {/* Input Area */}
            <div className="p-3 border-t border-border/50 bg-secondary/10 flex gap-2">
                <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                    placeholder={placeholder}
                    disabled={isLoading}
                    className="bg-background/50 border-border/50 focus:border-primary/50 transition-all"
                />
                <Button
                    size="icon"
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                    className="shrink-0"
                >
                    <Send className="w-4 h-4" />
                </Button>
            </div>
        </Card>
    );
}
