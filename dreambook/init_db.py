import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, Dream, Symbol, DreamSymbol, Statistic, EmotionStat, SymbolStat, GenerationRequest, GeneratedImage, UserImage

app = create_app()


def init_database():
    with app.app_context():
        print("Удаление существующих таблиц...")
        db.drop_all()
        
        print("Создание таблиц...")
        db.create_all()
        
        # Создаём папки для загрузки файлов
        print("\nСоздание папок для загрузки...")
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)
        os.makedirs(app.config['DREAM_IMAGES_FOLDER'], exist_ok=True)
        print("Папки созданы!")
        
        #СОЗДАНИЕ СИМВОЛОВ
        print("\nСоздание символов...")
        symbols_data = [
            "вода", "огонь", "воздух", "земля", "ветер", "гроза", "молния", "дождь", "снег", "туман",
            "полёт", "падение", "погоня", "опоздание", "потеря", "нахождение", "бег", "прыжок",
            "змея", "кошка", "собака", "волк", "медведь", "птица", "рыба", "конь", "лиса", "заяц",
            "дом", "лес", "море", "гора", "город", "пустыня", "замок", "пещера", "сарай", "кладбище",
            "страх", "радость", "грусть", "гнев", "спокойствие", "любовь", "ненависть", "зависть", "надежда", "отчаяние",
            "ключ", "дверь", "зеркало", "лестница", "мост", "книга", "письмо", "меч", "кольцо", "свеча",
            "свет", "тьма", "время", "смерть", "рождение", "путь", "выбор", "судьба", "тайна", "откровение"
        ]
        
        symbols = []
        for name in symbols_data:
            symbol = Symbol(name=name)
            db.session.add(symbol)
            symbols.append(symbol)
            print(f"  Создан символ: {name}")
        
        db.session.commit()
        print(f"Всего символов: {len(symbols_data)}")
        
        #СОЗДАНИЕ АДМИНИСТРАТОРА
        print("\nСоздание администратора...")
        admin = User(
            username='admin',
            email='admin@dreambook.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("  Администратор: admin / admin123")
        
        # СОЗДАНИЕ ТЕСТОВЫХ ПОЛЬЗОВАТЕЛЕЙ
        print("\nСоздание тестовых пользователей...")
        users_data = [
            {'username': 'anna', 'email': 'anna@example.com', 'password': 'anna123', 'role': 'user'},
            {'username': 'dmitry', 'email': 'dmitry@example.com', 'password': 'dmitry123', 'role': 'user'},
            {'username': 'elena', 'email': 'elena@example.com', 'password': 'elena123', 'role': 'user'},
        ]
        
        for user_data in users_data:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            print(f"  Создан пользователь: {user_data['username']} / {user_data['password']}")
        
        db.session.commit()
        
        # СОЗДАНИЕ ТЕСТОВЫХ СНОВ (для пользователя anna)
        print("\nСоздание тестовых снов...")
        anna = User.query.filter_by(username='anna').first()
        
        if anna:
            dreams_data = [
                {
                    'title': 'Полет над городом',
                    'content': 'Мне снилось, что я лечу над ночным городом. Огни внизу мерцали, ветер свистел в ушах. Я чувствовал невероятную свободу и радость.',
                    'dream_date': '2026-06-01',
                    'mood': 5
                },
                {
                    'title': 'Встреча с волком',
                    'content': 'Я шёл по тёмному лесу. Вдруг из-за деревьев вышел огромный чёрный волк. Он посмотрел на меня жёлтыми глазами, и я испытал сильный страх.',
                    'dream_date': '2026-06-03',
                    'mood': 2
                },
                {
                    'title': 'Потерянный ключ',
                    'content': 'Мне снился старый дом. Я искал ключ, но никак не мог его найти. Вокруг была темнота и тишина. Проснулся в тревоге.',
                    'dream_date': '2026-05-28',
                    'mood': 3
                },
                {
                    'title': 'Радуга после дождя',
                    'content': 'После сильного дождя появилась яркая радуга. Я стоял в поле и смотрел на неё. На душе было спокойно и тепло.',
                    'dream_date': '2026-05-20',
                    'mood': 5
                },
                {
                    'title': 'Опоздание на поезд',
                    'content': 'Я бежал по перрону, но поезд уехал без меня. Чувствовал отчаяние и беспомощность.',
                    'dream_date': '2026-05-15',
                    'mood': 1
                },
                {
                    'title': 'Зеркало в темноте',
                    'content': 'В тёмной комнате я увидел зеркало. Вместо своего отражения увидел незнакомца. Мне стало страшно.',
                    'dream_date': '2026-05-10',
                    'mood': 2
                },
                {
                    'title': 'Прогулка по морю',
                    'content': 'Я шёл по морскому дну, вокруг плавали рыбы и светились кораллы. Было очень красиво и спокойно.',
                    'dream_date': '2026-05-05',
                    'mood': 4
                }
            ]
            
            for dream_data in dreams_data:
                from datetime import datetime
                dream = Dream(
                    user_id=anna.user_id,
                    title=dream_data['title'],
                    content=dream_data['content'],
                    dream_date=datetime.strptime(dream_data['dream_date'], '%Y-%m-%d').date(),
                    mood=dream_data['mood']
                )
                db.session.add(dream)
                print(f"  Создан сон: {dream_data['title']} (Анна)")
            
            db.session.commit()
        
        print("\n" + "=" * 60)
        print("БАЗА ДАННЫХ УСПЕШНО ИНИЦИАЛИЗИРОВАНА!")
        print("=" * 60)
        
        print("\nСтатистика:")
        print(f"  • Пользователей: {User.query.count()}")
        print(f"  • Символов: {Symbol.query.count()}")
        print(f"  • Снов: {Dream.query.count()}")
        
        print("\nУчётные записи для входа:")
        print("-" * 50)
        print(f"{'Логин':<12} | {'Пароль':<12} | {'Роль':<12}")
        print("-" * 50)
        print(f"{'admin':<12} | {'admin123':<12} | {'Администратор':<12}")
        for user_data in users_data:
            print(f"{user_data['username']:<12} | {user_data['password']:<12} | {user_data['role']:<12}")
        print("-" * 50)


if __name__ == '__main__':
    init_database()