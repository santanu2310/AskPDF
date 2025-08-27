import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { authService } from "@/lib/auth";
import { useAuth } from "@/context/authContext";

const AuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { checkAuth } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      const provider = "google";
      const user = await authService.handleCallback(provider as "google" | "github");
      
      if (user) {
        await checkAuth(user); // Update auth context
        navigate("/chat/new");
      } else {
        navigate("/login?error=auth_failed");
      }
    };

    handleCallback();
  }, [navigate, searchParams, checkAuth]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
        <p className="mt-4 text-muted-foreground">Completing authentication...</p>
      </div>
    </div>
  );
};

export default AuthCallback;
