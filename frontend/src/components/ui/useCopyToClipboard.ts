import { useState } from 'react';
import { toast } from '@/components/ui/use-toast';

export const useCopyToClipboard = () => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      
      toast({
        title: "Copied to clipboard!",
        description: "The text has been copied successfully.",
      });

      setTimeout(() => setCopied(false), 2000);
      return true;
    } catch (err) {
      toast({
        title: "Failed to copy",
        description: "Please try again.",
        variant: "destructive",
      });
      return false;
    }
  };

  return { copyToClipboard, copied };
};
