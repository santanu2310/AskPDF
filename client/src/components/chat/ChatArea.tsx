import { useState, useRef, useCallback } from "react";
import { Send, Upload, FileText, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileUploadZone } from "@/components/chat/FileUploadZone";
import { ChatMessage } from "@/components/chat/ChatMessage";

interface ChatAreaProps {
  chatId?: string;
}

interface Message {
  id: string;
  content: string;
  sender: "user" | "assistant";
  timestamp: Date;
}

interface UploadedFile {
  name: string;
  size: number;
  type: string;
  url: string;
}

export function ChatArea({ chatId }: ChatAreaProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: uploadedFile 
          ? `Based on your uploaded PDF "${uploadedFile.name}", I can help analyze the content. ${inputValue.includes("summarize") ? "Here's a summary of the key points from the document..." : "I'm ready to answer questions about the document."}`
          : "Please upload a PDF first so I can help you analyze it.",
        sender: "assistant",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = (file: File) => {
    setUploadedFile({
      name: file.name,
      size: file.size,
      type: file.type,
      url: URL.createObjectURL(file),
    });

    const uploadMessage: Message = {
      id: Date.now().toString(),
      content: `Uploaded PDF: ${file.name}`,
      sender: "user",
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, uploadMessage]);

    // Simulate processing
    setTimeout(() => {
      const processMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `I've successfully processed your PDF "${file.name}". You can now ask me questions about its content, request summaries, or get specific information from the document.`,
        sender: "assistant",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, processMessage]);
    }, 1500);
  };

  const removeFile = () => {
    if (uploadedFile?.url) {
      URL.revokeObjectURL(uploadedFile.url);
    }
    setUploadedFile(null);
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        {messages.length === 0 ? (
          /* Upload Area - Centered when no messages */
          <div className="w-full max-w-2xl">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-semibold text-foreground mb-2">
                Upload a PDF to get started
              </h2>
              <p className="text-muted-foreground">
                Drag and drop your PDF file or click to browse
              </p>
            </div>
            <FileUploadZone onFileUpload={handleFileUpload} />
            
            {uploadedFile && (
              <Card className="glass mt-6 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-medium text-foreground">{uploadedFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={removeFile}>
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </Card>
            )}
          </div>
        ) : (
          /* Chat Messages - When chat has started */
          <div className="w-full max-w-4xl flex-1 flex flex-col">
            {/* File Status Bar */}
            {uploadedFile && (
              <Card className="glass mb-4 p-3 border-primary/20 bg-primary/5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-4 w-4 text-primary" />
                    <span className="text-sm font-medium text-foreground">
                      {uploadedFile.name}
                    </span>
                  </div>
                  <Button variant="ghost" size="sm" onClick={removeFile}>
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              </Card>
            )}

            {/* Messages */}
            <ScrollArea className="flex-1 pr-4" ref={scrollAreaRef}>
              <div className="space-y-6">
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}
                {isLoading && (
                  <ChatMessage 
                    message={{
                      id: "loading",
                      content: "Thinking...",
                      sender: "assistant",
                      timestamp: new Date(),
                    }}
                    isLoading
                  />
                )}
              </div>
            </ScrollArea>
          </div>
        )}
      </div>

      {/* Chat Input - Always at bottom */}
      <div className="border-t border-glass-border glass p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex space-x-3">
            {!uploadedFile && messages.length === 0 && (
              <Button
                variant="outline"
                size="sm"
                className="shrink-0 bg-secondary/50 hover:bg-secondary-hover border-glass-border"
                onClick={() => document.getElementById('file-upload')?.click()}
              >
                <Upload className="h-4 w-4 mr-2" />
                Upload PDF
              </Button>
            )}
            
            <div className="flex-1 relative">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={uploadedFile ? "Ask a question about your PDF..." : "Upload a PDF first"}
                disabled={!uploadedFile || isLoading}
                className="pr-12 bg-background/50 border-glass-border focus:border-primary"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || !uploadedFile || isLoading}
                size="sm"
                className="absolute right-1 top-1 h-8 w-8 bg-primary hover:bg-primary-hover text-primary-foreground"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Hidden file input */}
      <input
        id="file-upload"
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFileUpload(file);
        }}
      />
    </div>
  );
}