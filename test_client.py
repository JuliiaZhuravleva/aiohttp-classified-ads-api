import asyncio
import aiohttp
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_URL = "http://web:8080"


async def wait_for_api(session, max_retries=5, delay=2):
    for i in range(max_retries):
        try:
            async with session.get(f"{API_URL}/health") as response:
                if response.status == 200:
                    logger.info("API is ready")
                    return True
        except aiohttp.ClientError:
            logger.info(f"API not ready, retrying in {delay} seconds...")
            await asyncio.sleep(delay)
    logger.error("Max retries reached, API is not available")
    return False


async def test_api():
    async with aiohttp.ClientSession() as session:
        if not await wait_for_api(session):
            return
        # Тест регистрации пользователя
        logger.info("Тест: Регистрация пользователя")
        async with session.post(f"{API_URL}/user", json={
            "name": "Иван Иванов",
            "email": "ivan@example.com",
            "password": "secretpassword"
        }) as response:
            if response.status == 201:
                user = await response.json()
                logger.info(f"Успешно: Пользователь зарегистрирован с id {user['id']}")
            else:
                logger.error(f"Ошибка: Не удалось зарегистрировать пользователя. Статус: {response.status}")
                return

        # Тест входа пользователя
        logger.info("Тест: Вход пользователя")
        async with session.post(f"{API_URL}/login", json={
            "email": "ivan@example.com",
            "password": "secretpassword"
        }) as response:
            if response.status == 200:
                login_data = await response.json()
                logger.info(f"Успешно: Пользователь вошел в систему. User ID: {login_data['user_id']}")
            else:
                logger.error(f"Ошибка: Не удалось войти в систему. Статус: {response.status}")
                return

        # Тест создания объявления
        logger.info("Тест: Создание объявления")
        async with session.post(f"{API_URL}/advert", json={
            "title": "Продам гараж",
            "description": "Отличный гараж в центре города",
            "owner_id": login_data['user_id']
        }, headers={"Authorization": f"ivan@example.com:secretpassword"}) as response:
            if response.status == 201:
                advert = await response.json()
                logger.info(f"Успешно: Объявление создано с id {advert['id']}")
            else:
                logger.error(f"Ошибка: Не удалось создать объявление. Статус: {response.status}")
                return

        # Тест получения объявления
        logger.info("Тест: Получение объявления")
        async with session.get(f"{API_URL}/advert/{advert['id']}",
                               headers={"Authorization": f"ivan@example.com:secretpassword"}) as response:
            if response.status == 200:
                retrieved_advert = await response.json()
                logger.info(f"Успешно: Получено объявление с id {retrieved_advert['id']}")
            else:
                logger.error(f"Ошибка: Не удалось получить объявление. Статус: {response.status}")

        # Тест обновления объявления
        logger.info("Тест: Обновление объявления")
        async with session.patch(f"{API_URL}/advert/{advert['id']}", json={
            "title": "Продам гараж (обновлено)",
            "description": "Отличный гараж в центре города, свежий ремонт"
        }, headers={"Authorization": f"ivan@example.com:secretpassword"}) as response:
            if response.status == 200:
                updated_advert = await response.json()
                logger.info(f"Успешно: Объявление обновлено. Новый заголовок: {updated_advert['title']}")
            else:
                logger.error(f"Ошибка: Не удалось обновить объявление. Статус: {response.status}")

        # Тест удаления объявления
        logger.info("Тест: Удаление объявления")
        async with session.delete(f"{API_URL}/advert/{advert['id']}",
                                  headers={"Authorization": f"ivan@example.com:secretpassword"}) as response:
            if response.status == 200:
                logger.info(f"Успешно: Объявление удалено")
            else:
                logger.error(f"Ошибка: Не удалось удалить объявление. Статус: {response.status}")

        # Тест удаления пользователя
        logger.info("Тест: Удаление пользователя")
        async with session.delete(f"{API_URL}/user/{login_data['user_id']}",
                                  headers={"Authorization": f"ivan@example.com:secretpassword"}) as response:
            if response.status == 200:
                logger.info(f"Успешно: Пользователь удален")
            else:
                logger.error(f"Ошибка: Не удалось удалить пользователя. Статус: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_api())