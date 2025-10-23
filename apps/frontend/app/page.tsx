"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

const checkHealth = async () => {
  // Usamos mock para no depender del backend todavía
  await new Promise(resolve => setTimeout(resolve, 600));
  return { status: "ok" as const };
};

export default function OnboardingPage() {
  const router = useRouter();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["healthCheck"],
    queryFn: checkHealth,
    retry: false,
  });

  const handleGoogleConnect = () => {
    alert("Simulando OAuth con Google. (Conectaremos de verdad después)");
  };

  const handleContinue = () => router.push("/dashboard");

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle className="text-2xl">¡Bienvenido a Finanzas PWA!</CardTitle>
          <CardDescription>
            Conecta tu cuenta de Google para sincronizar transacciones de forma segura (read-only).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <h3 className="font-semibold">Paso 1: Conectar Google</h3>
            <p className="text-sm text-muted-foreground">
              Usaremos acceso de solo lectura a Gmail para detectar correos de bancos.
            </p>
            <Button className="w-full" onClick={handleGoogleConnect}>Conectar con Google</Button>
            <p className="text-xs text-center text-muted-foreground">
              Tu privacidad es prioridad. Nunca almacenamos tus correos.
            </p>
          </div>

          <div className="space-y-4">
            <h3 className="font-semibold">Paso 2: Verificación del Sistema</h3>
            <div className="flex items-center justify-between rounded-md border p-4">
              <span className="text-sm font-medium">Estado del Backend</span>
              {isLoading && <span className="text-sm text-muted-foreground">Verificando...</span>}
              {isError && <span className="text-sm text-red-600">Error de conexión</span>}
              {data?.status === "ok" && (
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-sm text-green-600">Conectado</span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
        <CardFooter>
          <Button className="w-full" disabled={isLoading || isError || data?.status !== "ok"} onClick={handleContinue}>
            Comenzar a usar la App
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}

