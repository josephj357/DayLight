import { Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface DisclaimerProps {
  variant?: "inline" | "block";
  className?: string;
  children?: React.ReactNode;
}

/**
 * Small recurring disclaimer about what campaign-finance data can and
 * can't show. Worth repeating — voters underestimate how much is hidden.
 */
export function Disclaimer({
  variant = "inline",
  className,
  children,
}: DisclaimerProps) {
  const message =
    children ??
    "This shows publicly disclosed donations. Dark money (501(c)(4)) and certain independent expenditures are not visible by law.";

  if (variant === "block") {
    return (
      <aside
        className={cn(
          "rounded-lg border border-ink-200 bg-ink-50 px-4 py-3 text-sm text-ink-600 flex gap-3 items-start",
          className,
        )}
        role="note"
      >
        <Info className="h-4 w-4 mt-0.5 shrink-0 text-ink-500" aria-hidden="true" />
        <p>{message}</p>
      </aside>
    );
  }

  return (
    <p
      className={cn(
        "text-xs text-ink-500 inline-flex items-center gap-1.5",
        className,
      )}
    >
      <Info className="h-3 w-3" aria-hidden="true" />
      <span>{message}</span>
    </p>
  );
}
