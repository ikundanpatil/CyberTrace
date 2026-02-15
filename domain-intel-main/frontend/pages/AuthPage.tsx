import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { Lock, Mail, User, Building2, Loader2 } from "lucide-react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { toast } from "@/hooks/use-toast";
import { login, signup } from "@/lib/api";

// Validation schemas
const loginSchema = z.object({
    email: z.string().trim().email("Enter a valid email").max(255),
    password: z.string().min(8, "Password must be at least 8 characters").max(128),
    remember: z.boolean(),
});

type LoginValues = z.infer<typeof loginSchema>;

const signupSchema = z
    .object({
        fullName: z.string().trim().min(2, "Enter your full name").max(120),
        email: z.string().trim().email("Enter a valid email").max(255),
        organization: z.string().trim().min(2, "Enter your organization/department").max(160),
        password: z.string().min(8, "Password must be at least 8 characters").max(128),
        confirmPassword: z.string().min(8, "Confirm your password").max(128),
    })
    .refine((v) => v.password === v.confirmPassword, {
        path: ["confirmPassword"],
        message: "Passwords do not match",
    });

type SignupValues = z.infer<typeof signupSchema>;

function FieldError({ message }: { message?: string }) {
    if (!message) return null;
    return <p className="mt-1 text-sm text-destructive">{message}</p>;
}

function IconInput({
    icon,
    inputProps,
}: {
    icon: React.ReactNode;
    inputProps: React.ComponentProps<typeof Input>;
}) {
    return (
        <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-muted-foreground">
                {icon}
            </div>
            <Input {...inputProps} className={`pl-10 ${inputProps.className ?? ""}`} />
        </div>
    );
}

