import { useState, useCallback } from "react";
import { Upload, FileText, AlertCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface FileUploadZoneProps {
  onFileUpload: (file: File) => void;
}

export function FileUploadZone({ onFileUpload }: FileUploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    if (file.type !== "application/pdf") {
      return "Please upload a PDF file only";
    }
    if (file.size > 50 * 1024 * 1024) { // 50MB limit
      return "File size must be less than 50MB";
    }
    return null;
  };

  const handleFile = (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }
    setError(null);
    onFileUpload(file);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
    // Reset input
    e.target.value = "";
  };

  return (
    <div className="w-full">
      <Card
        className={cn(
          "glass border-2 border-dashed transition-all cursor-pointer hover-shadow-glass",
          isDragOver 
            ? "border-primary bg-primary/5 scale-[1.02]" 
            : "border-glass-border hover:border-primary/50",
          error && "border-destructive bg-destructive/5"
        )}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => document.getElementById("file-input")?.click()}
      >
        <div className="p-12 text-center animate-fade-in">
          <div className={cn(
            "mx-auto mb-6 p-4 rounded-full transition-all",
            isDragOver 
              ? "bg-primary/20 scale-110" 
              : error 
                ? "bg-destructive/20" 
                : "bg-primary/10"
          )}>
            {error ? (
              <AlertCircle className="h-12 w-12 text-destructive mx-auto" />
            ) : (
              <Upload className={cn(
                "h-12 w-12 mx-auto transition-all",
                isDragOver ? "text-primary animate-pulse" : "text-primary/70"
              )} />
            )}
          </div>

          <div className="space-y-2">
            <h3 className={cn(
              "text-xl font-semibold transition-colors",
              error ? "text-destructive" : "text-foreground"
            )}>
              {isDragOver 
                ? "Drop your PDF here" 
                : error 
                  ? "Upload Error" 
                  : "Upload your PDF"
              }
            </h3>
            
            {error ? (
              <p className="text-destructive text-sm">{error}</p>
            ) : (
              <>
                <p className="text-muted-foreground">
                  Drag and drop your PDF file here, or click to browse
                </p>
                <div className="flex items-center justify-center space-x-4 text-sm text-muted-foreground">
                  <div className="flex items-center">
                    <FileText className="h-4 w-4 mr-1" />
                    PDF only
                  </div>
                  <span>•</span>
                  <span>Max 50MB</span>
                </div>
              </>
            )}
          </div>
        </div>
      </Card>

      <input
        id="file-input"
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={handleFileSelect}
      />
    </div>
  );
}