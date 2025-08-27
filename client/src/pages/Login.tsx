import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { MessageSquare,Sparkles } from "lucide-react";
import { useAuth } from "@/context/authContext";

const Login = () => {
  const { login, isLoading } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center gradient-primary p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative z-10 w-full max-w-md animate-fade-in">
        <Card className="glass border-0 shadow-2xl">
          <CardHeader className="text-center pb-8">
            <div className="flex items-center justify-center mb-6">
              <div className="p-3 bg-primary/10 rounded-xl">
                <MessageSquare className="h-8 w-8 text-primary" />
              </div>
              <Sparkles className="h-5 w-5 text-accent ml-2 animate-pulse" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Chat with PDF
            </h1>
            <p className="text-muted-foreground mt-2">
              Upload your PDFs and chat with them using AI
            </p>
          </CardHeader>

          <CardContent className="space-y-4">
            <Button
              onClick={() => login("google")}
              disabled={isLoading}
              className="w-full h-12 bg-primary hover:bg-primary-hover text-primary-foreground font-medium transition-all hover-shadow-soft"
            >
              <i className="ri-google-fill"></i>
              Continue with Google
            </Button>

            <Button
              onClick={() => login("github")}
              disabled={isLoading}
              variant="outline"
              className="w-full h-12 bg-secondary/50 hover:bg-secondary-hover border-glass-border transition-all hover-shadow-soft"
            >
              <i className="ri-github-fill"></i>
              Continue with GitHub
            </Button>

            <div className="text-center text-sm text-muted-foreground mt-6">
              By continuing, you agree to our terms of service
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;