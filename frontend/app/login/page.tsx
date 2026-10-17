import {
  DemoLoginButtons,
  LoginForm,
} from '@src/features/login';
import { AuthShell } from '@src/widgets';

export default function LoginPage() {
  return (
    <AuthShell
      eyebrow="С возвращением"
      title="Всё важное — рядом."
      description="Войдите, чтобы продолжить заботу о питомце без лишних поисков и напоминаний."
    >
      <div className="space-y-8">
        <LoginForm />
        <DemoLoginButtons />
      </div>
    </AuthShell>
  );
}
