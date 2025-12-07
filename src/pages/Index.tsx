import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

export default function Index() {
  const [nickname, setNickname] = useState('');
  const [donateAmount, setDonateAmount] = useState('');
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!nickname.trim()) {
      toast({
        title: "Ошибка",
        description: "Введите ваш никнейм",
        variant: "destructive",
      });
      return;
    }

    if (!donateAmount || Number(donateAmount) <= 0) {
      toast({
        title: "Ошибка",
        description: "Введите корректную сумму доната",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Успешно!",
      description: `Донат ${donateAmount} руб. от игрока ${nickname}`,
    });

    setNickname('');
    setDonateAmount('');
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-blue-600 via-blue-400 to-white relative overflow-hidden">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRjMC0yIDItNCAyLTRzMiAyIDIgNHYxMGMwIDIgMiA0IDIgNHMyLTIgMi00VjM0YzAtMi0yLTQtMi00cy0yIDItMiA0djEwYzAgMi0yIDQtMiA0cy0yLTItMi00VjM0eiIvPjwvZz48L2c+PC9zdmc+')] opacity-30"></div>
      
      <div className="relative z-10 min-h-screen flex items-center justify-center px-4 py-12">
        <Card className="w-full max-w-md shadow-2xl border-0 backdrop-blur-sm bg-white/95 animate-scale-in">
          <CardHeader className="text-center space-y-4 pb-8">
            <div className="mx-auto w-20 h-20 bg-gradient-to-br from-blue-600 to-blue-400 rounded-2xl flex items-center justify-center shadow-lg animate-fade-in">
              <Icon name="Gamepad2" size={40} className="text-white" />
            </div>
            <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
              SAMP Сервер
            </CardTitle>
            <CardDescription className="text-lg text-gray-600">
              Введите данные для доната
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2 animate-fade-in" style={{ animationDelay: '0.1s' }}>
                <Label htmlFor="nickname" className="text-base font-medium text-gray-700">
                  Никнейм
                </Label>
                <div className="relative">
                  <Icon 
                    name="User" 
                    size={20} 
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-blue-500" 
                  />
                  <Input
                    id="nickname"
                    type="text"
                    placeholder="Введите ваш игровой ник"
                    value={nickname}
                    onChange={(e) => setNickname(e.target.value)}
                    className="pl-10 h-12 border-2 border-gray-200 focus:border-blue-500 transition-colors"
                  />
                </div>
              </div>

              <div className="space-y-2 animate-fade-in" style={{ animationDelay: '0.2s' }}>
                <Label htmlFor="donate" className="text-base font-medium text-gray-700">
                  Сумма доната (рублей)
                </Label>
                <div className="relative">
                  <Icon 
                    name="Wallet" 
                    size={20} 
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-blue-500" 
                  />
                  <Input
                    id="donate"
                    type="number"
                    placeholder="100"
                    value={donateAmount}
                    onChange={(e) => setDonateAmount(e.target.value)}
                    className="pl-10 h-12 border-2 border-gray-200 focus:border-blue-500 transition-colors"
                    min="1"
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full h-12 text-lg font-medium bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 shadow-lg hover:shadow-xl transition-all duration-300 animate-fade-in"
                style={{ animationDelay: '0.3s' }}
              >
                <Icon name="CreditCard" size={20} className="mr-2" />
                Отправить донат
              </Button>
            </form>

            <div className="mt-6 pt-6 border-t border-gray-200 animate-fade-in" style={{ animationDelay: '0.4s' }}>
              <div className="flex items-center justify-center gap-6 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <Icon name="Users" size={16} className="text-blue-500" />
                  <span>Онлайн: 245</span>
                </div>
                <div className="flex items-center gap-2">
                  <Icon name="Server" size={16} className="text-blue-500" />
                  <span>Слоты: 500</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white/80 text-sm font-medium animate-fade-in">
        © 2024 SAMP Server. Все права защищены
      </div>
    </div>
  );
}
