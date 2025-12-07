import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

export default function Index() {
  const [nickname, setNickname] = useState('');
  const [donateAmount, setDonateAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [cardNumber, setCardNumber] = useState('');
  const [paymentId, setPaymentId] = useState('');
  const [isConfirming, setIsConfirming] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
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

    setIsLoading(true);

    try {
      const response = await fetch('https://functions.poehali.dev/9f161d17-3a34-4f4a-ac1d-33ab143b8e21', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nickname: nickname,
          amount: Number(donateAmount),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        toast({
          title: "Ошибка",
          description: data.error || "Не удалось создать платеж",
          variant: "destructive",
        });
        setIsLoading(false);
        return;
      }

      setCardNumber(data.card_number);
      setPaymentId(data.payment_id);
      setShowPaymentModal(true);
      setIsLoading(false);
      
      toast({
        title: "Успешно!",
        description: "Реквизиты карты получены",
      });
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Проблема с соединением. Попробуйте позже.",
        variant: "destructive",
      });
      setIsLoading(false);
    }
  };

  const handleConfirmPayment = async () => {
    setIsConfirming(true);
    
    try {
      const response = await fetch('https://functions.poehali.dev/9f161d17-3a34-4f4a-ac1d-33ab143b8e21', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'confirm',
          nickname: nickname,
          amount: Number(donateAmount),
          payment_id: paymentId,
        }),
      });

      if (response.ok) {
        toast({
          title: "Отлично!",
          description: "Уведомление отправлено администратору",
        });
        
        setShowPaymentModal(false);
        setNickname('');
        setDonateAmount('');
        setPaymentId('');
      } else {
        toast({
          title: "Ошибка",
          description: "Не удалось отправить подтверждение",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Проблема с соединением",
        variant: "destructive",
      });
    } finally {
      setIsConfirming(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(cardNumber);
    toast({
      title: "Скопировано!",
      description: "Номер карты скопирован в буфер обмена",
    });
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
                disabled={isLoading}
                className="w-full h-12 text-lg font-medium bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 shadow-lg hover:shadow-xl transition-all duration-300 animate-fade-in disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ animationDelay: '0.3s' }}
              >
                {isLoading ? (
                  <>
                    <Icon name="Loader2" size={20} className="mr-2 animate-spin" />
                    Загрузка...
                  </>
                ) : (
                  <>
                    <Icon name="CreditCard" size={20} className="mr-2" />
                    Получить реквизиты
                  </>
                )}
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

      <Dialog open={showPaymentModal} onOpenChange={setShowPaymentModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-center">
              Реквизиты для оплаты
            </DialogTitle>
            <DialogDescription className="text-center">
              Переведите {donateAmount} ₽ на указанную карту
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6 py-4">
            <div className="bg-gradient-to-r from-blue-600 to-blue-500 rounded-lg p-6 text-white space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm opacity-80">Номер карты</span>
                <Icon name="CreditCard" size={24} />
              </div>
              <div className="font-mono text-2xl font-bold tracking-wider">
                {cardNumber}
              </div>
              <Button
                onClick={copyToClipboard}
                variant="secondary"
                className="w-full bg-white/20 hover:bg-white/30 text-white border-0"
              >
                <Icon name="Copy" size={16} className="mr-2" />
                Скопировать номер
              </Button>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Icon name="Info" size={20} className="text-blue-600 mt-0.5" />
                <div className="text-sm text-gray-700">
                  <p className="font-medium mb-1">Важно:</p>
                  <p>После перевода нажмите кнопку "Я оплатил" ниже, чтобы администратор проверил платеж</p>
                </div>
              </div>
            </div>

            <Button
              onClick={handleConfirmPayment}
              disabled={isConfirming}
              className="w-full h-12 bg-green-600 hover:bg-green-700 text-white"
            >
              {isConfirming ? (
                <>
                  <Icon name="Loader2" size={20} className="mr-2 animate-spin" />
                  Отправка...
                </>
              ) : (
                <>
                  <Icon name="Check" size={20} className="mr-2" />
                  Я оплатил
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white/80 text-sm font-medium animate-fade-in">
        © 2024 SAMP Server. Все права защищены
      </div>
    </div>
  );
}
