import { DemoLoginButtons } from '@src/features/login';
import { RegisterForm } from '@src/features/register';
import { AuthShell } from '@src/widgets';

export default function RegisterPage() {
  return (
    <AuthShell
      eyebrow="Начните с малого"
      title="Забота начинается здесь."
      description="Создайте аккаунт и соберите историю, привычки и будущие дела питомца в одном месте."
    >
      <div className="space-y-8">
        <RegisterForm />
        <DemoLoginButtons />
      </div>
    </AuthShell>
  );
}
