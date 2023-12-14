from faker import Faker
from faker.providers import BaseProvider
from pydantic import BaseModel

class Person(BaseModel):
    first_name: str
    last_name: str
    email: str
    gender: str
    address: str
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class User(Person):
    username: str
    password: str

class PersonProvider(BaseProvider):
    __provider__ = "person"
    
    def person(self):
        gender = self.random_element(["F", "M"])
        first_name = self.generator.first_name_male() if gender == "M" else self.generator.first_name_female()
        last_name = self.generator.last_name()
        email_address = f"{first_name}.{last_name}@{self.generator.domain_name()}".lower()
        
        return Person(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            email=email_address,
            address=self.generator.address(),
        )

class UserProvider(PersonProvider):
    __provider__ = "user"
    
    def user(self):
        person = self.person()
        return User(
            username=f"{person.first_name}_{person.last_name}".lower(),
            password=self.generator.password(), **person.model_dump()
        )

class RandomProvider(BaseProvider):
    __provider__ = "random_from"
    
    def random_from(self, *args):
        return self.random_element(args)

class CustomProvider(BaseProvider):
    __provider__ = "get"
    
    def _call(self, method, args, kwargs):
        if args:
            if kwargs:
                if isinstance(args, dict):
                    output = method(**args, **kwargs)
                elif isinstance(args, list):
                    output = method(*args, **kwargs)
                else:
                    output = method(args, **kwargs)
            else:
                if isinstance(args, dict):
                    output = method(**args)
                elif isinstance(args, list):
                    output = method(*args)
                else:
                    output = method(args)
        else:
            if kwargs:
                output = method(**kwargs)
            else:
                output = method()

        return output
    
    def get(self, method_name: str, args: any, commons: dict, **kwargs):
        if "." in method_name:
            method_name, attribute = method_name.split(".")
            if method_name not in commons:
                method = getattr(self.generator, method_name)
                commons[method_name] = self._call(method, args, kwargs)
            return getattr(commons[method_name], attribute), commons

        method = getattr(self.generator, method_name)
        return self._call(method, args, kwargs), commons

faker = Faker()
faker.add_provider(PersonProvider)
faker.add_provider(UserProvider)
faker.add_provider(RandomProvider)
faker.add_provider(CustomProvider)
