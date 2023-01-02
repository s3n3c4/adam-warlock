class Person:

    def __init__(self, name, age, gender):
        self.__name = name
        self.__age = age
        self.__gender = gender

    @property
    def Name(self):
        return self.__name

    @Name.setter
    def Name(self, value):
        self.__name = value

    @staticmethod
    def mymethod():
        print("Hello World")

Person.mymethod()

p1 = Person("Allan", 31, 'm')
print(p1.Name)

p1.mymethod()

p1.Name = "Bob"
print(p1.Name)