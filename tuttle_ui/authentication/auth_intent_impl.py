from authentication.abstractions import AuthIntent
from core.abstractions import LocalCache
from authentication.user_data_source_impl import UserDataSourceImpl
from authentication.abstractions import AuthIntentsResult

from authentication.auth_data_keys import USER_ID


class AuthIntentImpl(AuthIntent):
    def __init__(self, cache: LocalCache):
        super().__init__(cache=cache, dataSource=UserDataSourceImpl())

    def is_user_created(
        self,
    ) -> bool:
        userId = self.cache.get_value(USER_ID)
        if userId:
            return True
        return False

    def create_user(
        self,
        title: str,
        name: str,
        email: str,
        phone: str,
        street: str,
        streetNum: str,
        postalCode: str,
        city: str,
        country: str,
    ) -> AuthIntentsResult:
        result = self.dataSource.create_and_save_user(
            title=title,
            name=name,
            email=email,
            phone=phone,
            street=street,
            streetNum=streetNum,
            postalCode=postalCode,
            city=city,
            country=country,
        )
        if result.wasIntentSuccessful:
            self.cache_user_data(key=USER_ID, data=result.data)
        return result

    def cache_user_data(self, key: str, data: any):
        self.cache.set_value(key, data)