export default function AuthPage() {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<"login" | "signup">("login");

    const loginForm = useForm<LoginValues>({
        resolver: zodResolver(loginSchema),
        defaultValues: { email: "", password: "", remember: true },
        mode: "onTouched",
    });

    const signupForm = useForm<SignupValues>({
        resolver: zodResolver(signupSchema),
        defaultValues: { fullName: "", email: "", organization: "", password: "", confirmPassword: "" },
        mode: "onTouched",
    });

    const loginLoading = loginForm.formState.isSubmitting;
    const signupLoading = signupForm.formState.isSubmitting;

    const subtitle = useMemo(
        () =>
            activeTab === "login"
                ? "Authenticate to access secure operations."
                : "Provision a verified operator identity.",
        [activeTab],
    );

    const onLogin = async (values: LoginValues) => {
        try {
            const res = await login({
                email: values.email,
                password: values.password,
            });
            localStorage.setItem("cybertrace_token", res.token);
            toast({
                title: "Access granted",
                description: res.message ?? "Authentication successful.",
            });
            navigate("/");
        } catch (e) {
            toast({
                title: "Access denied",
                description: e instanceof Error ? e.message : "Login failed.",
                variant: "destructive",
            });
        }
    };

    const onSignup = async (values: SignupValues) => {
        try {
            const res = await signup({
                fullName: values.fullName,
                email: values.email,
                organization: values.organization,
                password: values.password,
            });
            toast({
                title: "Enrollment complete",
                description: res.message ?? "Account created. You can now sign in.",
            });
            // Auto-login after signup
            localStorage.setItem("cybertrace_token", res.token);
            navigate("/");
        } catch (e) {
            toast({
                title: "Enrollment failed",
                description: e instanceof Error ? e.message : "Sign up failed.",
                variant: "destructive",
            });
        }
    };

    return (
        <div className="relative min-h-screen overflow-hidden bg-background">
            {/* Cyber background */}
            <div className="absolute inset-0 cyber-bg" />
            <div className="absolute inset-0 opacity-30 cyber-grid" />

            <main className="relative mx-auto flex min-h-screen max-w-7xl items-center justify-center px-4 py-10">
                <Card className="w-full max-w-md border-border/80 bg-card/95 shadow-xl backdrop-blur animate-in fade-in duration-500">
                    <div className="p-6 sm:p-7">
                        <header className="mb-6 text-center">
                            <h1 className="text-2xl font-semibold tracking-wide">CyberTrace</h1>
                            <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>
                        </header>

                        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "login" | "signup")}>
                            <TabsList className="grid w-full grid-cols-2 bg-muted/30">
                                <TabsTrigger value="login">Login</TabsTrigger>
                                <TabsTrigger value="signup">Sign Up</TabsTrigger>
                            </TabsList>

                            {/* LOGIN TAB */}
                            <TabsContent value="login" className="mt-5">
                                <form onSubmit={loginForm.handleSubmit(onLogin)} className="space-y-4">
                                    <div>
                                        <Label htmlFor="login-email">Email</Label>
                                        <div className="mt-2">
                                            <IconInput
                                                icon={<Mail className="h-4 w-4" />}
                                                inputProps={{
                                                    id: "login-email",
                                                    type: "email",
                                                    autoComplete: "email",
                                                    placeholder: "operator@agency.gov",
                                                    ...loginForm.register("email"),
                                                }}
                                            />
                                            <FieldError message={loginForm.formState.errors.email?.message} />
                                        </div>
                                    </div>

                                    <div>
                                        <Label htmlFor="login-password">Password</Label>
                                        <div className="mt-2">
                                            <IconInput
                                                icon={<Lock className="h-4 w-4" />}
                                                inputProps={{
                                                    id: "login-password",
                                                    type: "password",
                                                    autoComplete: "current-password",
                                                    placeholder: "••••••••",
                                                    ...loginForm.register("password"),
                                                }}
                                            />
                                            <FieldError message={loginForm.formState.errors.password?.message} />
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between gap-3">
                                        <div className="flex items-center gap-2">
                                            <Checkbox
                                                id="remember"
                                                checked={loginForm.watch("remember")}
                                                onCheckedChange={(v) => loginForm.setValue("remember", Boolean(v))}
                                            />
                                            <Label htmlFor="remember" className="text-sm text-muted-foreground">
                                                Remember me
                                            </Label>
                                        </div>
                                    </div>

                                    <Button
                                        type="submit"
                                        className="w-full"
                                        disabled={loginLoading}
                                    >
                                        {loginLoading ? (
                                            <>
                                                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                                Authenticating
                                            </>
                                        ) : (
                                            "Login"
                                        )}
                                    </Button>
                                </form>
                            </TabsContent>

                            {/* SIGNUP TAB */}
                            <TabsContent value="signup" className="mt-5">
                                <form onSubmit={signupForm.handleSubmit(onSignup)} className="space-y-4">
                                    <div>
                                        <Label htmlFor="fullName">Full Name</Label>
                                        <div className="mt-2">
                                            <IconInput
                                                icon={<User className="h-4 w-4" />}
                                                inputProps={{
                                                    id: "fullName",
                                                    type: "text",
                                                    autoComplete: "name",
                                                    placeholder: "Alex Morgan",
                                                    ...signupForm.register("fullName"),
                                                }}
                                            />
                                            <FieldError message={signupForm.formState.errors.fullName?.message} />
                                        </div>
                                    </div>

                                    <div>
                                        <Label htmlFor="signup-email">Email</Label>
                                        <div className="mt-2">
                                            <IconInput
                                                icon={<Mail className="h-4 w-4" />}
                                                inputProps={{
                                                    id: "signup-email",
                                                    type: "email",
                                                    autoComplete: "email",
                                                    placeholder: "operator@agency.gov",
                                                    ...signupForm.register("email"),
                                                }}
                                            />
                                            <FieldError message={signupForm.formState.errors.email?.message} />
                                        </div>
                                    </div>

                                    <div>
                                        <Label htmlFor="org">Organization / Department</Label>
                                        <div className="mt-2">
                                            <IconInput
                                                icon={<Building2 className="h-4 w-4" />}
                                                inputProps={{
                                                    id: "org",
                                                    type: "text",
                                                    autoComplete: "organization",
                                                    placeholder: "Cyber Defense Unit",
                                                    ...signupForm.register("organization"),
                                                }}
                                            />
                                            <FieldError message={signupForm.formState.errors.organization?.message} />
                                        </div>
                                    </div>

                                    <div>
                                        <Label htmlFor="signup-password">Password</Label>
                                        <div className="mt-2">
                                            <IconInput
                                                icon={<Lock className="h-4 w-4" />}
                                                inputProps={{
                                                    id: "signup-password",
                                                    type: "password",
                                                    autoComplete: "new-password",
                                                    placeholder: "Create a strong password",
                                                    ...signupForm.register("password"),
                                                }}
                                            />
                                            <FieldError message={signupForm.formState.errors.password?.message} />
                                        </div>
                                    </div>

                                    <div>
                                        <Label htmlFor="confirmPassword">Confirm Password</Label>
                                        <div className="mt-2">
                                            <IconInput
                                                icon={<Lock className="h-4 w-4" />}
                                                inputProps={{
                                                    id: "confirmPassword",
                                                    type: "password",
                                                    autoComplete: "new-password",
                                                    placeholder: "Repeat password",
                                                    ...signupForm.register("confirmPassword"),
                                                }}
                                            />
                                            <FieldError message={signupForm.formState.errors.confirmPassword?.message} />
                                        </div>
                                    </div>

                                    <Button
                                        type="submit"
                                        className="w-full"
                                        disabled={signupLoading}
                                    >
                                        {signupLoading ? (
                                            <>
                                                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                                Enrolling
                                            </>
                                        ) : (
                                            "Sign Up"
                                        )}
                                    </Button>
                                </form>
                            </TabsContent>
                        </Tabs>

                        <div className="mt-6 text-center text-sm text-muted-foreground">
                            {activeTab === "login" ? (
                                <>
                                    Don&apos;t have an account?{" "}
                                    <button
                                        type="button"
                                        onClick={() => setActiveTab("signup")}
                                        className="text-primary underline-offset-4 hover:underline"
                                    >
                                        Sign up
                                    </button>
                                </>
                            ) : (
                                <>
                                    Already have an account?{" "}
                                    <button
                                        type="button"
                                        onClick={() => setActiveTab("login")}
                                        className="text-primary underline-offset-4 hover:underline"
                                    >
                                        Login
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </Card>
            </main>
        </div>
    );
}
