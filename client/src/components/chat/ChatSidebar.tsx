import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { 
  MessageSquare, 
  Plus, 
  History, 
  Moon, 
  Sun, 
  User, 
  LogOut,
  Menu,
  X 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { Sidebar, SidebarContent, SidebarHeader, SidebarTrigger, useSidebar } from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/authContext";

interface ChatHistoryItem {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
}



export function ChatSidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { state } = useSidebar();
  const {user} = useAuth();
  const collapsed = state === "collapsed";
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([
    {
      id: "1",
      title: "Research Paper Analysis",
      lastMessage: "Can you summarize the key findings?",
      timestamp: new Date(Date.now() - 3600000)
    },
    {
      id: "2", 
      title: "Contract Review",
      lastMessage: "What are the main terms?",
      timestamp: new Date(Date.now() - 7200000)
    }
  ]);

  console.log(user)
  // Theme toggle
  useEffect(() => {
    const isDark = document.documentElement.classList.contains('dark');
    setIsDarkMode(isDark);
  }, []);

  const toggleTheme = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    document.documentElement.classList.toggle('dark', newDarkMode);
  };

  const handleNewChat = () => {
    const newChatId = Date.now().toString();
    navigate(`/chat/${newChatId}`);
  };

  const handleChatSelect = (chatId: string) => {
    navigate(`/chat/${chatId}`);
  };

  const handleLogout = () => {
    // Simulate logout - replace with real implementation
    navigate("/");
  };

  return (
    <Sidebar className={cn("border-r border-glass-border", collapsed ? "w-16" : "w-80")}>
      <div className="glass-strong h-full flex flex-col">
        {/* Header */}
        <SidebarHeader className="p-4 border-b border-glass-border">
          <div className="flex items-center justify-between">
            {!collapsed && (
              <div className="flex items-center space-x-2">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <MessageSquare className="h-5 w-5 text-primary" />
                </div>
                <span className="font-semibold text-foreground">Ask PDF</span>
              </div>
            )}
            <SidebarTrigger />
          </div>

          {!collapsed && (
            <Button 
              onClick={handleNewChat}
              className="w-full mt-4 bg-primary hover:bg-primary-hover text-primary-foreground transition-all hover-shadow-soft"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Chat
            </Button>
          )}
          {collapsed && (
            <Button 
              onClick={handleNewChat}
              size="sm"
              className="w-full mt-4 bg-primary hover:bg-primary-hover text-primary-foreground p-2"
            >
              <Plus className="h-4 w-4" />
            </Button>
          )}
        </SidebarHeader>

        {/* Chat History */}
        <SidebarContent className="flex-1 p-4">
          {!collapsed && (
            <div className="space-y-2">
        <div className="flex items-center space-x-2 text-sm font-medium text-muted-foreground mb-3">
          <History className="h-4 w-4" />
          <span>Recent Chats</span>
        </div>
              
              {chatHistory.map((chat) => (
                <button
                  key={chat.id}
                  onClick={() => handleChatSelect(chat.id)}
                  className={cn(
                    "w-full p-3 text-left rounded-lg transition-all hover:bg-secondary/50 group",
                    location.pathname.includes(chat.id) && "bg-primary/10 border border-primary/20"
                  )}
                >
                  <div className="font-medium text-sm truncate text-foreground">{chat.title}</div>
                  <div className="text-xs text-muted-foreground truncate mt-1">
                    {chat.lastMessage}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {chat.timestamp.toLocaleDateString()}
                  </div>
                </button>
              ))}
            </div>
          )}
        </SidebarContent>

        {/* Footer */}
        <div className="p-4 border-t border-glass-border">
          <div className="flex items-center justify-between">
            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
              className="hover:bg-secondary/50"
            >
              {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              {!collapsed && <span className="ml-2">{isDarkMode ? 'Light' : 'Dark'}</span>}
            </Button>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="hover:bg-secondary/50">
                  <Avatar className="h-6 w-6">
                    {user?.profile_pic_url ? <AvatarImage src={user.profile_pic_url}></AvatarImage>:<AvatarFallback className="bg-primary text-primary-foreground text-xs">
                      {user?.full_name?.charAt(0) || "U"}
                    </AvatarFallback>}
                  </Avatar>
                  {!collapsed && <span className="ml-2">{user?.full_name}</span>}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="glass border-glass-border">
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </Sidebar>
  );
}