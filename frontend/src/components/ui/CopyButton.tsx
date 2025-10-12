import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { useToast } from "./use-toast";
import { Copy, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface CopyButtonProps {
  text: string;
  className?: string;
  variant?: "default" | "outline" | "ghost" | "secondary";
  size?: "default" | "sm" | "lg" | "icon";
}

export const CopyButton: React.FC<CopyButtonProps> = ({
  text,
  className,
  variant = "ghost",
  size = "sm"
}) => {
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast({
        title: "Copied!",
        description: "Text has been copied to your clipboard.",
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast({
        title: "Failed to copy",
        description: "Please copy the text manually.",
        variant: "destructive"
      });
    }
  };

  return (
    <Button
      onClick={copyToClipboard}
      variant={variant}
      size={size}
      className={cn("neural-button", className)}
    >
      {copied ? (
        <CheckCircle2 className="w-4 h-4" />
      ) : (
        <Copy className="w-4 h-4" />
      )}
    </Button>
  );
};
