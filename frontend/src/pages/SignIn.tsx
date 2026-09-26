import React, { useState, useEffect, useMemo } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Eye, EyeOff, Mail, Smartphone, ShieldCheck } from "lucide-react";
import { useAuth } from "@/contexts/SimpleAuthContext";
import authService from "@/services/authService";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/components/ui/input-otp";

function scorePassword(password: string) {
  const checks = [
    { id: "len", label: "12–72 characters", ok: password.length >= 12 && password.length <= 72 },
    { id: "lower", label: "One lowercase letter (a–z)", ok: /[a-z]/.test(password) },
    { id: "upper", label: "One uppercase letter (A–Z)", ok: /[A-Z]/.test(password) },
    { id: "num", label: "One number (0–9)", ok: /\d/.test(password) },
    { id: "spec", label: "One special character (!@#$%^&*…)", ok: /[^A-Za-z0-9]/.test(password) },
  ];
  const passed = checks.filter((c) => c.ok).length;
  const labels = ["Too weak", "Weak", "Fair", "Good", "Strong", "Excellent"];
  return { checks, passed, label: labels[passed] || "Too weak", pct: (passed / checks.length) * 100 };
}

const PasswordField: React.FC<{
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  autoComplete: string;
  placeholder?: string;
}> = ({ id, label, value, onChange, autoComplete, placeholder }) => {
  const [show, setShow] = useState(false);
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2">
        <Label htmlFor={id}>{label}</Label>
        <button
          type="button"
          className="text-xs text-muted-foreground hover:text-foreground inline-flex items-center gap-1"
          onClick={() => setShow((s) => !s)}
        >
          {show ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
          {show ? "Hide password" : "View password"}
        </button>
      </div>
      <div className="relative">
        <Input
          id={id}
          type={show ? "text" : "password"}
          autoComplete={autoComplete}
          value={value}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          required
          className="pr-11"
        />
        <button
          type="button"
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground"
          onClick={() => setShow((s) => !s)}
          aria-label={show ? "Hide password" : "View password"}
        >
          {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </button>
      </div>
    </div>
  );
};

const SignIn: React.FC = () => {
  const { login, verifyLogin, register, verifyRegister, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const next = (location.state as { from?: string } | null)?.from || "/try";

  const [mode, setMode] = useState<"signin" | "signup" | "forgot">("signin");
  const [step, setStep] = useState<"form" | "otp">("form");
  const [otpKind, setOtpKind] = useState<"login" | "signup" | "reset">("login");
  const [idType, setIdType] = useState<"email" | "mobile">("email");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [fullName, setFullName] = useState("");
  const [emailCode, setEmailCode] = useState("");
  const [smsCode, setSmsCode] = useState("");
  const [challengeId, setChallengeId] = useState("");
  const [maskedEmail, setMaskedEmail] = useState("");
  const [maskedPhone, setMaskedPhone] = useState<string | null>(null);
  const [smsRequired, setSmsRequired] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [busy, setBusy] = useState(false);
  const [resendIn, setResendIn] = useState(0);
  const [policy, setPolicy] = useState<{ email_ready?: boolean; sms_ready?: boolean }>({});

  const strength = useMemo(() => scorePassword(password), [password]);
  const remaining = Math.max(0, 12 - password.length);

  useEffect(() => {
    if (isAuthenticated) navigate(next, { replace: true });
  }, [isAuthenticated, navigate, next]);

  useEffect(() => {
    authService.authPolicy().then(setPolicy).catch(() => {});
  }, []);

  useEffect(() => {
    if (resendIn <= 0) return;
    const t = setTimeout(() => setResendIn((n) => n - 1), 1000);
    return () => clearTimeout(t);
  }, [resendIn]);

  const applyChallenge = (result: Record<string, unknown>, kind: "login" | "signup" | "reset") => {
    setOtpKind(kind);
    setChallengeId(String(result.challenge_id || result.signup_id || result.reset_id || ""));
    setMaskedEmail(String(result.email_masked || ""));
    setMaskedPhone((result.phone_masked as string) || null);
    setSmsRequired(Boolean(result.sms_required));
    setResendIn(Number(result.resend_in || 60));
    setInfo(String(result.message || "Check Gmail Inbox and Spam for a 6-digit code."));
    setEmailCode("");
    setSmsCode("");
    setStep("otp");
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setInfo("");
    if (mode === "signup") {
      if (password !== confirm) {
        setError("Passwords do not match.");
        return;
      }
      if (strength.passed < 5) {
        setError("Password does not meet all requirements.");
        return;
      }
    }
    setBusy(true);
    try {
      if (mode === "forgot") {
        const result = await authService.forgotPassword(email.trim());
        applyChallenge(result, "reset");
        return;
      }
      if (mode === "signin") {
        const result = await login(
          idType === "email" ? email.trim() : "",
          password,
          idType === "mobile" ? phone.trim() : undefined
        );
        if (result.needs_verification) {
          applyChallenge(result, "login");
          return;
        }
        if (!result.success) {
          setError(result.message || "Sign in failed");
          return;
        }
        navigate(next, { replace: true });
        return;
      }
      const result = await register({
        email: email.trim(),
        password,
        fullName: fullName.trim(),
        phone: phone.trim() || undefined,
      });
      if (result.needs_verification) {
        applyChallenge(result, "signup");
        return;
      }
      if (!result.success) {
        setError(result.message || "Could not create account");
        return;
      }
      navigate(next, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setBusy(false);
    }
  };

  const onVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (otpKind === "reset") {
        if (strength.passed < 5) {
          setError("New password does not meet all requirements.");
          setBusy(false);
          return;
        }
        await authService.resetPassword({ reset_id: challengeId, code: emailCode, new_password: password });
        setInfo("Password updated. Sign in.");
        setMode("signin");
        setStep("form");
        setPassword("");
        return;
      }
      const payload = {
        signup_id: challengeId,
        challenge_id: challengeId,
        email_code: emailCode,
        sms_code: smsRequired ? smsCode : undefined,
      };
      const result = otpKind === "login" ? await verifyLogin(payload) : await verifyRegister(payload);
      if (!result.success) {
        setError(result.message || "Verification failed");
        return;
      }
      navigate(next, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed");
    } finally {
      setBusy(false);
    }
  };

  const resend = async (channel: "email" | "sms") => {
    setError("");
    try {
      if (otpKind === "login") {
        await authService.resendLoginOtp({ challenge_id: challengeId, channel });
      } else if (otpKind === "signup") {
        await authService.resendOtp({ signup_id: challengeId, channel });
      } else {
        await authService.forgotPassword(email.trim());
      }
      setResendIn(60);
      setInfo(channel === "sms" ? "New SMS code sent." : "New email code sent. Check Gmail Inbox and Spam.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not resend");
    }
  };

  const heading =
    step === "otp"
      ? otpKind === "reset"
        ? "Reset password"
        : "Verify it’s you"
      : mode === "signup"
        ? "Create account"
        : mode === "forgot"
          ? "Forgot password"
          : "Sign in";

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 shadow-lg">
        <div className="flex items-center gap-2 mb-1">
          <ShieldCheck className="h-5 w-5 text-primary" />
          <h1 className="text-2xl font-bold">{heading}</h1>
        </div>
        <p className="text-sm text-muted-foreground mb-6">
          {step === "otp"
            ? "We emailed a 6-digit code to your Gmail. It expires in 10 minutes."
            : mode === "signin"
              ? "Password plus Gmail inbox code. Mobile OTP is added when your number is verified and Twilio is configured."
              : mode === "forgot"
                ? "We’ll send a reset code to your Gmail inbox."
                : "Gmail inbox verification is required. Mobile OTP is optional if Twilio is configured."}
        </p>

        {step === "form" && mode !== "forgot" && (
          <div className="flex rounded-lg bg-muted p-1 mb-6">
            <button
              type="button"
              className={`flex-1 py-2 text-sm rounded-md ${mode === "signin" ? "bg-background shadow font-medium" : ""}`}
              onClick={() => {
                setMode("signin");
                setError("");
              }}
            >
              Sign in
            </button>
            <button
              type="button"
              className={`flex-1 py-2 text-sm rounded-md ${mode === "signup" ? "bg-background shadow font-medium" : ""}`}
              onClick={() => {
                setMode("signup");
                setError("");
              }}
            >
              Register
            </button>
          </div>
        )}

        {step === "form" && (
          <form onSubmit={onSubmit} className="space-y-4">
            {mode === "signup" && (
              <div className="space-y-2">
                <Label htmlFor="name">Full name</Label>
                <Input id="name" value={fullName} onChange={(e) => setFullName(e.target.value)} required minLength={2} autoComplete="name" />
              </div>
            )}

            {mode === "signin" && (
              <div className="flex rounded-lg bg-muted p-1">
                <button type="button" className={`flex-1 py-1.5 text-xs rounded-md ${idType === "email" ? "bg-background shadow" : ""}`} onClick={() => setIdType("email")}>
                  Gmail
                </button>
                <button type="button" className={`flex-1 py-1.5 text-xs rounded-md ${idType === "mobile" ? "bg-background shadow" : ""}`} onClick={() => setIdType("mobile")}>
                  Mobile
                </button>
              </div>
            )}

            {(mode !== "signin" || idType === "email") && (
              <div className="space-y-2">
                <Label htmlFor="email">Gmail / email</Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required={mode !== "signin" || idType === "email"}
                  placeholder="you@gmail.com"
                />
                <p className="text-xs text-muted-foreground flex items-start gap-1.5">
                  <Mail className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                  {mode === "signin"
                    ? "After the password is correct we send a 6-digit code to this inbox."
                    : "We email a 6-digit code here. Check Inbox and Spam."}
                </p>
              </div>
            )}

            {(mode === "signup" || (mode === "signin" && idType === "mobile")) && (
              <div className="space-y-2">
                <Label htmlFor="phone">{mode === "signin" ? "Mobile number" : "Mobile number (optional)"}</Label>
                <Input
                  id="phone"
                  type="tel"
                  autoComplete="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+91 98765 43210"
                  required={mode === "signin" && idType === "mobile"}
                  disabled={mode === "signup" && policy.sms_ready === false}
                />
                <p className="text-xs text-muted-foreground flex items-start gap-1.5">
                  <Smartphone className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                  {mode === "signin"
                    ? "Use the number on your account. Password still required; Gmail code still sent."
                    : policy.sms_ready
                      ? "We’ll text a second code to this number."
                      : "SMS is off until Twilio is set in config.env."}
                </p>
              </div>
            )}

            {mode !== "forgot" && (
              <PasswordField
                id="password"
                label="Password"
                value={password}
                onChange={setPassword}
                autoComplete={mode === "signin" ? "current-password" : "new-password"}
                placeholder={mode === "signup" ? "12+ characters" : "Your password"}
              />
            )}

            {mode === "signin" && (
              <p className="text-xs text-muted-foreground">
                Account passwords are 12–72 characters with upper, lower, number, and a special character.
                {password.length > 0 && password.length < 12 ? ` ${remaining} more character${remaining === 1 ? "" : "s"} to reach the minimum.` : ""}
              </p>
            )}

            {mode === "signup" && (
              <>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted-foreground">Password strength</span>
                    <span className="font-medium">{strength.label}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        strength.passed <= 2 ? "bg-red-500" : strength.passed <= 3 ? "bg-amber-500" : "bg-emerald-500"
                      }`}
                      style={{ width: `${strength.pct}%` }}
                    />
                  </div>
                  <ul className="mt-2 space-y-1">
                    {strength.checks.map((c) => (
                      <li key={c.id} className={`text-xs ${c.ok ? "text-emerald-600" : "text-muted-foreground"}`}>
                        {c.ok ? "✓" : "○"} {c.label}
                      </li>
                    ))}
                  </ul>
                </div>
                <PasswordField id="confirm" label="Confirm password" value={confirm} onChange={setConfirm} autoComplete="new-password" />
              </>
            )}

            {error && (
              <p className="text-sm text-red-600 bg-red-50 dark:bg-red-950/40 border border-red-200 rounded-md px-3 py-2">{error}</p>
            )}
            {policy.email_ready === false && (
              <p className="text-xs text-amber-700 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 rounded-md px-3 py-2">
                Gmail delivery needs SMTP_USER / SMTP_PASSWORD (App Password) in config.env. Restart the API after saving.
              </p>
            )}
            <Button type="submit" className="w-full" disabled={busy}>
              {busy ? "Please wait…" : mode === "signin" ? "Continue — send Gmail code" : mode === "forgot" ? "Send reset code" : "Send verification code"}
            </Button>
            {mode === "signin" && (
              <button type="button" className="text-xs underline w-full" onClick={() => { setMode("forgot"); setError(""); }}>
                Forgot password?
              </button>
            )}
            {mode === "forgot" && (
              <button type="button" className="text-xs underline w-full" onClick={() => { setMode("signin"); setError(""); }}>
                Back to sign in
              </button>
            )}
          </form>
        )}

        {step === "otp" && (
          <form onSubmit={onVerify} className="space-y-5">
            <div className="space-y-2">
              <Label>Email code · {maskedEmail}</Label>
              <InputOTP maxLength={6} value={emailCode} onChange={setEmailCode}>
                <InputOTPGroup>
                  {Array.from({ length: 6 }).map((_, i) => (
                    <InputOTPSlot key={i} index={i} />
                  ))}
                </InputOTPGroup>
              </InputOTP>
            </div>
            {smsRequired && (
              <div className="space-y-2">
                <Label>SMS code · {maskedPhone}</Label>
                <InputOTP maxLength={6} value={smsCode} onChange={setSmsCode}>
                  <InputOTPGroup>
                    {Array.from({ length: 6 }).map((_, i) => (
                      <InputOTPSlot key={i} index={i} />
                    ))}
                  </InputOTPGroup>
                </InputOTP>
              </div>
            )}
            {otpKind === "reset" && (
              <PasswordField id="newpass" label="New password" value={password} onChange={setPassword} autoComplete="new-password" placeholder="12+ characters" />
            )}
            {info && <p className="text-sm text-muted-foreground">{info}</p>}
            {error && (
              <p className="text-sm text-red-600 bg-red-50 dark:bg-red-950/40 border border-red-200 rounded-md px-3 py-2">{error}</p>
            )}
            <Button
              type="submit"
              className="w-full"
              disabled={busy || emailCode.length !== 6 || (smsRequired && smsCode.length !== 6)}
            >
              {busy ? "Verifying…" : otpKind === "login" ? "Verify and sign in" : otpKind === "reset" ? "Update password" : "Verify and create account"}
            </Button>
            <div className="flex flex-wrap gap-3 text-xs">
              <button type="button" className="underline disabled:opacity-50" disabled={resendIn > 0} onClick={() => resend("email")}>
                {resendIn > 0 ? `Resend email in ${resendIn}s` : "Resend email code"}
              </button>
              {smsRequired && (
                <button type="button" className="underline disabled:opacity-50" disabled={resendIn > 0} onClick={() => resend("sms")}>
                  Resend SMS
                </button>
              )}
              <button
                type="button"
                className="underline"
                onClick={() => {
                  setStep("form");
                  setError("");
                }}
              >
                Back
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default SignIn;
