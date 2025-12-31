import 'katex/dist/katex.min.css';
import Latex from 'react-latex-next';

interface LatexRendererProps {
    children: string;
    className?: string;
}

export function LatexRenderer({ children, className }: LatexRendererProps) {
    // Ensure we have a string to process
    const content = children || '';

    // Custom delimiter handling (optional, but good for robustness)
    // react-latex-next handles $...$ and $$...$$ by default.
    // We can also ensure strict mode or trusting html if needed.

    return (
        <span className={className}>
            <Latex>{content}</Latex>
        </span>
    );
}
