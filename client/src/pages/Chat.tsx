import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatArea } from "@/components/chat/ChatArea";
import { SidebarProvider } from "@/components/ui/sidebar";

const Chat = () => {
  const { chat_id } = useParams();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen gradient-secondary">
      <SidebarProvider>
        <div className="flex h-screen w-full">
          <ChatSidebar />
          <ChatArea chatId={chat_id} />
        </div>
      </SidebarProvider>
    </div>
  );
};

export default Chat;