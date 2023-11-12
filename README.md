# sg_test_task1

Цей проект генерує випадкові замовлення і проводить моніторинг замовлень.

## Як запустити проект
1. Встановити необхідні модулі:
```
pip install requirements.txt
```
або
```
pip3 install requirements.txt
```
2. Помістити отриманий від автора файл з ключем <sub>key.key</sub> в цю папку з проектом. Якщо у вас немає файлу з ключем, напишіть сюди: oleksii.yakymchuk@gmail.com.
3. Запустити файл <sub> crypto.py </sub>. Він розшифрує файли <sub>config.py</sub> і <sub>google_sa_credentials.json</sub>.
```
python crypto.py
```
```
python3 crypto.py
```
4. Запустити файл <sub> main.py </sub> однією з команд
```
python main.py
```
або
```
python3 main.py
```
і слідувати інструкціям, що будуть виводитись в терміналі.

## Щось схоже на опис роботи

### Як відбувається генерація замовлень (create_and_fill_db.py):
1. За замовчуванням генерується 100 замовлень (їхню кількість можна змінити в <sub>config.py</sub>).
2. Ми вважаємо, що у нас є 10 торговців з id від 1 до 10.
3. Для кожного замовлення генерується час замовлення в проміжку від \[сьогодні - 30 днів\] до сьогодні.
4. Для кожного замовлення генерується транзакція автентифікації.
5. 1. Час транзації автентифікації - протягом 2 годин з часу замовлення.
   2. З імовірністю 95% ця транзакція буде успішна, а з імовірністю 5% - неуспішна.
6. Якщо транзакція автентицікації неуспішна - кінець генерації замовлення.
7. Якщо транзакція автентифікації успішна, тоді з імовірністю 90% буде проведено другу транзакцію для цього замовлення протягом 7 днів, а з імовірністю 10% такої транзакції не буде:
8. 1. Генерується друга транзакція для цього замовлення.
   2. 1. З імовірністю 95% це буде транзакція списання коштів, а з імовірністю 5% - відміна замовлення.
      2. З імовірністю 90% друга транзакція буде успішна, а з імовірністю 10% вона буде не успішна.

### Як відбувається моніторинг (monitoring.py):
1. Виконується запит в базу для пошуку ордерів, для яких не було другої успішної транзакції після успішної транзакції автентифікації протягом 7 днів. Дані групуються по торговцях.
2. В телеграм канал відправляється повідомлення з кількістю незавершених замовленнями для кожного торговця.
3. Оновлюється гугл-таблиця з незавершеними замовленнями.

Якщо у вас немає доступу до телеграм каналу і гугл-таблиці, напишіть сюди: oleksii.yakymchuk@gmail.com.